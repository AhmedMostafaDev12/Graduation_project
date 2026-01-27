from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sentry_app.config import settings

SQLCHEMY_DATABASE_URL = settings.get_database_url()

engine = create_engine(SQLCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()   


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()