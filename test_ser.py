from app.db.session import SessionLocal
from app.models.stage import Stage
from app.schemas.stage import Stage as StageSchema
from pydantic import ValidationError

def test_serialization():
    db = SessionLocal()
    try:
        stage = db.query(Stage).filter(Stage.approval_status == "pending").first()
        if not stage:
            # Create a mock one if none exist
            print("No pending stages found, creating a mock one in memory...")
            stage = Stage(
                id=999,
                category_id=1,
                order=1,
                title="Test",
                approval_status="pending"
            )
        
        print(f"Testing serialization for Stage ID: {stage.id}")
        schema_data = StageSchema.model_validate(stage)
        print("✅ Serialization successful!")
        print(schema_data.model_dump_json(indent=2))
        
    except ValidationError as ve:
        print(f"❌ Pydantic Validation Error: {ve}")
    except Exception as e:
        print(f"❌ General Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_serialization()
