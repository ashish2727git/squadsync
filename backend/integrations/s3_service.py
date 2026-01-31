"""
AWS S3 Integration for file uploads
"""
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import uuid

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.cloudfront_domain = os.getenv('AWS_CLOUDFRONT_DOMAIN')

    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "uploads"
    ) -> dict:
        """
        Upload file to S3 and return URL
        
        Args:
            file: File to upload
            folder: S3 folder (e.g., 'avatars', 'squad-logos')
            
        Returns:
            dict with 'url' and 'key'
        """
        try:
            # Generate unique filename
            file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())
            s3_key = f"{folder}/{unique_filename}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'public-read'
                }
            )
            
            # Generate URL
            if self.cloudfront_domain:
                url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return {
                'url': url,
                'key': s3_key,
                'filename': file.filename
            }
            
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")

    async def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False

    async def get_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL for private files"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

# Global instance
s3_service = S3Service()
