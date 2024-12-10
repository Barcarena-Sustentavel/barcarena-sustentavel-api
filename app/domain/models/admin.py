from models import Base
from sqlalchemy import Column, Integer, String, DateTime

#conexao com o banco para fazer operações dql e ddl
class DimensaoContribuicao(Base):
    __tablename__ = "Admin" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)