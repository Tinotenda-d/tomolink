# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Create the SQLAlchemy engine (SQLAlchemy will manage connections)
engine = create_engine(DATABASE_URL)
# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# Base class for our models to inherit
Base = declarative_base()

# Dependency for getting DB session (to use with FastAPI's Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
