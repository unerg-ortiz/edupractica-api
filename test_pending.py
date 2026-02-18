from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud import crud_stage
from app.api.endpoints import stages
import json

def test_pending_stages():
    db = SessionLocal()
    try:
        print("Testing get_pending_stages CRUD...")
        pending = crud_stage.get_pending_stages(db)
        print(f"Found {len(pending)} pending stages")
        for p in pending:
            print(f"- ID: {p.id}, Status: {p.approval_status}, Submitted: {p.submitted_at}")
    except Exception as e:
        print(f"❌ Error in CRUD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_pending_stages()
