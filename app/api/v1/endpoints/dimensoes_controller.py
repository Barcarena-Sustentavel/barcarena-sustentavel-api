from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import dimesao_schema, anexo_schema, contribuicao_schema ,indicador_schema, referencia_schema, kml_schema
from app.domain.models import dimensao , indicador, anexo, contribuicao,  indicador,  referencias,  kml
from app.domain.schemas.response_schemas.get_dimensao_response import DimensaoData
from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData
from http import HTTPStatus
from typing import List, Dict, TypedDict
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any  

dimensoes = APIRouter()

#Retorna todos os indicadores de uma dimensão
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados
@dimensoes.get("/dimensoes/{dimensaoNome}/", response_model=DimensaoData)
async def get_dimensao(dimensaoNome: dimesao_schema.DimensaoParameters, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_data = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
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

    try:
        dimensao_data_json = dimesao_schema.DimensaoSchema(id=dimensao_data.id, nome=dimensao_data.nome, descricao=dimensao_data.descricao)
    except AttributeError:
        dimensao_data_json = dimesao_schema.DimensaoSchema(id=0, nome="Nome Dimensão", descricao="Descrição Dimensão")
    #print(dimensao_data_json)
    for a in indicadoresall:
        indicadoresDimensao.append(indicador_schema.IndicadorSchema(id=a.id, fkDimensao=a.fkDimensao_id, nome=a.nome))
    for b in refrenciasall:
        referenciasIndicador.append(referencia_schema.ReferenciaSchema(id=b.id, nome=b.nome, fkDimensao=b.fkDimensao_id, link=b.link))
    
    return {"dimensao":dimensao_data_json, "indicadores":indicadoresDimensao, "referencias":referenciasIndicador}

@dimensoes.get("/dimensoes/kml/{dimensaoNome}/",status_code=HTTPStatus.OK)
async def get_kml(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    #kmls = session.scalars(select(kml.KML).where(
    #      kml.KML.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    #     )
    #)
    #kmls_list = []
#
    #for k in kmls.all():
    #    kmls_list.append(kml_schema.KMLSchema(id=k.id, nome=k.name, fkDimensao=k.fkDimensao_id))
    kmls_list = [
    kml_schema.KMLSchema(id=1, nome="Mapa de Vulnerabilidade Social", fkDimensao=1),
    kml_schema.KMLSchema(id=2, nome="Mapa de Áreas Verdes", fkDimensao=2),
    kml_schema.KMLSchema(id=3, nome="Mapa de Desenvolvimento Local", fkDimensao=1),
    kml_schema.KMLSchema(id=4, nome="Mapa de Recursos Hídricos", fkDimensao=3),
    kml_schema.KMLSchema(id=5, nome="Mapa de Infraestrutura", fkDimensao=2)
]
    return {"kmls":kmls_list}

@dimensoes.get("/dimensoes/kmlCoords/{kmlNome}/")
async def get_kml_coords(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    #anexos = session.scalars(select(anexo.Anexo).where(
    #    anexo.Anexo.fkKML_id == await get_model_id(kmlNome, session, kml.KML)
    #))
    path_generico = "" 
    if kmlNome ==  "Mapa de Áreas Verdes":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/150130305000001P.kml"
    
    if kmlNome == "Mapa de Desenvolvimento Local":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/3G_VIVO_pa_intersect_clean.kml"
    
    if kmlNome == "Mapa de Infraestrutura":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/3G_TIM_pa_intersect_clean.kml"    
    
    anexo = open(path_generico, "r")
    
    
    return {"coordenadas":anexo.read()}


@dimensoes.get("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
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

@dimensoes.patch("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
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


@dimensoes.post("/contribuicao/")
async def post_contribuicao(contribuicao: contribuicao_schema.ContribuicaoSchema, status_code=HTTPStatus.CREATED):
    return contribuicao




#Função para retornar o id a partir de um modelo
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados
#model: modelo da dimensão, localizado em app/domain/models/
async def get_model_id(dimensao_nome: str, session: Session, model):
    model_id = session.scalar(select(model).where(
            model.nome == dimensao_nome
    ))
    try:
        return model_id.id
    except AttributeError:
        return 0