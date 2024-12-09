from pydantic import BaseModel

class ContribuicaoSchema(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    comentario: str
    fkDimensao_id: int 

    class Config:
        from_atributes = True