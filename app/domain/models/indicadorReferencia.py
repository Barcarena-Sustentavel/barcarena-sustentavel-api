from app.domain.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class IndicadorReferencia(Base): 
    __tablename__ = "IndicadorReferencia"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    fkIndicador_id = Column(Integer, ForeignKey("barcarena_sustentavel.Indicador.id"), nullable=False)
    fkReferencia_id = Column(Integer, ForeignKey("barcarena_sustentavel.Referencias.id"), nullable=False)

    indicador = relationship("Indicador", back_populates="referencias_associadas")
    referencia = relationship("Referencias", back_populates="indicadores_associados")