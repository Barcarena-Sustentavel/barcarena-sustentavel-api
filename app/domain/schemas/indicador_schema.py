from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Annotated, Any
from fastapi import UploadFile, File
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

    
class DadosGrafico(BaseModel):
    tipoGrafico: Optional[str]
    tituloGrafico: Optional[str]
    descricaoGrafico: Optional[str]
    dados: List[List[int | float]]
    categoria: List[int | float | str]

class IndicadorGraficos(IndicadorSchema):
    graficos: List[DadosGrafico]

class UpdateIndicadorSchema(BaseModel):
    nome: Optional[str]
    path: Optional[str]
    descricaoGrafico: Optional[str]
    tituloGrafico: Optional[str]
    tipoGrafico: Optional[str]