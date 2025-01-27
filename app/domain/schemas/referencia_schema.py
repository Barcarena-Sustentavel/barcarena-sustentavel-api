from pydantic import BaseModel

class ReferenciaSchema(BaseModel):
    id: int
    nome: str
    link: str
    fkDimensao: int

    class Config:
        from_atributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Relatório Social",
                "link": "http://example.com/social",
                "fkDimensao": 1
            }
        }
