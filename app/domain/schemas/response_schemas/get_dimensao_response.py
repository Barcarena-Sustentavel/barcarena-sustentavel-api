from typing import List
from pydantic import BaseModel
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema

class DimensaoData(BaseModel):  # Response Model
    dimensao: dimesao_schema.DimensaoSchema
    indicadores: List[str]
    referencias: List[referencia_schema.ReferenciaSchema]

    class Config:
        from_atributes = True

