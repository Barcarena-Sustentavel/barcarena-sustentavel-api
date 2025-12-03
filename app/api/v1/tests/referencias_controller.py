from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import referencia_schema 
from app.domain.models import dimensao, referencias
from app.domain.schemas.response_schemas.get_dimensao_response import DimensaoData
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any, List
from .aux.get_model_id import get_model_id

referenciasRouter = APIRouter()

@referenciasRouter.get("/admin/dimensoes/{dimensaoNome}/referencias/",response_model=List[str],status_code=HTTPStatus.OK)
async def get_admin_referencias(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> List[str]:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencias_bd = session.scalars(select(referencias.Referencias).where(referencias.Referencias.fkDimensao_id == dimensao_id))
    referencias_list = []
    for r in referencias_bd.all():
        referencias_list.append(r.nome)
        
    return {"referencias":referencias_list}

@referenciasRouter.post("/admin/dimensoes/{dimensaoNome}/referencias/", response_model=referencia_schema.ReferenciaSchema,status_code=HTTPStatus.CREATED)
async def post_admin_referencia(dimensaoNome: str, referenciaNova: referencia_schema.ReferenciaSchema, session: Session = Depends(get_db),status_code=HTTPStatus.CREATED) -> Any:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    new_referencia = referencias.Referencias(nome=referenciaNova.nome, link=referenciaNova.link, fkDimensao_id=dimensao_id)
    session.add(new_referencia)
    session.commit()
    session.refresh(new_referencia)

    referencia_response = referencia_schema.ReferenciaSchema(nome=new_referencia.nome, link=new_referencia.link)

    return referencia_response

@referenciasRouter.get("/admin/dimensoes/{dimensaoNome}/referencias/{referenciaNome}/", response_model=referencia_schema.ReferenciaSchema, status_code=HTTPStatus.OK)
async def get_admin_referencia_detail(dimensaoNome: str, referenciaNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK) -> Any:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencia_data = session.scalar(select(referencias.Referencias).where(
        referencias.Referencias.nome == referenciaNome,
        referencias.Referencias.fkDimensao_id == dimensao_id
    ))
    
    if not referencia_data:
        raise HTTPException(status_code=404, detail="Referência não encontrada")
    
    referencia_response = referencia_schema.ReferenciaSchema(nome=referencia_data.nome, link=referencia_data.link)
    
    return referencia_response


@referenciasRouter.patch("/admin/dimensoes/{dimensaoNome}/referencias/{referenciaNome}/", response_model=referencia_schema.ReferenciaSchema,status_code=HTTPStatus.OK)
async def patch_admin_referencia(dimensaoNome: str, referenciaNome: str, referenciaModificado: referencia_schema.ReferenciaSchema, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencia_data = session.scalar(select(referencias.Referencias).where(
        referencias.Referencias.nome == referenciaNome
    ))

    if not referencia_data:
        raise HTTPException(status_code=404, detail="Referencia não encontrada")

    referencia_data.nome = referenciaModificado.nome if referenciaModificado.nome != referencia_data.nome else referencia_data.nome
    referencia_data.link = referenciaModificado.link if referenciaModificado.link != referencia_data.link else referencia_data.link
    
    session.add(referencia_data)
    session.commit()
    session.refresh(referencia_data)

    referencia_response = referencia_schema.ReferenciaSchema(nome=referencia_data.nome, link=referencia_data.link)

    return referencia_response

@referenciasRouter.delete("/admin/dimensoes/{dimensaoNome}/referencias/{referenciaNome}/", status_code=HTTPStatus.NO_CONTENT)
async def delete_admin_referencias(dimensaoNome: str, referenciaNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> None:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencia_data = session.scalar(select(referencias.Referencias).where(
        referencias.Referencias.nome == referenciaNome
    ))
    session.delete(referencia_data)
    session.commit()

    return


    
    