from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
import app.domain.schemas.indicador_schema as indicador_schema
#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class AnexoSchema(BaseModel):
    id: Optional[int]
    path: str
    descricaoGrafico: Optional[str] 
    tipoGrafico: Optional[str]
    fkIndicador: Optional[int] 
    fkDimensao: Optional[int] 
    fkKml: Optional[int]
    fkContribuicao: Optional[int]

    class Config:
        from_atributes = True
        json_schema_extra ={
            "example": {
                "id": 1,
                "path": "caminho/do/arquivo.jpg",
                "fkIndicador": 1,
                "fkDimensao": 1,
                "fkKml": 1,
                "fkContribuicao": 1
            }
        }

class AnexoIndicadorSchema(BaseModel):
    id: int
    path: Optional[str]
    descricaoGrafico: Optional[str] 
    tipoGrafico: Optional[str] 
    tituloGrafico: Optional[str]

class UpdateAnexoIndicadorSchema(indicador_schema.IndicadorSchema):
    graficos: List[AnexoIndicadorSchema]
    


