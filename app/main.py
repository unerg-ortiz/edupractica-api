from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import os
import logging

from app.api.endpoints import login, users, categories, stages, feedback, oauth, analytics, transfer, topics, media

# ── Logging configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS middleware ──────────────────────────────────────────────────────────
# DEBE registrarse ANTES que cualquier app.mount() para que las sub-aplicaciones
# montadas también hereden las respuestas con los headers correctos.
# allow_origins=["*"] is restricted, using allow_origin_regex or explicit list for better compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── Request logging middleware ───────────────────────────────────────────────
from fastapi import Request
from fastapi.responses import JSONResponse
import time
import traceback

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} - ERROR ({process_time:.3f}s)")
        logger.error(f"Exception: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {type(e).__name__}: {str(e)}"}
        )

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(login.router, tags=["login"])
app.include_router(oauth.router, prefix="/auth", tags=["oauth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(stages.router, prefix="/api", tags=["stages"])
app.include_router(topics.router, prefix="/api", tags=["topics"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(transfer.router, prefix="/api/transfer", tags=["transfer"])
app.include_router(media.router, prefix="/api/media", tags=["media"])

# ── Root & health endpoints ───────────────────────────────────────────────────
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/admin/categories.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ── Static file mounts (AL FINAL para no bloquear startup) ───────────────────
# Los montamos después de los routers para que un fallo en el sistema de archivos
# no impida que la aplicación y sus routers arranquen.

# Directorio de uploads (local fallback cuando no hay Supabase configurado)
uploads_dir = "uploads"
try:
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
except (OSError, PermissionError) as e:
    print(f"Warning: Could not create/mount 'uploads' directory: {e}")

# Archivos estáticos del admin (HTML/CSS/JS legacy)
static_dir = "app/static"
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: Static directory '{static_dir}' not found. Skipping mount.")

# ── Database tables ───────────────────────────────────────────────────────────
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not initialize database tables. Error: {e}")
