from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import contribuicao_schema
from app.domain.models import contribuicao, dimensao
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from http import HTTPStatus
from aux.get_model_id import get_model_id

contribuicoes = APIRouter()

@contribuicoes.post("/contribuicao/")
async def post_contribuicao(contribuicao: contribuicao_schema.ContribuicaoSchema, status_code=HTTPStatus.CREATED):
    return contribuicao

@contribuicoes.get("/contribuicao/{dimensaoNome}/")
async def get_contribuicao(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    contribuicao_list = []
    for c in contribuicaoSession.all():
        contribuicao_list.append(contribuicao_schema.ContribuicaoSchema(id=c.id,
                                                                        nome= c.nome if c.nome != None else None, 
                                                                        fkDimensao= c.fkDimensao_id if c.fkDimensao_id != None else None,
                                                                        email = c.email if c.email != None else None,
                                                                        comentario = c.comentario))
    return {"contribuicoes": contribuicao_list}

@contribuicoes.delete("/contribuicao/{contribuicaoId}/")
async def delete_contribuicao(contribuicaoId: int, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.id == contribuicaoId
    ))
    session.delete(contribuicaoSession)
    session.commit()