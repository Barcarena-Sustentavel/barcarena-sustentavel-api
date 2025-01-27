from pydantic import BaseModel
from enum import Enum
#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class AnexoSchema(BaseModel):
    id: int
    path: str
    fkIndicador: int
    fkDimensao: int
    fkKml: int
    fkContribuicao: int

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
    


