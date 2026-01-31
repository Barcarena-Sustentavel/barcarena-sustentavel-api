from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
import os

class Environment(BaseSettings):
    tipo:str = 'development'

node_env = Environment().tipo #os.environ.get('NODE_ENV')
print(node_env)
database_url = "postgresql://barcarena_sustentavel:barcarenasustentavel@54.233.210.68:6000/barcarena_sustentavel"
if node_env == 'production':
    database_url ="postgresql://barcarena_sustentavel:barcarenasustentavel@barcarena-postgresql:5432/barcarena_sustentavel"
print(database_url)
SQLALCHEMY_DATABASE_URL = database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True) # pool_pre_ping for robust connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
