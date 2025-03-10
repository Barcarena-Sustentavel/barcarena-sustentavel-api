from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import contribuicao_schema
from app.domain.models import contribuicao, dimensao
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from http import HTTPStatus
from .aux.get_model_id import get_model_id
from typing import List

contribuicaoRouter = APIRouter()

@contribuicaoRouter.post("/dimensoes/contribuicao/{dimensaoNome}/", response_model=contribuicao_schema.ContribuicaoSchema)
async def post_contribuicao(dimensaoNome:str,contribuicaoNova: contribuicao_schema.ContribuicaoSchema, session: Session = Depends(get_db) ,status_code=HTTPStatus.CREATED):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    contribuicao_post = contribuicao.Contribuicao(nome=contribuicaoNova.nome, 
                                                comentario = contribuicaoNova.comentario,
                                                email=contribuicaoNova.email,
                                                telefone=contribuicaoNova.telefone,
                                                fkDimensao_id=dimensao_id,
                                                path = contribuicaoNova.path)
    session.add(contribuicao_post)
    session.commit()
    session.refresh(contribuicao_post)

    response_contribuicao = contribuicao_schema.ContribuicaoSchema(nome=contribuicao_post.nome,comentario=contribuicao_post.comentario,email=contribuicao_post.email,telefone=contribuicao_post.telefone)

    return response_contribuicao    

@contribuicaoRouter.get("/admin/dimensoes/{dimensaoNome}/contribuicao/", response_model=List[contribuicao_schema.ContribuicaoSchema])
async def admin_get_contribuicao(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK,):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    contribuicao_list = []
    for c in contribuicaoSession.all():
        contribuicao_list.append(contribuicao_schema.ContribuicaoSchema(id=c.id,
                                                                        nome= c.nome ,
                                                                        email = c.email,
                                                                        comentario = c.comentario,
                                                                        path = c.path))
    return contribuicao_list

@contribuicaoRouter.delete("/admin/dimensoes/{dimensaoNome}/contribuicao/{comentarioPublicao}/")
async def delete_contribuicao(dimensaoNome:str, comentarioPublicacao: str,session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.comentario == comentarioPublicacao
    ))
    session.delete(contribuicaoSession)
    session.commit()

    return