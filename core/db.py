
# core/db.py
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Usa o caminho do banco definido no settings (ProgramData\IA_PROTEC\status\audit.db)
from settings import get_audit_db_path

DB_PATH = Path(get_audit_db_path(create_dir=True))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # somente para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id        = Column(Integer, primary_key=True, index=True)
    user      = Column(String, index=True)
    event     = Column(String, index=True)        # "login" ou "logout"
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
