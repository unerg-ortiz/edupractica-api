import os
import shutil
import time
import tempfile
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from app.core.supabase_client import supabase

try:
    from PIL import Image
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# Define upload directory
BASE_UPLOAD_DIR = Path("uploads")
# Only create local directory if NOT using Supabase
if not supabase:
    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "audio/x-wav"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/x-matroska", "video/webm"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}
MAX_FILE_SIZE_MB = 100
BUCKET_NAME = "uploads"

def validate_file(file: UploadFile, media_type: str):
    """Validate file type and size. Note: Size check is better done after reading/saving."""
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
    elif media_type == "document":
        if file.content_type not in ALLOWED_DOC_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Allowed: {', '.join(ALLOWED_DOC_TYPES)}"
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
    Save an uploaded file.
    If Supabase is configured, uploads to Supabase Storage bucket 'uploads'.
    Otherwise, saves to local disk.
    
    Returns the public URL (Supabase) or relative path (local).
    """
    
    # Create a unique filename
    filename = f"{sub_dir}/{entity_id}/{int(time.time())}_{file.filename}"
    
    # Use temporary file to handle saving/compression before final upload/move
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
        
    try:
        # Check file size
        file_size = tmp_path.stat().st_size
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB"
            )

        # Compress image if possible
        if file.content_type in ALLOWED_IMAGE_TYPES and PILLOW_INSTALLED:
             compressed_path = tmp_path.with_suffix(tmp_path.suffix + ".optimized")
             if compress_image(tmp_path, compressed_path):
                 tmp_path.unlink() # Remove original temp
                 tmp_path = compressed_path
    
        # --- Supabase Upload Strategy ---
        if supabase:
            try:
                with open(tmp_path, "rb") as f:
                    file_bytes = f.read()
                    
                # Upload to Supabase Storage
                # Note: 'upsert=True' avoids errors if file exists, though timestamp makes it unique
                response = supabase.storage.from_(BUCKET_NAME).upload(
                    path=filename,
                    file=file_bytes,
                    file_options={"content-type": file.content_type, "upsert": "true"}
                )
                
                # Get Public URL
                public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
                return public_url

            except Exception as e:
                # If bucket doesn't exist, try to create it? (Admin API required usually)
                # Or just fail gracefully
                print(f"Supabase upload error: {e}")
                raise HTTPException(status_code=500, detail="Failed to upload file to storage")

        # --- Local Storage Strategy (Fallback) ---
        else:
            upload_path = BASE_UPLOAD_DIR / sub_dir / str(entity_id)
            upload_path.mkdir(parents=True, exist_ok=True)
            final_path = upload_path / Path(filename).name
            
            shutil.move(str(tmp_path), str(final_path))
            return str(final_path).replace("\\", "/")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    finally:
        # Clean up temp file if it still exists
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except:
                pass

def delete_file(file_path: str):
    """Delete a file from storage (Supabase or Local)"""
    if not file_path:
        return
        
    # Check if it's a Supabase URL
    if supabase and "supabase.co" in file_path:
        try:
            # Extract path from URL
            # URL format: .../storage/v1/object/public/{bucket}/{path/to/file}
            if f"/public/{BUCKET_NAME}/" in file_path:
                file_key = file_path.split(f"/public/{BUCKET_NAME}/")[1]
                supabase.storage.from_(BUCKET_NAME).remove([file_key])
        except Exception as e:
            print(f"Error deleting file from Supabase: {e}")
            pass
            
    # Local file deletion
    else:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass
