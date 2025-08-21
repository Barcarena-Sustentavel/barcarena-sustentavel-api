from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(..., min_length=32, description="Must be at least 32 characters long. Generate with: `openssl rand -hex 32`")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # This will automatically read from a .env file and environment variables
    class Config:
        env_file = ".env"
        case_sensitive = True # Environment variable names are case-sensitive on some systems

# Create a global settings object
settings = Settings()
