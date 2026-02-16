from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
<<<<<<< HEAD
from app.api.endpoints import login, users, categories, stages, feedback, analytics
import os
=======
from app.api.endpoints import login, users, categories, stages, feedback, oauth, analytics
>>>>>>> HU78

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Mount uploads directory to serve media files
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router, tags=["login"])
app.include_router(oauth.router, prefix="/auth", tags=["oauth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(stages.router, prefix="/api", tags=["stages"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(transfer.router, prefix="/api/transfer", tags=["transfer"])

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/admin/categories.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}
