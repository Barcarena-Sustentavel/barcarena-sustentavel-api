from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema 
from app.domain.models import dimensao , indicador, indicador,  referencias, kml, contribuicao
from app.domain.schemas.response_schemas.get_dimensao_response import DimensaoData
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any  
from .aux.get_model_id import get_model_id

referenciasRouter = APIRouter()

@referenciasRouter.post("/admin/dimensoes/{dimensaoNome}/referencias/", response_model=referencia_schema,status_code=HTTPStatus.CREATED)
async def post_admin_referencia(dimensaoNome: str, referenciaNome: str, referenciaNova: referencia_schema.ReferenciaSchema, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    new_referencia = referencias.Referencias(nome=referenciaNova.nome, link=referenciaNova.link, fkDimensao_id=dimensao_id)
    session.add(new_referencia)
    session.commit()
    session.refresh(new_referencia)

    referencia_response = referencia_schema.ReferenciaSchema(nome=new_referencia.nome, link=new_referencia.link)

    return referencia_response

@referenciasRouter.patch("/admin/dimensoes/{dimensaoNome}/referencias/{referenciaNome}", response_model=referencia_schema.ReferenciaSchema,status_code=HTTPStatus.OK)
async def patch_admin_referencia(dimensaoNome: str, referenciaNome: str, referenciaNova: referencia_schema.ReferenciaSchema, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencia_data = session.scalar(select(referencias.Referencias).where(
        referencias.Referencias.nome == referenciaNome
    ))

    if not referencia_data:
        raise HTTPException(status_code=404, detail="Referencia não encontrada")

    referencia_data.nome = referenciaNova.nome if referenciaNova.nome != referencia_data.nome else referencia_data.nome
    referencia_data.link = referenciaNova.link if referenciaNova.link != referencia_data.link else referencia_data.link
    
    session.add(referencia_data)
    session.commit()
    session.refresh(referencia_data)

    referencia_response = referencia_schema.ReferenciaSchema(nome=referencia_data.nome, link=referencia_data.link)

    return referencia_response

@referenciasRouter.delete("/admin/dimensoes/{dimensaoNome}/referencias/{referenciaNome}", status_code=HTTPStatus.NO_CONTENT)
async def delete_admin_referencias(dimensaoNome: str, referenciaNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> None:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencia_data = session.scalar(select(referencias.Referencias).where(
        referencias.Referencias.nome == referenciaNome
    ))
    session.delete(referencia_data)
    session.commit()

    return


    
    