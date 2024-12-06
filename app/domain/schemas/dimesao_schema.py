from pydantic import BaseModel
class DimensaoSchema(BaseModel):
    id: int
    nome: str
    descricao: str

    class Config:
        from_atributes = True