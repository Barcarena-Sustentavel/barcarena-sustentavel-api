from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class IndicadorSchema(BaseModel):
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

class CreateIndicadorGrafico(BaseModel):
    arquivo: str
    descricaoGrafico: Optional[str]
    tituloGrafico: str
    tipoGrafico: str

class CreateIndicadorSchema(IndicadorSchema):
    graficos: List[CreateIndicadorGrafico]

class UpdateIndicadorSchema(BaseModel):
    nome: Optional[str]
    path: Optional[str]
    descricaoGrafico: Optional[str]
    tituloGrafico: Optional[str]
    tipoGrafico: Optional[str]