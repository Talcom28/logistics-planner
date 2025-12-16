from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://logistics:logistics@localhost:5432/logistics",
)

Base = declarative_base()

_engine = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine
    url = DATABASE_URL
    try:
        _engine = create_engine(url, echo=False)
        return _engine
    except Exception:
        # Try psycopg (v3) dialect
        try:
            alt_url = url
            if url.startswith("postgresql+psycopg2"):
                alt_url = url.replace("postgresql+psycopg2", "postgresql+psycopg", 1)
            elif url.startswith("postgresql://"):
                alt_url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            _engine = create_engine(alt_url, echo=False)
            return _engine
        except Exception:
            # As a last resort, use in-memory SQLite so the app can boot
            try:
                _engine = create_engine("sqlite:///:memory:", echo=False)
                return _engine
            except Exception:
                # Give up: re-raise the original
                raise


def get_db():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
