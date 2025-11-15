import logging
import uuid
from typing import Optional
from google.cloud import storage
from config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for uploading generated content to Google Cloud Storage"""

    def __init__(self):
        """Initialize GCS client"""
        try:
            self.client = storage.Client(project=settings.project_id)
            self.bucket_name = settings.storage_bucket

            if not self.bucket_name:
                logger.warning("Storage bucket not configured in settings")
                self.bucket = None
            else:
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"Storage service initialized with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Storage client: {e}")
            self.client = None
            self.bucket = None

    def upload_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        job_id: str = "",
        day: int = 0,
        segment_number: int = 0
    ) -> Optional[str]:
        """
        Upload image to GCS and return public URL.

        Args:
            image_bytes: Image data as bytes
            mime_type: MIME type of the image
            job_id: Generation job ID (for organizing files)
            day: Day number (for organizing files)
            segment_number: Image segment number

        Returns:
            Public GCS URL or None if upload fails
        """
        if not self.bucket:
            logger.warning("Storage bucket not configured, cannot upload image")
            return None

        try:
            # Generate unique filename with organization
            file_extension = mime_type.split('/')[-1]  # jpeg, png, etc.
            filename = f"generated/{job_id}/day-{day}/image-{segment_number}.{file_extension}"

            # Create blob and upload
            blob = self.bucket.blob(filename)
            blob.upload_from_string(
                image_bytes,
                content_type=mime_type
            )

            # Return public URL (bucket must be configured for public access via IAM)
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{filename}"
            logger.info(f"Uploaded image to GCS: {filename} ({len(image_bytes)} bytes)")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading image to GCS: {e}")
            return None

    def upload_video(
        self,
        video_bytes: bytes,
        mime_type: str = "video/mp4",
        job_id: str = "",
        day: int = 0,
        segment_number: int = 0
    ) -> Optional[str]:
        """
        Upload video to GCS and return public URL.

        Args:
            video_bytes: Video data as bytes
            mime_type: MIME type of the video
            job_id: Generation job ID (for organizing files)
            day: Day number (for organizing files)
            segment_number: Video segment number

        Returns:
            Public GCS URL or None if upload fails
        """
        if not self.bucket:
            logger.warning("Storage bucket not configured, cannot upload video")
            return None

        try:
            # Generate unique filename with organization
            file_extension = mime_type.split('/')[-1]  # mp4, etc.
            filename = f"generated/{job_id}/day-{day}/video-{segment_number}.{file_extension}"

            # Create blob and upload
            blob = self.bucket.blob(filename)
            blob.upload_from_string(
                video_bytes,
                content_type=mime_type
            )

            # Return public URL (bucket must be configured for public access via IAM)
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{filename}"
            logger.info(f"Uploaded video to GCS: {filename} ({len(video_bytes)} bytes)")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading video to GCS: {e}")
            return None
