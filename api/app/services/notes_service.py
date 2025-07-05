from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ..models import NotesMain
from ..schemas import NoteCreate, NoteUpdate

class NotesService:
    """Note functions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_note(self, note: NoteCreate) -> NotesMain:
        """Create new note."""
        db_note = NotesMain(
            name=note.name,
            description=note.description,
            comment=note.comment,
            status=note.status
        )
        
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        return db_note
    
    def get_note(self, note_id: int) -> Optional[NotesMain]:
        """Get note by id."""
        return self.db.query(NotesMain).filter(NotesMain.id == note_id).first()
        
    def get_notes(self, skip: int = 0, limit: int = 100) -> List[NotesMain]:
        """Get a paginated list of nodes."""
        return self.db.query(NotesMain).offset(skip).limit(limit).all()

    def update_note(self, note_id: int, note_update: NoteUpdate) -> Optional[NotesMain]:
        """Update note."""
        db_note = self.get_note(note_id)
        if not db_note:
            return None
        
        update_data = note_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_note, field, value)
        
        self.db.commit()
        self.db.refresh(db_note)
        return db_note
    
    def delete_note(self, note_id: int) -> bool:
        """Delete note."""
        db_note = self.get_note(note_id)
        if not db_note:
            return False
        
        self.db.delete(db_note)
        self.db.commit()
        return True
    
    def get_notes_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[NotesMain]:
        """Get note by status."""
        return (
            self.db.query(NotesMain)
            .filter(NotesMain.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_notes_count(self) -> int:
        """Get the number of notes."""
        return self.db.query(NotesMain).count()