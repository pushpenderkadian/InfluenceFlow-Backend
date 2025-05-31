import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any
import logging
import uuid
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        
        try:
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=self.region
                )
                logger.info("S3 client initialized successfully")
            else:
                self.s3_client = None
                logger.warning("AWS credentials not found, using mock mode")
        except Exception as e:
            self.s3_client = None
            logger.error(f"Failed to initialize S3 client: {e}")
    
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
        folder: str = "uploads"
    ) -> Optional[str]:
        """Upload file to S3 and return the URL"""
        try:
            if not self.s3_client:
                # Mock mode - return a fake URL
                mock_url = f"https://mock-s3-bucket.com/{folder}/{file_name}"
                logger.info(f"Mock file upload: {mock_url}")
                return mock_url
            
            # Generate unique filename
            unique_filename = f"{folder}/{uuid.uuid4()}_{file_name}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type,
                ACL='private'  # Private by default, use presigned URLs for access
            )
            
            # Return the S3 URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}"
            logger.info(f"File uploaded successfully: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            return None
    
    async def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> Optional[str]:
        """Generate a presigned URL for S3 object access"""
        try:
            if not self.s3_client:
                # Mock mode
                mock_url = f"https://mock-s3-bucket.com/presigned/{object_key}?expires={expiration}"
                logger.info(f"Mock presigned URL: {mock_url}")
                return mock_url
            
            url = self.s3_client.generate_presigned_url(
                http_method,
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Presigned URL generated for {object_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    async def generate_presigned_post(
        self,
        object_key: str,
        expiration: int = 3600,
        max_file_size: int = 10485760  # 10MB default
    ) -> Optional[Dict[str, Any]]:
        """Generate presigned POST data for direct upload from frontend"""
        try:
            if not self.s3_client:
                # Mock mode
                mock_data = {
                    "url": f"https://mock-s3-bucket.com",
                    "fields": {
                        "key": object_key,
                        "AWSAccessKeyId": "mock-key",
                        "policy": "mock-policy",
                        "signature": "mock-signature"
                    }
                }
                logger.info(f"Mock presigned POST data: {mock_data}")
                return mock_data
            
            conditions = [
                ["content-length-range", 1, max_file_size]
            ]
            
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=object_key,
                ExpiresIn=expiration,
                Conditions=conditions
            )
            
            logger.info(f"Presigned POST data generated for {object_key}")
            return response
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned POST: {e}")
            return None
    
    async def delete_file(self, object_key: str) -> bool:
        """Delete file from S3"""
        try:
            if not self.s3_client:
                logger.info(f"Mock file deletion: {object_key}")
                return True
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"File deleted successfully: {object_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
    
    def extract_key_from_url(self, url: str) -> Optional[str]:
        """Extract S3 object key from URL"""
        try:
            if f"{self.bucket_name}.s3" in url:
                # Extract key from S3 URL
                parts = url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")
                if len(parts) == 2:
                    return parts[1]
            return None
        except Exception as e:
            logger.error(f"Failed to extract key from URL: {e}")
            return None

# Global instance
s3_service = S3Service()