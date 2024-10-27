import boto3
from datetime import datetime, timedelta
from ..config.settings import get_settings
from botocore.exceptions import ClientError
import logging

settings = get_settings()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region 
        )
        self.bucket_name = settings.s3_bucket_name

        # print(f"Initialized S3 client with bucket: {self.bucket_name}")
        # print(f"s3_client: {settings.aws_access_key}")

    def upload_image(self, image_bytes):
        try:
            # Generate filename with timestamp
            filename = f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{datetime.now().timestamp()}.jpg"
            
            # Calculate expiry date (2 days from now)
            expiry_date = datetime.now() + timedelta(days=2)
            
            # Upload to S3 with metadata
            self.s3_client.upload_fileobj(
                image_bytes,
                self.bucket_name,
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

            # Generate presigned URL (optional, if you want temporary URLs)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': filename
                },
                ExpiresIn=86400  # 1 days in seconds
            )

            return {
                'url': f"https://{self.bucket_name}.s3.amazonaws.com/{filename}",
                'presigned_url': url,
                'expiry_date': expiry_date.isoformat()
            }

        except ClientError as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            raise Exception("Failed to upload image to S3")

    def delete_image(self, filename):
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except ClientError as e:
            logging.error(f"Error deleting from S3: {str(e)}")
            return False