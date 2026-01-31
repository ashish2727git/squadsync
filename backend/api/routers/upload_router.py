"""
File upload router for avatars, squad logos, and attachments
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
from backend.core.dependencies import get_current_user
from backend.models.models import User
from backend.integrations.s3_service import s3_service
import os

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload user avatar"""
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only images allowed (JPEG, PNG, GIF, WebP)"
        )
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max 5MB"
        )
    
    # Check if AWS is configured
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File upload not configured"
        )
    
    try:
        # Upload to S3
        result = await s3_service.upload_file(file, folder="avatars")
        
        # Update user avatar in database
        from backend.core.dependencies import get_db_session
        async for db in get_db_session():
            current_user.avatar_url = result['url']
            db.add(current_user)
            await db.commit()
            break
        
        return {
            "success": True,
            "avatar_url": result['url'],
            "message": "Avatar updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/squad-logo/{squad_id}")
async def upload_squad_logo(
    squad_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload squad logo"""
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only images allowed (JPEG, PNG, GIF, WebP)"
        )
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max 5MB"
        )
    
    # Check if AWS is configured
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File upload not configured"
        )
    
    try:
        # Upload to S3
        result = await s3_service.upload_file(file, folder="squad-logos")
        
        # Update squad logo in database
        from backend.core.dependencies import get_db_session
        from backend.models.models import Squad
        from sqlalchemy import select
        import uuid
        
        async for db in get_db_session():
            squad = await db.get(Squad, uuid.UUID(squad_id))
            if not squad:
                raise HTTPException(status_code=404, detail="Squad not found")
            
            squad.logo_url = result['url']
            db.add(squad)
            await db.commit()
            break
        
        return {
            "success": True,
            "logo_url": result['url'],
            "message": "Squad logo updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload file attachment (for chat, vault, etc.)"""
    
    MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_ATTACHMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max 10MB"
        )
    
    # Check if AWS is configured
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File upload not configured"
        )
    
    try:
        # Upload to S3
        result = await s3_service.upload_file(file, folder="attachments")
        
        return {
            "success": True,
            "file_url": result['url'],
            "file_name": result['filename'],
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.delete("/file")
async def delete_file(
    file_key: str,
    current_user: User = Depends(get_current_user)
):
    """Delete file from S3"""
    
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File upload not configured"
        )
    
    try:
        success = await s3_service.delete_file(file_key)
        
        if success:
            return {
                "success": True,
                "message": "File deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )
