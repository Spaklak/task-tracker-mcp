from fastapi import FastAPI
from .routers import router
from .config import engine
from .models import Base

app = FastAPI(
    title="Notes API",
    description="API for work with notes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Create tables."""
    Base.metadata.create_all(bind=engine)
    print("Tables were created!")


app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Main API page"""
    return {
        "message": "Notes API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }