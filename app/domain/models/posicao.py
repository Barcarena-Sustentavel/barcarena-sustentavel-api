from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Posicao(Base):
    __tablename__ = "Posicao"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    posicao = Column(Integer, nullable=False)
    fkIndicador_id = Column(Integer, ForeignKey("barcarena_sustentavel.Indicador.id"), nullable=True)
    fkAnexo_id = Column(Integer, ForeignKey("barcarena_sustentavel.Anexo.id"), nullable=True)

    indicador = relationship("Indicador", back_populates="posicao")
    anexos = relationship("Anexo", back_populates="posicao")
