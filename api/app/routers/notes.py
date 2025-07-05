from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..schemas import NoteCreate, NoteUpdate, NoteResponse, StatusType
from ..services import NotesService
from ..dependencies import get_db

router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={
        404: {"description": "Note not found"},
        422: {"description": "Validation error"}
    }
)

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create new note.
    
    - **name**: Name of the note
    - **description**: description of the note
    - **comment**: Comment for the note
    - **status**: Note's status (by deffault: in_progress)
    """
    try:
        service = NotesService(db)
        db_note = service.create_note(note)
        return db_note
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when creating a note: {str(e)}"
        )

@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    status_filter: Optional[StatusType] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get list of notes with pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records (1-1000)
    - **status_filter**: Filter by note status
    """
    service = NotesService(db)
    
    if status_filter:
        notes = service.get_notes_by_status(status_filter.value, skip, limit)
    else:
        notes = service.get_notes(skip, limit)
    
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    """
    Get note by ID.

    - **note_id**: Unique note identifier
    """
    service = NotesService(db)
    db_note = service.get_note(note_id)
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )
    
    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update note.

    - **note_id**: Unique note identifier
    - **name**: New note title (optional)
    - **description**: New note description (optional)
    - **comment**: New note comment (optional)
    - **status**: New note status (optional)
    """
    service = NotesService(db)
    db_note = service.update_note(note_id, note_update)
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )
    
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete note.

    - **note_id**: Unique note identifier
    """
    service = NotesService(db)
    success = service.delete_note(note_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )

@router.get("/stats/count")
async def get_notes_count(
    db: Session = Depends(get_db)
):
    """
    Get total count of notes.
    """
    service = NotesService(db)
    count = service.get_notes_count()
    return {"total_notes": count}
