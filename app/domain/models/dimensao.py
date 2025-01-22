from sqlalchemy import Column, Integer, String
from app.domain.models.base import Base
#conexao com o banco para fazer operações dql e ddl
class Dimensao(Base):
    __tablename__ = "Dimensao" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=True)
    descricao = Column(String, nullable=True)