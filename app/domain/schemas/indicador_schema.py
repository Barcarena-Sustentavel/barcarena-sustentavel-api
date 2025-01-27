from pydantic import BaseModel
from enum import Enum
#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class IndicadorSchema(BaseModel):
    id: int
    fkDimensao: int
    nome: str

    class Config:
        from_atributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "fkDimensao": 1,
                "nome": "IDH"
            }
        }

class IndicadorParameters(str, Enum):
    idh = "IDH"
    qualidade_ar= "Qualidade do Ar"
    pib = "PIB"