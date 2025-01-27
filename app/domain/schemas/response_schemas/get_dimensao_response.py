from typing import List
from pydantic import BaseModel
from app.domain.schemas import indicador_schema, referencia_schema

class DimensaoData(BaseModel):  # Response Model
    indicadores: List[indicador_schema.IndicadorSchema]
    referencias: List[referencia_schema.ReferenciaSchema]

    class Config:
        from_atributes = True

