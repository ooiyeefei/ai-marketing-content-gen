import os
import httpx
import asyncio
import base64
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MiniMaxService:
    """
    MiniMax API service for image and video generation.

    Features:
    - Text-to-image with subject reference
    - Image-to-video with first frame input
    """

    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY environment variable not set")

        # MiniMax API endpoints - correct base URL from docs
        self.image_url = "https://api.minimax.io/v1/image_generation"
        self.video_url = "https://api.minimax.io/v1/video_generation"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info("✓ MiniMax API initialized")

    # ========================================================================
    # Image Generation
    # ========================================================================

    async def generate_images(
        self,
        prompt: str,
        subject_reference_url: Optional[str] = None,
        num_images: int = 2,
        aspect_ratio: str = "1:1"
    ) -> List[bytes]:
        """
        Generate images from text prompt.

        Args:
            prompt: Image generation prompt
            subject_reference_url: Optional reference image URL (from R2)
            num_images: Number of images to generate (default: 2)
            aspect_ratio: Aspect ratio (default: 1:1 for Instagram)

        Returns:
            List of image bytes
        """
        payload = {
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": num_images,  # Correct parameter name per API docs
            "response_format": "base64"  # Request base64 encoded images
        }

        # Add subject reference if provided (image-to-image)
        if subject_reference_url:
            payload["subject_reference"] = [
                {
                    "type": "character",
                    "image_file": subject_reference_url
                }
            ]

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.image_url,
                    headers=self.headers,
                    json=payload
                )

                # Check for API errors in response body
                result = response.json()

                # MiniMax returns errors in base_resp even with 200 status
                if "base_resp" in result:
                    status_code = result["base_resp"].get("status_code")
                    status_msg = result["base_resp"].get("status_msg")

                    if status_code != 0:
                        error_msg = f"MiniMax API error: status_code {status_code}, {status_msg}"
                        logger.error(f"✗ {error_msg}")
                        raise Exception(error_msg)

                response.raise_for_status()

                # Parse response - handle both response formats
                data = result.get("data", {})

                # Try new format first: data.items[{base64}]
                items = data.get("items", [])
                if items:
                    images = []
                    for item in items:
                        base64_data = item.get("base64")
                        if base64_data:
                            image_bytes = base64.b64decode(base64_data)
                            images.append(image_bytes)
                else:
                    # Fall back to old format: data.image_base64[]
                    base64_list = data.get("image_base64", [])
                    images = [base64.b64decode(b64) for b64 in base64_list if b64]

                logger.info(f"✓ Generated {len(images)} images with MiniMax")
                return images

        except httpx.HTTPStatusError as e:
            logger.error(f"✗ MiniMax HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ MiniMax image generation failed: {e}")
            raise

    # ========================================================================
    # Video Generation (Image-to-Video)
    # ========================================================================

    async def generate_video(
        self,
        motion_prompt: str,
        first_frame_image_url: str,
        duration: int = 6
    ) -> Optional[bytes]:
        """
        Generate video from image with motion prompt.

        Args:
            motion_prompt: Description of desired motion
            first_frame_image_url: R2 URL of source image
            duration: Video duration in seconds (default: 6)

        Returns:
            Video bytes or None if failed
        """
        payload = {
            "model": "video-01",
            "prompt": motion_prompt,
            "first_frame_image": first_frame_image_url,
            "duration": duration
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Submit video generation task
                response = await client.post(
                    self.video_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                task_id = response.json().get("task_id")
                logger.info(f"✓ MiniMax video task created: {task_id}")

                # Poll for completion
                video_bytes = await self._poll_video_task(task_id, max_wait=300)

                return video_bytes

        except Exception as e:
            logger.error(f"✗ MiniMax video generation failed: {e}")
            return None

    async def _poll_video_task(
        self,
        task_id: str,
        max_wait: int = 300
    ) -> Optional[bytes]:
        """
        Poll MiniMax video task until completion.

        Args:
            task_id: MiniMax task ID
            max_wait: Maximum wait time in seconds

        Returns:
            Video bytes or None
        """
        waited = 0

        async with httpx.AsyncClient() as client:
            while waited < max_wait:
                response = await client.get(
                    f"{self.video_url}/tasks/{task_id}",
                    headers=self.headers
                )
                response.raise_for_status()

                status_data = response.json()
                status = status_data.get("status")

                if status == "completed":
                    video_file_url = status_data.get("file_url")

                    # Download video
                    video_response = await client.get(video_file_url)
                    video_response.raise_for_status()

                    logger.info(f"✓ MiniMax video completed: {task_id}")
                    return video_response.content

                elif status == "failed":
                    error = status_data.get("error", "Unknown error")
                    logger.error(f"✗ MiniMax video failed: {error}")
                    return None

                # Still processing
                await asyncio.sleep(10)
                waited += 10

        logger.warning(f"⚠ MiniMax video task {task_id} timed out")
        return None
