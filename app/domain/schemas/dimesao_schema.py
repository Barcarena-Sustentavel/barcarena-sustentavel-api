from pydantic import BaseModel , Field
from enum import Enum

class DimensaoSchema(BaseModel):
    nome: str = Field(default="")
    descricao: str = Field(default="")

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
