from models import Base
from sqlalchemy import Column, Integer, String, DateTime

#conexao com o banco para fazer operações dql e ddl
class DimensaoContribuicao(Base):
    __tablename__ = "Admin" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=True)
    sobrenome = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)