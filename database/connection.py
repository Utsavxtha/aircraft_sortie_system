from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# SQLite db file will be created in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "aircraft_sortie.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=True)
Base = declarative_base()

_session = None

def get_session():
    global _session
    if _session is None:
        _session = SessionLocal()
    return _session

def reset_session():
    global _session
    if _session is not None:
        try:
            _session.close()
        except Exception:
            pass
    _session = SessionLocal()
    return _session