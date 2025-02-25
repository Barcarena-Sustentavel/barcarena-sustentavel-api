from pydantic import BaseModel
from enum import Enum
class KMLSchema(BaseModel):
    id: int
    nome: str
    fkDimensao: int

    class Config:
        from_atributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Mapa Social",
                "fkDimensao": 1
            }
        }

class KMLParameters(str, Enum):
    mapa_social = "Mapa Social"
    mapa_econômica = "Mapa Econômica"
    mapa_ambiental = "Mapa Ambiental"


class CreateKMLSchema(BaseModel):
    nome: str
    arquivo: str