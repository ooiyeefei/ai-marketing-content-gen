import os
import asyncio
import boto3
from botocore.client import Config
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class R2Service:
    """
    Cloudflare R2 object storage service (S3-compatible).
    Stores all media files: research images, customer photos, generated images/videos.
    """

    def __init__(self):
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket = os.getenv("R2_BUCKET", "superscrat")

        if not all([account_id, access_key, secret_key]):
            raise ValueError("Missing R2 credentials in environment variables")

        # Configure S3-compatible client for R2
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )

        self.public_url_base = f"https://pub-{account_id}.r2.dev"
        logger.info(f"Connected to R2 bucket: {self.bucket}")

    async def upload_bytes(
        self,
        data: bytes,
        object_key: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Upload bytes to R2 and return public URL.

        Args:
            data: File bytes
            object_key: Path in bucket (e.g., "campaigns/xyz/day_1.jpg")
            content_type: MIME type

        Returns:
            Public R2 URL
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.upload_fileobj(
                    BytesIO(data),
                    self.bucket,
                    object_key,
                    ExtraArgs={"ContentType": content_type}
                )
            )

            public_url = f"{self.public_url_base}/{object_key}"
            logger.info(f"Uploaded to R2: {object_key}")
            return public_url

        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            raise

    async def upload_from_url(
        self,
        source_url: str,
        object_key: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Download from URL and upload to R2.

        Args:
            source_url: URL to download from
            object_key: Path in R2 bucket
            content_type: MIME type

        Returns:
            Public R2 URL
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(source_url)
                response.raise_for_status()

                return await self.upload_bytes(
                    response.content,
                    object_key,
                    content_type
                )

        except Exception as e:
            logger.error(f"Failed to upload from URL: {e}")
            raise

    def get_campaign_path(self, campaign_id: str, filename: str) -> str:
        """
        Generate object key for campaign file.

        Example: campaigns/xyz/research/competitor_1.jpg
        """
        return f"campaigns/{campaign_id}/{filename}"
