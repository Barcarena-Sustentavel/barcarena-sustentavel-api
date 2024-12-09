from pydantic import BaseModel
from  typing import List

class Dimensao(BaseModel):
    id: int
    nome: str
    descricao: str

class Indicador(BaseModel):
    id: int
    fkDimensao: int
    nome: str

class Anexo(BaseModel):
    id: int
    path: str
    fkIndicador: int
    fkDimensao: int
    fkKml: int
    fkContribuicao: int

class Referencia(BaseModel):
    id: int
    nome: str
    link: str
    fkDimensao: int

class Kml(BaseModel):
    id: int
    nome: str
    fkDimensao: int

class Contribuicao(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    comentario: str
    fkDimensao: int
