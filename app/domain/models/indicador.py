from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base
from app.domain.models.indicadorReferencia import IndicadorReferencia

class Indicador(Base):
    __tablename__ = "Indicador"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    fkDimensao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Dimensao.id"), nullable=False)
    periodicidade = Column(String, nullable=False)
    ultimaAtualizacao = Column(String, nullable=False)
    unidadeMedida = Column(String, nullable=False)
    metodologia = Column(String, nullable=False)

    dimensao = relationship("Dimensao", back_populates="indicadores")
    anexos = relationship("Anexo", back_populates="indicador")
    posicao = relationship("Posicao", back_populates="indicador")
    #referencia = relationship("Referencias", back_populates="indicador", uselist=False)
    referencias_associadas = relationship(IndicadorReferencia, back_populates="indicador")
