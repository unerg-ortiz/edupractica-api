"""
Database initialization script: migrations + seeds.
Run with: poe init-db

1. Creates/updates all tables (migrations).
2. Applies manual column migrations for SQLite.
3. Seeds default users (admin, professor, students).
"""
import sqlite3
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User

# Ensure ALL models are imported for metadata
from app.models import user, audit, category, topic, stage, feedback, transfer


# ──────────────────────────────────────────────
# 1. MIGRATIONS
# ──────────────────────────────────────────────

def run_migrations():
    """Create tables and apply manual column migrations for SQLite."""
    print("\n🔄 Ejecutando migraciones...")

    # Create all tables from models
    Base.metadata.create_all(bind=engine)
    print("  ✅ Tablas creadas/verificadas.")

    # SQLite manual column migrations (ALTER TABLE)
    if "sqlite" in settings.DATABASE_URL:
        _sqlite_migrations()


def _sqlite_migrations():
    """Apply column additions that SQLAlchemy create_all won't handle on existing tables."""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("./", "")
    
    # Check if DB file exists before connecting
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    migrations = [
        # Users Table
        {
            "table": "users",
            "column": "role",
            "sql": "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'",
            "post": "UPDATE users SET role = 'admin' WHERE is_superuser = 1",
        },
        {
            "table": "users",
            "column": "is_professor",
            "sql": "ALTER TABLE users ADD COLUMN is_professor BOOLEAN DEFAULT 0",
        },
        {
            "table": "users",
            "column": "oauth_provider",
            "sql": "ALTER TABLE users ADD COLUMN oauth_provider TEXT",
        },
        {
            "table": "users",
            "column": "oauth_id",
            "sql": "ALTER TABLE users ADD COLUMN oauth_id TEXT",
        },
        {
            "table": "users",
            "column": "is_blocked",
            "sql": "ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT 0",
        },
        {
            "table": "users",
            "column": "block_reason",
            "sql": "ALTER TABLE users ADD COLUMN block_reason TEXT",
        },
        # Categories Table
        {
            "table": "categories",
            "column": "created_at",
            "sql": "ALTER TABLE categories ADD COLUMN created_at DATETIME",
            "post": "UPDATE categories SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        },
        # Stages Table
        {
            "table": "stages",
            "column": "topic_id",
            "sql": "ALTER TABLE stages ADD COLUMN topic_id INTEGER",
        },
        {
            "table": "stages",
            "column": "professor_id",
            "sql": "ALTER TABLE stages ADD COLUMN professor_id INTEGER",
        },
        {
            "table": "stages",
            "column": "media_url",
            "sql": "ALTER TABLE stages ADD COLUMN media_url TEXT",
        },
        {
            "table": "stages",
            "column": "media_type",
            "sql": "ALTER TABLE stages ADD COLUMN media_type TEXT",
        },
        {
            "table": "stages",
            "column": "media_filename",
            "sql": "ALTER TABLE stages ADD COLUMN media_filename TEXT",
        },
        {
            "table": "stages",
            "column": "media_files",
            "sql": "ALTER TABLE stages ADD COLUMN media_files JSON",
        },
        {
            "table": "stages",
            "column": "interactive_config",
            "sql": "ALTER TABLE stages ADD COLUMN interactive_config JSON",
        },
        {
            "table": "stages",
            "column": "challenge_description",
            "sql": "ALTER TABLE stages ADD COLUMN challenge_description TEXT",
        },
        {
            "table": "stages",
            "column": "category_id",
            "sql": "ALTER TABLE stages ADD COLUMN category_id INTEGER",
        },
        {
            "table": "stages",
            "column": "approval_status",
            "sql": "ALTER TABLE stages ADD COLUMN approval_status TEXT DEFAULT 'pending'",
        },
        {
            "table": "stages",
            "column": "approval_comment",
            "sql": "ALTER TABLE stages ADD COLUMN approval_comment TEXT",
        },
        {
            "table": "stages",
            "column": "submitted_at",
            "sql": "ALTER TABLE stages ADD COLUMN submitted_at DATETIME",
        },
        {
            "table": "stages",
            "column": "is_active",
            "sql": "ALTER TABLE stages ADD COLUMN is_active BOOLEAN DEFAULT 1",
        },
        {
            "table": "stages",
            "column": "is_archived",
            "sql": "ALTER TABLE stages ADD COLUMN is_archived BOOLEAN DEFAULT 0",
        },
    ]

    for m in migrations:
        try:
            cursor.execute(f"PRAGMA table_info({m['table']})")
            columns = [col[1] for col in cursor.fetchall()]
            if not columns:
                # Table might not exist yet if create_all failed or wasn't run
                continue
                
            if m["column"] not in columns:
                cursor.execute(m["sql"])
                if m.get("post"):
                    cursor.execute(m["post"])
                conn.commit()
                print(f"  ✅ Columna '{m['column']}' añadida a '{m['table']}'.")
            # else:
            #     print(f"  ✅ Columna '{m['column']}' ya existe en '{m['table']}'.")
        except Exception as e:
            print(f"  ⚠️ Error en migración para '{m['table']}.{m['column']}': {e}")

    conn.close()


# ──────────────────────────────────────────────
# 2. SEEDS
# ──────────────────────────────────────────────

SEED_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin",
        "is_superuser": True,
        "is_professor": True, # Admin is also professor usually
        "is_active": True,
    },
    {
        "email": "profe@example.com",
        "password": "profe123",
        "full_name": "Profesor de Prueba",
        "role": "professor",
        "is_superuser": False,
        "is_professor": True,
        "is_active": True,
    },
    {
        "email": "student1@example.com",
        "password": "password123",
        "full_name": "Estudiante Uno",
        "role": "student",
        "is_superuser": False,
        "is_professor": False,
        "is_active": True,
    },
    {
        "email": "student2@example.com",
        "password": "password123",
        "full_name": "Estudiante Dos",
        "role": "student",
        "is_superuser": False,
        "is_professor": False,
        "is_active": True,
    },
    {
        "email": "student3@example.com",
        "password": "password123",
        "full_name": "Estudiante Tres",
        "role": "student",
        "is_superuser": False,
        "is_professor": False,
        "is_active": True,
    },
]


def run_seeds(db: Session):
    """Create default users if they don't exist."""
    print("\n🌱 Ejecutando seeds...")

    for user_data in SEED_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            new_user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_superuser=user_data["is_superuser"],
                is_professor=user_data.get("is_professor", False),
                is_active=user_data["is_active"],
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"  ✅ Usuario creado: {user_data['email']} (rol: {user_data['role']})")
        else:
            # Update role/professor status if needed
            updated = False
            if existing.role != user_data["role"]:
                existing.role = user_data["role"]
                updated = True
            
            should_be_prof = user_data.get("is_professor", False)
            if existing.is_professor != should_be_prof:
                existing.is_professor = should_be_prof
                updated = True
            
            if updated:
                db.add(existing)
                db.commit()
                print(f"  🔄 Usuario actualizado: {existing.email}")
            else:
                print(f"  ⏭️  Ya existe: {existing.email} (rol: {existing.role})")

    print("")


# ──────────────────────────────────────────────
# 3. MAIN
# ──────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  EduPractica - Inicialización de Base de Datos")
    print("=" * 50)

    run_migrations()

    db = SessionLocal()
    try:
        run_seeds(db)
    finally:
        db.close()

    print("✅ Base de datos lista.\n")
    print("📋 Credenciales de acceso:")
    print("   Admin:      admin@example.com / admin123")
    print("   Profesor:   profe@example.com / profe123")
    print("   Estudiante: student1@example.com / password123")
    print("")


if __name__ == "__main__":
    main()
