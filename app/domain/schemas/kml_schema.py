from pydantic import BaseModel
class KMLSchema(BaseModel):
    id: int
    nome: str
    fkDimensao: int

    class Config:
        from_atributes = True