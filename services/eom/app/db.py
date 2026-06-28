import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./eom.sqlite3')

def _build_engine(url: str):
    connect_args = {}
    if url.startswith('sqlite:'):
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args)

engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
