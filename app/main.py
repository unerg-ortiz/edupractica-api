from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import os

from app.api.endpoints import login, users, categories, stages, feedback, oauth, analytics, transfer

# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS middleware ──────────────────────────────────────────────────────────
# DEBE registrarse ANTES que cualquier app.mount() para que las sub-aplicaciones
# montadas también hereden las respuestas con los headers correctos.
# allow_origins=["*"]: acepta peticiones de CUALQUIER dominio.
# allow_credentials DEBE ser False cuando allow_origins=["*"] (restricción CORS spec).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(login.router, tags=["login"])
app.include_router(oauth.router, prefix="/auth", tags=["oauth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(stages.router, prefix="/api", tags=["stages"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(transfer.router, prefix="/api/transfer", tags=["transfer"])

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
