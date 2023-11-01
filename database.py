from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345678@localhost/Todos"
SQLALCHEMY_DATABASE_URL = f"{settings.SQLALCHEMY_DATABASE_URL}/{settings.DB_NAME}"

# , connect_args={"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
