from domain.models.base import Base
from sqlalchemy import Column, Integer, String  
from sqlalchemy.orm import relationship

#conexao com o banco para fazer operações dql e ddl
class Anexo(Base):
    __tablename__ = "Anexos" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=True)
    fkDimensao_id = relationship("Dimensao", back_populates="Anexos")
    fkKML_id = relationship("KML", back_populates="Anexos")
    fkIndicador_id = relationship("Indicadores", back_populates="Anexos")
    fkContribuicao_id = relationship("Contribuicao", back_populates="Anexos")