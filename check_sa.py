from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_sa_columns():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    inspector = inspect(engine)
    columns = inspector.get_columns("stages")
    print("SQLAlchemy Inspector sees these columns for 'stages':")
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

if __name__ == "__main__":
    check_sa_columns()
