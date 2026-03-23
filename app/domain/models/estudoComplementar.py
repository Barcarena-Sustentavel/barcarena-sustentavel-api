from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class EstudoComplementar(Base):
    __tablename__ = "EstudoComplementar"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    pagina = Column(String, CheckConstraint("pagina IN ('Pagina_inicial', 'Pagina_sobre')"), nullable=True)
    fkDimensao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Dimensao.id"), nullable=True)
    dimensao = relationship("Dimensao", back_populates="estudoComplementar")
    anexos = relationship("Anexo", back_populates="estudoComplementar")
