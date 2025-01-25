from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.domain.models.base import Base
#conexao com o banco para fazer operações dql e ddl
class Dimensao(Base):
    __tablename__ = "Dimensao" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=True)
    descricao = Column(String, nullable=True)

    indicadores = relationship("Indicador", back_populates="dimensao")
    kmls = relationship("KML", back_populates="dimensao")
    referencias = relationship("Referencias", back_populates="dimensao")
    contribuicoes = relationship("Contribuicao", back_populates="dimensao")
    anexos = relationship("Anexo", back_populates="dimensao")
