from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.api import deps
from app.core import media
from app.models.user import User

router = APIRouter()

@router.post("/upload")
async def upload_media(
    media_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """
    Upload a media file (image, video, audio).
    Returns the URL/path of the uploaded file.
    """
    # Validate media type
    if media_type not in ["image", "video", "audio", "document"]:
         raise HTTPException(status_code=400, detail="Invalid media type. Allowed: image, video, audio, document")
    
    # We might need to update media.validate_file to handle "document"
    try:
        if media_type != "document":
            media.validate_file(file, media_type)
        
        # Save the file. Using 0 as entity_id for generic uploads
        file_url = media.save_upload_file(file, entity_id=current_user.id, sub_dir=f"stages/{media_type}")
        
        return {
            "url": file_url,
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
