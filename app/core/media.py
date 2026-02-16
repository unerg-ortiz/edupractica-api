import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

# Define upload directory
UPLOAD_DIR = Path("uploads/feedback")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"}
MAX_FILE_SIZE_MB = 10

def validate_file(file: UploadFile, media_type: str):
    """Validate file type and size"""
    if media_type == "image":
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
    elif media_type == "audio":
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid audio type. Allowed: {', '.join(ALLOWED_AUDIO_TYPES)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media type specified"
        )
    
    # Size check would typically require reading the file or checking content-length header
    # For now we'll assume the web server handles max body size

def save_upload_file(file: UploadFile, stage_id: int) -> str:
    """
    Save an uploaded file to the disk.
    Returns the relative path to the file.
    """
    stage_dir = UPLOAD_DIR / str(stage_id)
    stage_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = Path(file.filename).suffix
    # Create a unique filename based on original name to avoid collisions if needed
    # but here we keep original to be simple, maybe prefix with timestamp in production
    import time
    filename = f"{int(time.time())}_{file.filename}"
    file_path = stage_dir / filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    # Return path relative to app root for URL generation
    return str(file_path).replace("\\", "/")

def delete_file(file_path: str):
    """Delete a file from disk"""
    if not file_path:
        return
        
    path = Path(file_path)
    if path.exists():
        try:
            path.unlink()
        except Exception:
            pass  # Log error in production
