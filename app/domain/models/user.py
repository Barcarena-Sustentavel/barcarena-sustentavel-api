from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class User(Base):
    __tablename__ = "User"
    __table_args__ = {"schema": "barcarena_sustentavel"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
