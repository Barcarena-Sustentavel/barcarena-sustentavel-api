from pydantic import BaseModel
from enum import Enum
from typing import Optional
#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class AnexoSchema(BaseModel):
    id: Optional[int]
    path: str
    descricaoGrafico: Optional[str] #str = None
    tipoGrafico: Optional[str] #str = None
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
    


