from pydantic import BaseModel

#Funciona semelhante a uma serialização, utilizado para enviar o JSON
class IndicadorSchema(BaseModel):
    id: int
    fkDimensao: int
    nome: str

    class Config:
        from_atributes = True
