from pydantic import BaseModel
from enum import Enum
from typing import Optional

class ContribuicaoSchema(BaseModel):
    id: int
    nome: str = None
    email: str = None
    telefone: str = None
    comentario: str
    fkDimensao_id: int 

    class Config:
        from_atributes = True

class ContribuicaoParamenters(str, Enum):
    nome = "usario1"
    email = "email@email.com"
    telefone = "0919xxxx-xxxx"
    comentario = "comentario 1"  
    fkDimensao_id = "1"