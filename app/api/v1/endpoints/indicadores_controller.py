from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData, AnexoIndicadorSchema
from app.domain.schemas import anexo_schema,indicador_schema
from app.domain.models import dimensao , indicador, anexo,indicador
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from .aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus
from .anexo_controller import get_anexo_indicador
from minio import Minio

indicadorRouter = APIRouter()
@indicadorRouter.get("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def get_indicador(dimensaoNome: str, indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK): 
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == dimensao_id
    ))
    anexoIndicador = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == await get_model_id(indicadorNome, session, indicador.Indicador)
    ))

    indicadorDimensaoJson = indicador_schema.IndicadorSchema(id=indicadorDimensao.id, nome=indicadorDimensao.nome, fkDimensao=indicadorDimensao.fkDimensao_id)
    anexoIndicadorJson:list = []
    for anexos in anexoIndicador.all():
        anexoIndicadorJson.append(anexo_schema.AnexoSchema(id=anexos.id,
                                                fkDimensao=dimensao_id,
                                                fkIndicador=anexos.fkIndicador_id, 
                                                fkKml=anexos.fkKml_id,
                                                fkContribuicao=anexos.fkContribuicao_id,
                                                path=anexos.path,
                                                tipoGrafico=anexos.tipoGrafico,
                                                descricaoGrafico=anexos.descricaoGrafico))
    
         
        
        
        

    return {"indicador":indicadorDimensaoJson, "anexo":anexoIndicadorJson}

@indicadorRouter.post("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def create_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    dadosIndicador: indicador_schema.IndicadorSchema,
    dadosAnexo: anexo_schema.AnexoSchema,
    session: Session = Depends(get_db)):

    #print(dadosIndicador)
    new_indicador = indicador.Indicador(nome=dadosIndicador.nome, fkDimensao_id=await get_model_id(dimensaoNome, session, dimensao.Dimensao))    
    session.add(new_indicador)
    session.commit()
    session.refresh(new_indicador)
    
    new_anexo_indicador = anexo.Anexo(fkIndicador_id=await get_model_id(indicadorNome, session, indicador.Indicador), 
                                    fkKml_id=dadosAnexo.fkKml, 
                                    fkContribuicao_id=dadosAnexo.fkContribuicao,
                                    path=dadosAnexo.path,
                                    descricaoGrafico=dadosAnexo.descricaoGrafico,
                                    tipoGrafico=dadosAnexo.tipoGrafico,
                                    )
    session.add(new_anexo_indicador)
    session.commit()
    session.refresh(new_anexo_indicador)

    indicador_response = await get_indicador(dimensaoNome, indicadorNome, session)
    anexo_response = await get_anexo_indicador(dimensaoNome, indicadorNome, session)
    response = IndicadorData(indicadores=indicador_response["indicador"], arquivos=anexo_response)
    return response
   

@indicadorRouter.patch("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
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
            fkKml=anexoIndicador.fkKml_id,
            path=anexoIndicador.path
        )

        return {"indicador": indicadorDimensaoJson, "anexo": anexoIndicadorJson}

@indicadorRouter.delete("/dimensoes/{dimensaoNome}/{indicadorNome}/", status_code=HTTPStatus.NO_CONTENT)
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