from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData
from app.domain.schemas import dimesao_schema, anexo_schema,indicador_schema
from app.domain.models import dimensao , indicador, anexo,indicador
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus

indicadores = APIRouter()

@indicadores.get("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def get_indicador(dimensaoNome: dimesao_schema.DimensaoParameters, indicadorNome: indicador_schema.IndicadorParameters, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    anexoIndicador = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == await get_model_id(indicadorNome, session, indicador.Indicador)
    ))

    indicadorDimensaoJson = indicador_schema.IndicadorSchema(id=indicadorDimensao.id, nome=indicadorDimensao.nome, fkDimensao=indicadorDimensao.fkDimensao_id)
    anexoIndicadorJson = anexo_schema.AnexoSchema(id=anexoIndicador.id, fkIndicador=anexoIndicador.fkIndicador_id, fkKml=anexoIndicador.fkKML_id, path=anexoIndicador.path)

    return {"indicador":indicadorDimensaoJson, "anexo":anexoIndicadorJson}

@indicadores.post("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def create_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    indicador_insert_data: indicador_schema.IndicadorSchema,
    anexo_insert_data: anexo_schema.AnexoSchema,
    session: Session = Depends(get_db)):
    
    new_indicador = indicador.Indicador(nome=indicador_insert_data.nome, fkDimensao_id=await get_model_id(dimensaoNome, session, dimensao.Dimensao))    
    await session.add(new_indicador)
    await session.commit()
    await session.refresh(new_indicador)
    
    new_anexo_indicador = anexo.Anexo(fkIndicador_id=await get_model_id(indicadorNome, session, indicador.Indicador), fkKML_id=None, path=anexo_insert_data.path)
    await session.add(new_anexo_indicador)
    await session.commit()
    await session.refresh(new_anexo_indicador)
    
    return await get_indicador(dimensaoNome, indicadorNome, session)

@indicadores.patch("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def update_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    indicador_update_data: indicador_schema.IndicadorSchema,#
    anexo_update_data: anexo_schema.AnexoSchema,
    session: Session = Depends(get_db)):
        #Acha o indicador existente baseado no nome e no id da dimensão
        indicadorDimensao = session.scalar(select(indicador.Indicador).where(
            indicador.Indicador.nome == indicadorNome,
            indicador.Indicador.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
        ))
        
        #Se indicador não achado, retorna erro
        if not indicadorDimensao:
            raise HTTPException(status_code=404, detail="Indicator not found")

        #itera sobre os atributos do atributo do indicador e atualiza o seu valor para o 
        #que foi achado no banco de dados
        for field, value in indicador_update_data.model_dump(exclude_unset=True).items():
            setattr(indicadorDimensao, field, value)

        
        anexoIndicador = session.scalar(select(anexo.Anexo).where(
            anexo.Anexo.fkIndicador_id == indicadorDimensao.id
        ))

        if anexoIndicador != None:
            for field, value in anexo_update_data.model_dump(exclude_unset=True).items():
                setattr(anexoIndicador, field, value)

        session.commit()

        # Prepare response
        indicadorDimensaoJson = indicador_schema.IndicadorSchema(
            id=indicadorDimensao.id,
            nome=indicadorDimensao.nome,
            fkDimensao=indicadorDimensao.fkDimensao_id
        )
        
        anexoIndicadorJson = anexo_schema.AnexoSchema(
            id=anexoIndicador.id,
            fkIndicador=anexoIndicador.fkIndicador_id,
            fkKml=anexoIndicador.fkKML_id,
            path=anexoIndicador.path
        )

        return {"indicador": indicadorDimensaoJson, "anexo": anexoIndicadorJson}

@indicadores.delete("/dimensoes/{dimensaoNome}/{indicadorNome}/", status_code=HTTPStatus.NO_CONTENT)
async def delete_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    session: Session = Depends(get_db)
) -> None:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    
    db_indicador = session.scalar(
        select(indicador.Indicador).where(
            indicador.Indicador.nome == indicadorNome,
            indicador.Indicador.fkDimensao_id == dimensao_id
        )
    )
    
    if not db_indicador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Indicador não encontrado"
        )
    
    session.delete(db_indicador)
    session.commit()