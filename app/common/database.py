# app/common/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")

if not DATABASE_URI:
    raise RuntimeError("DATABASE_URI not found in .env file")

# ✅ Create SQLAlchemy engine with reconnection safety
engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True,   # Checks if connection is still valid before using
    pool_recycle=300,     # Recycles connections every 5 minutes to avoid timeouts
    echo=False            # Set to True for SQL debug output
)

# ✅ Declarative base for models
Base = declarative_base()

# ✅ Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db_session():
    """Return a new SQLAlchemy session."""
    return SessionLocal()
