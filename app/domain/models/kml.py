from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class KML(Base):
    __tablename__ = "KMLs"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fkDimensao_id = Column(Integer, ForeignKey("barcarena_sustentavel.Dimensao.id"), nullable=False)

    dimensao = relationship("Dimensao", back_populates="kmls")