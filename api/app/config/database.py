from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
POSTGRES_SERVICE_NAME=os.getenv("POSTGRES_SERVICE_NAME")
if not DB_USER or not DB_PASSWORD or not DB_NAME or not POSTGRES_SERVICE_NAME:
    raise ValueError("Values were not passed to .env")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{POSTGRES_SERVICE_NAME}:5432/{DB_NAME}")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()