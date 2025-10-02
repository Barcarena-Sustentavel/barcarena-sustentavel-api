from typing import List
from pydantic import BaseModel
from app.domain.schemas import indicador_schema, anexo_schema

class IndicadorData(BaseModel):  # Response Model
    indicadores: indicador_schema.IndicadorSchema
    arquivos: List[anexo_schema.AnexoSchema]

class AnexoIndicadorSchema(BaseModel):  # Response Model
    dados:List[List[int]]
    titulo: str
    tipoGrafico: str
    descricaoGrafico: str