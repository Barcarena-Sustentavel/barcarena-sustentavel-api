from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

class UserSchema(BaseModel):
    username:str
    hashed_password:str
