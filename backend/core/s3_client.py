"""
AWS S3 Integration
Handles file uploads to S3 for avatars, attachments, and media.
"""

import logging
from typing import Optional
from uuid import UUID, uuid4

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile

from backend.core.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_BUCKET,
    AWS_SECRET_ACCESS_KEY,
)

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 client for file operations."""

    def __init__(self):
        """Initialize S3 client."""
        self._s3_client = None
        self._bucket_name = AWS_S3_BUCKET
        self._region = AWS_REGION

    def _get_client(self):
        """Get or create S3 client."""
        if self._s3_client is None:
            try:
                self._s3_client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=self._region,
                )
                logger.info("✅ S3 client initialized")
            except NoCredentialsError:
                logger.error("❌ AWS credentials not found")
                raise
        return self._s3_client

    async def upload_file(
        self,
        file: UploadFile,
        user_id: UUID,
        file_type: str = "general",
    ) -> Optional[str]:
        """
        Upload file to S3.

        Args:
            file: File to upload
            user_id: User ID for organizing files
            file_type: Type of file (avatar, attachment, media)

        Returns:
            S3 URL of uploaded file, or None if upload failed
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
            unique_filename = f"{user_id}/{file_type}/{uuid4()}.{file_extension}"

            # Read file content
            content = await file.read()

            # Upload to S3
            s3_client = self._get_client()
            s3_client.put_object(
                Bucket=self._bucket_name,
                Key=unique_filename,
                Body=content,
                ContentType=file.content_type or "application/octet-stream",
            )

            # Generate public URL
            url = f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{unique_filename}"
            logger.info(f"✅ File uploaded to S3: {url}")
            return url

        except ClientError as e:
            logger.error(f"❌ S3 upload error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during S3 upload: {e}")
            return None

    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3.

        Args:
            file_url: S3 URL of file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Extract key from URL
            key = file_url.split(f"{self._bucket_name}.s3.{self._region}.amazonaws.com/")[-1]

            # Delete from S3
            s3_client = self._get_client()
            s3_client.delete_object(Bucket=self._bucket_name, Key=key)

            logger.info(f"✅ File deleted from S3: {key}")
            return True

        except ClientError as e:
            logger.error(f"❌ S3 delete error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during S3 delete: {e}")
            return False

    async def get_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
    ) -> Optional[str]:
        """
        Generate presigned URL for temporary access.

        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL, or None if generation failed
        """
        try:
            s3_client = self._get_client()
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': file_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"❌ Presigned URL generation error: {e}")
            return None


# Global S3 client instance
_s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """Get global S3 client instance."""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client
