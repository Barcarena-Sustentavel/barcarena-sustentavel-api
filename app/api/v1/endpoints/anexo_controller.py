from app.domain.schemas import anexo_schema
from app.domain.models import anexo, indicador, dimensao
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from .aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus

anexoRouter = APIRouter()  
@anexoRouter.get("/dimensoes/anexos/{dimensaoNome}/{indicadorNome}/", response_model=anexo_schema.AnexoSchema)
async def get_anexo_indicador(indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    dimensao_id = await get_model_id(indicadorNome, session, dimensao.Dimensao)
    indicador_id = await get_model_id(indicadorNome, session, indicador.Indicador)
    anexoIndicador = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == indicador_id
    ))

    anexo_response = anexo_schema.AnexoSchema(id = anexoIndicador.id,
                                            path = anexoIndicador.path,
                                            fkDimensao=dim)
    return anexo_response