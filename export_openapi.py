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

def resolve_schema_ref(ref_path, openapi_schema):
    """Resolve a $ref path to the actual schema."""
    if not ref_path.startswith("#/"):
        return None
    parts = ref_path[2:].split("/")
    result = openapi_schema
    for part in parts:
        if isinstance(result, dict) and part in result:
            result = result[part]
        else:
            return None
    return result

def generate_example_value(prop_def, prop_name, openapi_schema, required_fields=None):
    """Generate an example value based on property definition."""
    required_fields = required_fields or []
    
    # Handle $ref
    if "$ref" in prop_def:
        ref_schema = resolve_schema_ref(prop_def["$ref"], openapi_schema)
        if ref_schema:
            return generate_example_from_schema(ref_schema, openapi_schema)
        return {}
    
    # Handle anyOf (nullable types, unions)
    if "anyOf" in prop_def:
        # Find the non-null type
        for option in prop_def["anyOf"]:
            if option.get("type") != "null":
                return generate_example_value(option, prop_name, openapi_schema, required_fields)
        return None
    
    prop_type = prop_def.get("type", "string")
    prop_format = prop_def.get("format")
    
    # Use default if available
    if "default" in prop_def:
        return prop_def["default"]
    
    # Generate based on type
    if prop_type == "string":
        if prop_format == "email":
            return "usuario@ejemplo.com"
        elif prop_format == "password":
            return "contraseña123"
        elif prop_format == "date":
            return "2026-01-01"
        elif prop_format == "date-time":
            return "2026-01-01T00:00:00Z"
        elif prop_format == "uri" or prop_format == "url":
            return "https://ejemplo.com"
        elif "name" in prop_name.lower():
            return "Nombre de ejemplo"
        elif "description" in prop_name.lower():
            return "Descripción de ejemplo"
        elif "reason" in prop_name.lower():
            return "Razón de ejemplo"
        elif "icon" in prop_name.lower():
            return "icon-example"
        else:
            return f"valor_{prop_name}"
    elif prop_type == "integer":
        return 1
    elif prop_type == "number":
        return 1.0
    elif prop_type == "boolean":
        return True
    elif prop_type == "array":
        items = prop_def.get("items", {})
        item_example = generate_example_value(items, prop_name + "_item", openapi_schema)
        return [item_example] if item_example is not None else []
    elif prop_type == "object":
        return {}
    
    return None

def generate_example_from_schema(schema, openapi_schema):
    """Generate a complete example object from a schema."""
    if not schema or not isinstance(schema, dict):
        return {}
    
    # Handle $ref at top level
    if "$ref" in schema:
        ref_schema = resolve_schema_ref(schema["$ref"], openapi_schema)
        if ref_schema:
            return generate_example_from_schema(ref_schema, openapi_schema)
        return {}
    
    example = {}
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    for prop_name, prop_def in properties.items():
        value = generate_example_value(prop_def, prop_name, openapi_schema, required_fields)
        if value is not None:
            example[prop_name] = value
    
    return example

def get_request_body_example(content_type, schema_def, openapi_schema):
    """Get example body from schema definition."""
    if not schema_def:
        return None
    
    return generate_example_from_schema(schema_def, openapi_schema)

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
                        example = get_request_body_example("application/json", schema, openapi_schema)
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
                        example = get_request_body_example("form", schema, openapi_schema)
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
