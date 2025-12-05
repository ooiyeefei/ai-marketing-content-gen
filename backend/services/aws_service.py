"""
AWS Service - S3 storage for generated assets
"""

import os
import logging
from typing import Optional
import io
import base64
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class AWSService:
    """
    AWS service for:
    - S3 asset storage (images, videos)
    - CloudFront CDN (optional)
    """

    def __init__(self):
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket = os.getenv("AWS_S3_BUCKET", "brandmind-assets")
        self.presigned_url_expiration = int(os.getenv("AWS_PRESIGNED_URL_EXPIRATION", "604800"))  # 7 days default

        self.s3_client = None

        if self.access_key and self.secret_key:
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                logger.info(f"✅ AWS S3 service initialized (bucket: {self.bucket})")
            except Exception as e:
                logger.warning(f"⚠️  AWS S3 initialization failed: {e}")
        else:
            logger.warning("⚠️  AWS credentials not set - using local storage")

    def upload_image(
        self,
        image_data: str,
        campaign_id: str,
        day: int,
        image_type: str = "image"
    ) -> str:
        """
        Upload image to S3

        Args:
            image_data: Base64 image data or URL
            campaign_id: Campaign ID for organization
            day: Day number (1-7)
            image_type: Type of image (image, product, etc.)

        Returns:
            S3 URL or local path
        """
        try:
            # Handle placeholder URLs
            if image_data.startswith("http"):
                logger.info(f"Image already has URL: {image_data}")
                return image_data

            # Handle base64 data
            if image_data.startswith("data:image"):
                # Extract base64 part
                image_data = image_data.split(",")[1]

            # Decode base64
            image_bytes = base64.b64decode(image_data)

            # Generate unique filename
            filename = f"{campaign_id}/day{day}_{image_type}_{datetime.now().strftime('%H%M%S')}.jpg"

            if self.s3_client:
                return self._upload_to_s3(image_bytes, filename)
            else:
                return self._save_locally(image_bytes, filename)

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            # Return original data as fallback
            return image_data

    def upload_video(
        self,
        video_path: str,
        campaign_id: str,
        day: int
    ) -> str:
        """
        Upload video to S3

        Args:
            video_path: Local video file path or GCS URI
            campaign_id: Campaign ID
            day: Day number

        Returns:
            S3 URL or local path
        """
        try:
            # Handle GCS URIs
            if video_path.startswith("gs://"):
                logger.info(f"Video on GCS: {video_path}")
                return video_path

            # Read video file
            with open(video_path, "rb") as f:
                video_bytes = f.read()

            filename = f"{campaign_id}/day{day}_video_{datetime.now().strftime('%H%M%S')}.mp4"

            if self.s3_client:
                return self._upload_to_s3(
                    video_bytes,
                    filename,
                    content_type="video/mp4"
                )
            else:
                return self._save_locally(video_bytes, filename)

        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return video_path

    def _upload_to_s3(
        self,
        file_bytes: bytes,
        key: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """Upload file to S3 bucket and return presigned URL"""
        try:
            # Upload to private bucket (no public ACL)
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type
                # No ACL - bucket remains private
            )

            # Generate presigned URL with configurable expiration
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': key
                },
                ExpiresIn=self.presigned_url_expiration
            )

            days = self.presigned_url_expiration // 86400
            logger.info(f"✅ Uploaded to S3 (private): {key}")
            logger.info(f"🔒 Generated presigned URL (expires in {days} days)")
            return presigned_url

        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            # Fallback to local storage
            return self._save_locally(file_bytes, key)

    def _save_locally(self, file_bytes: bytes, filename: str) -> str:
        """Save file locally as fallback"""
        try:
            # Create local storage directory
            local_dir = "/tmp/brandmind_assets"
            os.makedirs(local_dir, exist_ok=True)

            # Save file
            local_path = os.path.join(local_dir, filename.replace("/", "_"))
            with open(local_path, "wb") as f:
                f.write(file_bytes)

            logger.info(f"💾 Saved locally: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Local save error: {e}")
            return f"error_{filename}"

    def get_presigned_url(self, key: str, expiration: int = None) -> str:
        """
        Generate presigned URL for private S3 object

        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default: from config)

        Returns:
            Presigned URL
        """
        if self.s3_client:
            try:
                # Use configured expiration if not specified
                if expiration is None:
                    expiration = self.presigned_url_expiration

                presigned_url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket,
                        'Key': key
                    },
                    ExpiresIn=expiration
                )
                return presigned_url
            except Exception as e:
                logger.error(f"Error generating presigned URL: {e}")
                return f"/tmp/brandmind_assets/{key.replace('/', '_')}"
        else:
            return f"/tmp/brandmind_assets/{key.replace('/', '_')}"

    def delete_campaign_assets(self, campaign_id: str) -> bool:
        """Delete all assets for a campaign"""
        try:
            if not self.s3_client:
                return False

            # List objects with campaign prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=f"{campaign_id}/"
            )

            if 'Contents' not in response:
                return True

            # Delete objects
            objects = [{'Key': obj['Key']} for obj in response['Contents']]
            self.s3_client.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': objects}
            )

            logger.info(f"🗑️  Deleted {len(objects)} assets for campaign {campaign_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting campaign assets: {e}")
            return False


# Global instance
_aws_service = None


def get_aws_service() -> AWSService:
    """Get or create AWS service instance"""
    global _aws_service
    if _aws_service is None:
        _aws_service = AWSService()
    return _aws_service
