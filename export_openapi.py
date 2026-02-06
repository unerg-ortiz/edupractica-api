"""
Script to export Postman Collection v2.1 format.
Run with: poe export-postman

This generates a native Postman Collection with:
- Collection variable 'token'
- Bearer authentication pre-configured with {{token}}
- Fixed _postman_id for collection replacement on import
"""
import json
import uuid
from app.main import app

# Fixed collection ID - Postman will replace existing collection with same ID
COLLECTION_ID = "edupractica-api-collection-v1"

def get_request_body_schema(content_type, schema_ref, openapi_schema):
    """Get example body from schema reference."""
    if not schema_ref:
        return None
    
    # Extract schema name from $ref
    if "$ref" in schema_ref:
        ref_path = schema_ref["$ref"]
        schema_name = ref_path.split("/")[-1]
        schemas = openapi_schema.get("components", {}).get("schemas", {})
        if schema_name in schemas:
            schema = schemas[schema_name]
            # Generate example from properties
            example = {}
            for prop_name, prop_def in schema.get("properties", {}).items():
                if prop_def.get("type") == "string":
                    if prop_def.get("format") == "email":
                        example[prop_name] = "user@example.com"
                    elif prop_def.get("format") == "password":
                        example[prop_name] = "password123"
                    else:
                        example[prop_name] = ""
                elif prop_def.get("type") == "integer":
                    example[prop_name] = 0
                elif prop_def.get("type") == "boolean":
                    example[prop_name] = prop_def.get("default", False)
            return example
    return None

def export_postman_collection():
    """Export API as native Postman Collection v2.1 format."""
    openapi_schema = app.openapi()
    
    # Build Postman collection structure
    collection = {
        "info": {
            "_postman_id": COLLECTION_ID,
            "name": openapi_schema.get("info", {}).get("title", "EduPractica API"),
            "description": openapi_schema.get("info", {}).get("description", "API Collection"),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{token}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "token",
                "value": "",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group endpoints by tag
    tag_folders = {}
    
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, operation in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                tags = operation.get("tags", ["Default"])
                tag = tags[0] if tags else "Default"
                
                if tag not in tag_folders:
                    tag_folders[tag] = {
                        "name": tag.capitalize(),
                        "item": []
                    }
                
                # Build request
                request = {
                    "name": operation.get("summary", f"{method.upper()} {path}"),
                    "request": {
                        "auth": {
                            "type": "bearer",
                            "bearer": [
                                {
                                    "key": "token",
                                    "value": "{{token}}",
                                    "type": "string"
                                }
                            ]
                        },
                        "method": method.upper(),
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}" + path,
                            "host": ["{{baseUrl}}"],
                            "path": [p for p in path.split("/") if p]
                        }
                    },
                    "response": []
                }
                
                # Handle path parameters
                url_path_parts = []
                for part in path.split("/"):
                    if part.startswith("{") and part.endswith("}"):
                        param_name = part[1:-1]
                        url_path_parts.append(f":{param_name}")
                        if "variable" not in request["request"]["url"]:
                            request["request"]["url"]["variable"] = []
                        request["request"]["url"]["variable"].append({
                            "key": param_name,
                            "value": "",
                            "description": f"Path parameter: {param_name}"
                        })
                    else:
                        url_path_parts.append(part)
                
                request["request"]["url"]["path"] = [p for p in url_path_parts if p]
                request["request"]["url"]["raw"] = "{{baseUrl}}" + "/".join(url_path_parts)
                
                # Handle query parameters
                params = operation.get("parameters", [])
                query_params = [p for p in params if p.get("in") == "query"]
                if query_params:
                    request["request"]["url"]["query"] = [
                        {
                            "key": p["name"],
                            "value": str(p.get("schema", {}).get("default", "")),
                            "description": p.get("description", "")
                        }
                        for p in query_params
                    ]
                
                # Handle request body
                request_body = operation.get("requestBody", {})
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        schema = content["application/json"].get("schema", {})
                        example = get_request_body_schema("application/json", schema, openapi_schema)
                        request["request"]["header"].append({
                            "key": "Content-Type",
                            "value": "application/json"
                        })
                        request["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example, indent=2) if example else "{}",
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                    elif "application/x-www-form-urlencoded" in content:
                        schema = content["application/x-www-form-urlencoded"].get("schema", {})
                        example = get_request_body_schema("form", schema, openapi_schema)
                        request["request"]["body"] = {
                            "mode": "urlencoded",
                            "urlencoded": [
                                {"key": k, "value": str(v), "type": "text"}
                                for k, v in (example or {}).items()
                            ]
                        }
                
                tag_folders[tag]["item"].append(request)
    
    # Add folders to collection
    collection["item"] = list(tag_folders.values())
    
    # Save collection
    output_file = "postman_collection.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"Postman Collection exported to: {output_file}")
    print(f"Import in Postman: File > Import > Upload Files")
    print(f"The collection will REPLACE any existing 'EduPractica API' collection")

if __name__ == "__main__":
    export_postman_collection()
