from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import categories
from app.db.base import Base
from app.db.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(categories.router, prefix="/categories", tags=["categories"])

@app.get("/")
def read_root():
    return {"message": "Welcome to EduPractica API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
