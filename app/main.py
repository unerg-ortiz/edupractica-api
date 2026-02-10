from fastapi import FastAPI
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.endpoints import login, users, categories, stages, feedback

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(stages.router, prefix="/api", tags=["stages"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])

@app.get("/")
def read_root():
    return {"message": "Welcome to EduPractica API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
