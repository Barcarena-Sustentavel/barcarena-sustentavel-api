from models import Base
from sqlalchemy import Column, Integer, String  
from sqlalchemy.orm import relationship

#conexao com o banco para fazer operações dql e ddl
class Indicador(Base):
    __tablename__ = "Indicadores" #tabela no banco
    __table_args__ = {"schema": "barcarena_sustentavel"} #schema

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=True)
    fkDimensao_id = relationship("Dimensao", back_populates="Indicadores")