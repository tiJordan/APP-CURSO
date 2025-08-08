# core/db.py
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine,Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 1) Path de rede para o status
NETWORK_STATUS = Path(r"\\Srv-aux\projetos$\APP-CURSO\status")

# 2) Escolhe entre rede (.exe) ou local (dev)
if getattr(sys, "frozen", False):
    # quando empacotado via PyInstaller
    DB_FOLDER = NETWORK_STATUS
else:
    # durante o desenvolvimento
    DB_FOLDER = Path(__file__).resolve().parent.parent / "status"

DB_FOLDER.mkdir(parents=True, exist_ok=True)

# 3) String de conexão SQLite (para dev e share)
DB_PATH = DB_FOLDER / "audit.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 4) engine e session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # só para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id        = Column(Integer, primary_key=True, index=True)
    user      = Column(String, index=True)
    event     = Column(String, index=True)        # "login" ou "logout"
    timestamp = Column(DateTime, default=datetime.utcnow)

# Método para criar as tabelas no banco
def init_db():
    Base.metadata.create_all(bind=engine)
