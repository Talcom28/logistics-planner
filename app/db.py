from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://logistics:logistics@localhost:5432/logistics",
)


def _create_engine_with_fallback(url: str):
    try:
        return create_engine(url, echo=False)
    except ImportError as e:
        msg = str(e)
        if "psycopg2" in msg or "_psycopg" in msg:
            alt_url = url.replace("postgresql+psycopg2", "postgresql+psycopg")
            if alt_url == url and url.startswith("postgresql://"):
                alt_url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            return create_engine(alt_url, echo=False)
        raise


# echo True for debugging locally
engine = _create_engine_with_fallback(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()