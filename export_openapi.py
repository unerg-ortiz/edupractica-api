"""
Script to export OpenAPI schema for Postman import.
Run with: poe export-postman
"""
import json
from app.main import app

def export_openapi():
    """Export OpenAPI schema to a JSON file for Postman import."""
    openapi_schema = app.openapi()
    
    # Save as OpenAPI JSON (Postman compatible)
    output_file = "postman_collection.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI schema exported to: {output_file}")
    print(f"📦 Import this file in Postman: File > Import > Upload Files")
    print(f"🔗 Or use the live endpoint while server is running: http://127.0.0.1:8000/openapi.json")

if __name__ == "__main__":
    export_openapi()
