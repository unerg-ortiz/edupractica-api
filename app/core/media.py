import os
import shutil
import time
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
try:
    from PIL import Image
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# Define upload directory
BASE_UPLOAD_DIR = Path("uploads")
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "audio/x-wav"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/x-matroska", "video/webm"}
MAX_FILE_SIZE_MB = 100

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
    elif media_type == "video":
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid video type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media type specified"
        )

def compress_image(source_path: Path, target_path: Path, quality: int = 85):
    """Compress image if Pillow is installed"""
    if not PILLOW_INSTALLED:
        return False
    
    try:
        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for PNG/RGBA to JPEG)
            if img.mode in ("RGBA", "P") and target_path.suffix.lower() in [".jpg", ".jpeg"]:
                img = img.convert("RGB")
            
            # Preserve aspect ratio and scale down if very large (e.g., > 2000px)
            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
            img.save(target_path, optimize=True, quality=quality)
        return True
    except Exception:
        return False

def save_upload_file(file: UploadFile, entity_id: int, sub_dir: str = "feedback") -> str:
    """
    Save an uploaded file to the disk.
    Returns the relative path to the file.
    """
    upload_path = BASE_UPLOAD_DIR / sub_dir / str(entity_id)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename
    filename = f"{int(time.time())}_{file.filename}"
    file_path = upload_path / filename
    
    try:
        # Save original file first
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Check file size after saving
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB"
            )
        
        # Automatic compression for images
        if file.content_type in ALLOWED_IMAGE_TYPES and PILLOW_INSTALLED:
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
            file_path.rename(temp_path)
            if compress_image(temp_path, file_path):
                temp_path.unlink()
            else:
                temp_path.rename(file_path) # Restore if failed
            
    except HTTPException:
        raise
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
