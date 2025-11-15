import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # GCP Configuration
    project_id: str = Field(default="", validation_alias="GCP_PROJECT_ID")
    region: str = Field(default="us-central1", validation_alias="GCP_REGION")
    storage_bucket: str = Field(default="", validation_alias="STORAGE_BUCKET")

    # API Keys (from Secret Manager in production)
    google_maps_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_MAPS_API_KEY")

    # Content Limits (optimized for demo and cost control)
    max_videos_per_post: int = 1  # Max video segments per post (reduced to prevent quota exhaustion)
    max_images_per_post: int = 3  # Max image generations per post

    # Video Settings (optimized for demo)
    video_duration_seconds: int = 5  # Reduced from 8 to 5 seconds per segment
    video_resolution: str = "720p"  # Required for extension (cannot be changed)

    # Cost Control Flags
    # Set to "true" to enable actual API calls for content generation
    # Set to "false" to use placeholder URIs (recommended for development)
    enable_video_generation: bool = Field(
        default=False,
        validation_alias="ENABLE_VIDEOS",
        description="Enable video generation via Veo 2.0"
    )
    enable_image_generation: bool = Field(
        default=False,
        validation_alias="ENABLE_IMAGES",
        description="Enable image generation via Imagen 3"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton settings instance
settings = Settings()
