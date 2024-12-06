from pydantic import BaseModel

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
