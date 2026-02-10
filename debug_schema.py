from app.main import app
import json

openapi_schema = app.openapi()
paths = openapi_schema.get("paths", {})
feedback_media_path = paths.get("/api/feedback/{feedback_id}/media", {})
post_op = feedback_media_path.get("post", {})
request_body = post_op.get("requestBody", {})
content = request_body.get("content", {})
multipart = content.get("multipart/form-data", {})

print(json.dumps(multipart, indent=2))
