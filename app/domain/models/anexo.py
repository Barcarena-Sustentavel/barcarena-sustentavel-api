from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Anexo(Base):
    __tablename__ = "Anexo"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    tipoGrafico = Column(String, nullable=True)
    descricaoGrafico = Column(String, nullable=True)
    fkDimensao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Dimensao.id"), nullable=False)
    fkKML_id = Column(Integer, ForeignKey("barcarena_sustentavel.KML.id"), nullable=True)
    fkIndicador_id = Column(Integer, ForeignKey("barcarena_sustentavel.Indicador.id"), nullable=True)
    fkContribuicao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Contribuicao.id"), nullable=True)

    dimensao = relationship("Dimensao", back_populates="anexos")
    kml = relationship("KML", back_populates="anexos")
    indicador = relationship("Indicador", back_populates="anexos")
    contribuicao = relationship("Contribuicao", back_populates="anexos")
