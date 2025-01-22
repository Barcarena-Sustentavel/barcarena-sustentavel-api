from domain.models.base import Base
from sqlalchemy import Column, Integer, String  
from sqlalchemy.orm import relationship

#conexao com o banco para fazer operações dql e ddl
class DimensaoContribuicao(Base):
    __tablename__ = "Contribuicao" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    comentario = Column(String, nullable=False)
    fkDimensao_id = relationship("Dimensao", back_populates="Contribuicao")