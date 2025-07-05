from sqlalchemy import String, Integer, Column, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM
from ..config import Base
import enum

class NotesMain(Base):
    __tablename__ = "notes_main"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    comment = Column(Text)
    status = Column(String(20), default="in_progress", nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('done', 'in_progress', 'not_activate')",
            name='check_status_values'
        ),
    )