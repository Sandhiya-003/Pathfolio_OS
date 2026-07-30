import os
import shutil
import hashlib
from typing import Optional
from app.core.config import settings
from app.core.logger import logger

def save_upload(file_content: bytes, filename: str) -> tuple[str, str]:
    """Save uploaded file and return (file_path, file_hash)"""
    file_hash = hashlib.md5(file_content).hexdigest()
    ext = os.path.splitext(filename)[1]
    safe_filename = f"{file_hash}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    logger.info(f"💾 Saved file: {filename} -> {file_path}")
    return file_path, file_hash

def delete_file(file_path: str) -> bool:
    """Delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Deleted file: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"