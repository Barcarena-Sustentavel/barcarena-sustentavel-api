from pydantic import BaseModel

class ReferenciaSchema(BaseModel):
    id: int
    nome: str
    link: str
    fkDimensao: int

    class Config:
        from_atributes = True
