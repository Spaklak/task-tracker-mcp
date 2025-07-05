from sqlalchemy.orm import Session
from ..config import SessionLocal

def get_db() -> Session:
    """get Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
