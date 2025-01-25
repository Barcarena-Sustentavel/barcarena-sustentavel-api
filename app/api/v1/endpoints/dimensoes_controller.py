from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import dimesao_schema, anexo_schema, contribuicao_schema ,indicador_schema, referencia_schema, kml_schema
from app.domain.models import dimensao , indicador, anexo, contribuicao,  indicador,  referencias,  kml
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any  

dimensoes = APIRouter()

@dimensoes.get("/dimensoes/{dimensaoNome}/")
async def get_dimensao(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    #print(get_model_id(dimensaoNome, session, dimensao.Dimensao))
    indicadores = session.scalars(select(indicador.Indicador).where(
        indicador.Indicador.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    refrencias = session.scalars(select(referencias.Referencias).where(
        referencias.Referencias.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))

    indicadoresDimensao = []
    referenciasIndicador = []
    indicadoresall = indicadores.all()
    refrenciasall = refrencias.all()


    for a in indicadoresall:
        indicadoresDimensao.append(indicador_schema.IndicadorSchema(id=a.id, fkDimensao_id=a.fkDimensao_id, nome=a.nome))
    for b in refrenciasall:
        referenciasIndicador.append(referencia_schema.ReferenciaSchema(id=b.id, nome=b.nome, fkDimensao_id=b.fkDimensao_id))
    
    return {"indicadores":indicadoresDimensao, "referencias":referenciasIndicador}

@dimensoes.get("/dimensoes/kml/{dimensaoNome}/")
async def get_kml(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    kmls = session.scalars(select(kml.KML).where(
          kml.KML.fkDimensao_id == get_model_id(dimensaoNome, session, dimensao.Dimensao)
         )
    )
    kmls_list = []

    for k in kmls.all():
        kmls_list.append(kml_schema.KMLSchema(id=k.id, name=k.name, fkDimensao_id=k.fkDimensao_id))
    
    return {"kmls":kmls_list}

@dimensoes.get("/dimensoes/kmlCoords/{kmlNome}/")
async def get_kml_coords(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    anexos = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkKML_id == get_model_id(kmlNome, session, kml.KML)
    ))
    anexoJson = anexo_schema.AnexoSchema(id=anexos.all()[0].id, fkIndicador_id=anexos.all()[0].fkIndicador_id, fkKML_id=anexos.all()[0].fkKML_id, path=anexos.all()[0].path)
    return {"cordenadas":anexoJson.path}


@dimensoes.get("/dimensoes/{dimensaoNome}/{indicadorNome}/")
async def get_indicador(dimensaoNome: str, indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    anexoIndicador = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == get_model_id(indicadorNome, session, indicador.Indicador)
    ))

    indicadorDimensaoJson = indicador_schema.IndicadorSchema(id=indicadorDimensao.id, nome=indicadorDimensao.nome, fkDimensao_id=indicadorDimensao.fkDimensao_id)
    anexoIndicadorJson = anexo_schema.AnexoSchema(id=anexoIndicador.id, fkIndicador_id=anexoIndicador.fkIndicador_id, fkKML_id=anexoIndicador.fkKML_id, path=anexoIndicador.path)

    return {"indicador":indicadorDimensaoJson, "anexo":anexoIndicadorJson}

@dimensoes.post("/contribuicao/")
async def post_contribuicao(contribuicao: contribuicao_schema.ContribuicaoSchema, status_code=HTTPStatus.CREATED):
    return contribuicao


#from fastapi import APIRouter
#
#dimensoes = APIRouter()
#
#@dimensoes.get("/dimensoes/{dimensaoNome}/")
#async def get_dimensao(dimensaoNome: str):
#
#    return f"Dimensão {dimensaoNome} encontrada!"
#
#@dimensoes.get("/dimensoes/kml/{dimensaoNome}/")
#async def get_kml(dimensaoNome: str):
#
#    return f"KML associado à Dimensão {dimensaoNome} encontrado!"
#
#@dimensoes.get("/dimensoes/kmlCoords/{kmlNome}/")
#async def get_kml_coords(kmlNome: str):
#
#    return f"KML com coordenadas para {kmlNome} encontrado!"
#
#@dimensoes.get("/dimensoes/{dimensao}/{indicador}/")
#async def get_indicador(dimensaoNome: str, indicadorNome: str):
#
#    return f"Indicador {indicadorNome} da Dimensão {dimensaoNome} encontrado!"


#Função para retornar o id a partir de um modelo
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados
#model: modelo da dimensão, localizado em app/domain/models/
async def get_model_id(dimensao_nome: str, session: Session, model):
    model_id = session.scalar(select(model).where(
        model.nome == dimensao_nome
    ))
    return model_id.id