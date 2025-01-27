from typing import List
from pydantic import BaseModel
from app.domain.schemas import indicador_schema, anexo_schema

class IndicadorData(BaseModel):  # Response Model
    indicadores: List[indicador_schema.IndicadorSchema]
    referencias: List[anexo_schema.AnexoSchema]