from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Indicador(Base):
    __tablename__ = "Indicador"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    fkDimensao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Dimensao.id"), nullable=False)

    dimensao = relationship("Dimensao", back_populates="indicadores")
    anexos = relationship("Anexo", back_populates="indicador")
