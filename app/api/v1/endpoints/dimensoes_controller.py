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

dimensaoRouter = APIRouter()

#Retorna todos os indicadores de uma dimensão
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados
@dimensaoRouter.get("/dimensoes/{dimensaoNome}/", response_model=DimensaoData)
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

@dimensaoRouter .patch("/dimensoes/{dimensaoNome}/", response_model=DimensaoData)
async def update_dimensao(dimensaoNome: str, update_dimensao:dimesao_schema.DimensaoSchema,session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_data = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    
    if not dimensao_data:
        raise HTTPException(status_code=404, detail="Dimensão não encontrada")
    
    # Update fields
    for field, value in update_dimensao.model_dump(exclude_unset=True).items():
        setattr(dimensao_data, field, value)
    
    session.commit()
    
    # Return updated data in same format as GET
    return await get_dimensao(dimensaoNome=dimensaoNome, session=session)

#Retorna todos os nomes dos kmls e contribuições de uma dimensão
#Criado somente para ser utilizado na parte de administrador
@dimensaoRouter .get("/dimensoesAdmin/{dimensaoNome}/")
async def get_dimensao_admin(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    get_dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    
    kml_dimensao = session.scalars(select(kml.KML).where(
        kml.KML.fkDimensao_id == get_dimensao_id
    ))
    
    contribuicao_dimensao = session.scalars(select(dimensao.Dimensao).where(
       contribuicao.Contribuicao.fkDimensao_id == get_dimensao_id
    ))
    
    kml_nomes = []
    contribuicao_nomes = []
    
    for a in kml_dimensao:
        kml_nomes.append(a.name)
        
    for b in contribuicao_dimensao:
        contribuicao_nomes.append(b.nome)
        
    return {"kmls":kml_nomes, "contribuicoes":contribuicao_nomes}
        
    
    
    
