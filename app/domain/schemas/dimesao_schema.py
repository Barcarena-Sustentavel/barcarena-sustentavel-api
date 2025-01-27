from pydantic import BaseModel
from enum import Enum

class DimensaoSchema(BaseModel):
    id: int
    nome: str = "Social"
    descricao: str

    class Config:
        from_atributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Social",
                "descricao": "Descrição da dimensão 1"
            }
        }

class DimensaoParameters(str, Enum):
    social = "Social"
    econômica = "Econômica"
    ambiental = "Ambiental"
