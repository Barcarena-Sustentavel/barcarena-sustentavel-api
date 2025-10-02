from pydantic import BaseModel , Field
from enum import Enum

class EstudoComplementarSchema(BaseModel):
    name: str = Field(default="")
