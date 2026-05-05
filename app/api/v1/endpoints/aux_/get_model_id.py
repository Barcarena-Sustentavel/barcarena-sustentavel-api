from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.models import kml
#Função para retornar o id a partir de um modelo
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados
#model: modelo da dimensão, localizado em app/domain/models/
async def get_model_id(dimensao_nome: str, session: Session, model):
    model_id = None
    if model == kml.KML:
        model_id = session.scalar(select(model).where(
                model.name == dimensao_nome
    ))
    else:
        model_id = session.scalar(select(model).where(
                model.nome == dimensao_nome
    ))
    try:
        return model_id.id
    except AttributeError:
        return 0
