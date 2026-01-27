import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://user:password@host:port/dbname"
    VECTOR_DB_URL: str = "postgresql+psycopg://user:password@host:port/dbname" # Default or read from .env

    class Config:
        env_file = ".env"

settings = Settings()