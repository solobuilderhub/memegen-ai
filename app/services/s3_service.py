import boto3
from datetime import datetime, timedelta
from functools import lru_cache
from ..config.settings import get_settings
from botocore.exceptions import ClientError
import logging
from typing import Dict, Optional

settings = get_settings()

# Cache the client creation
@lru_cache()
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_key,
        region_name=settings.aws_region 
    )

class S3Service:
    @staticmethod
    def upload_image(image_bytes: bytes) -> Dict:
        s3_client = get_s3_client()
        bucket_name = settings.s3_bucket_name
        
        try:
            filename = f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{datetime.now().timestamp()}.jpg"
            expiry_date = datetime.now() + timedelta(days=2)
            
            s3_client.upload_fileobj(
                image_bytes,
                bucket_name,
                filename,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'Metadata': {
                        'expiry-date': expiry_date.isoformat(),
                        'content-type': 'meme-image'
                    },
                    'CacheControl': 'max-age=172800'  # 2 days in seconds
                }
            )

            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': filename
                },
                ExpiresIn=86400  # 1 day in seconds
            )

            return {
                'url': f"https://{bucket_name}.s3.amazonaws.com/{filename}",
                'presigned_url': url,
                'expiry_date': expiry_date.isoformat()
            }

        except ClientError as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            raise Exception("Failed to upload image to S3")

    @staticmethod
    def delete_image(filename: str) -> bool:
        s3_client = get_s3_client()
        bucket_name = settings.s3_bucket_name
        
        try:
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=filename
            )
            return True
        except ClientError as e:
            logging.error(f"Error deleting from S3: {str(e)}")
            return False

    @staticmethod
    def get_image_url(filename: str, expiry: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for an existing image
        Args:
            filename: The key of the file in S3
            expiry: URL expiration time in seconds (default 1 hour)
        """
        s3_client = get_s3_client()
        bucket_name = settings.s3_bucket_name
        
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': filename
                },
                ExpiresIn=expiry
            )
            return url
        except ClientError as e:
            logging.error(f"Error generating presigned URL: {str(e)}")
            return None