from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "mysql+pymysql://aircraft_user:Aircraft1@localhost:3306/aircraft_db"

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)
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