from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://barcarena_sustentavel:barcarenasustentavel@host:5432/barcarena_sustentavel"  # Replace with your PostgreSQL connection string

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