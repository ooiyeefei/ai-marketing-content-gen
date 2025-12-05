"""
Vertex AI Service - Image and Video generation with Gemini and Veo
Using the NEW unified Google GenAI SDK
"""

import os
import logging
from typing import List, Optional
import base64
import asyncio
import time
import tempfile

logger = logging.getLogger(__name__)


class VertexService:
    """
    Google GenAI service for:
    - Gemini 3.0 Pro for image generation
    - Veo 3.1 for video generation with image-to-video
    """

    def __init__(self):
        self.google_ai_key = os.getenv("GOOGLE_AI_API_KEY")

        if not self.google_ai_key:
            logger.warning("⚠️  No GOOGLE_AI_API_KEY - generation will use placeholders")
        else:
            logger.info("✅ Vertex AI service initialized (Google GenAI SDK)")

    async def generate_image(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        num_images: int = 2,
        business_context: Optional[dict] = None
    ) -> List[str]:
        """
        Generate images with Gemini 3.0 Pro

        Args:
            prompt: Image generation prompt
            reference_images: Optional reference images for style matching
            aspect_ratio: Aspect ratio (1:1, 16:9, 9:16, 4:3)
            num_images: Number of images to generate
            business_context: Optional business context for better images

        Returns:
            List of image URLs or base64 data
        """
        try:
            if self.google_ai_key:
                return await self._generate_with_genai_sdk(
                    prompt, num_images, business_context
                )
            else:
                return self._generate_placeholder(prompt, num_images)

        except Exception as e:
            logger.error(f"Image generation error: {e}", exc_info=True)
            return self._generate_placeholder(prompt, num_images)

    async def _generate_with_genai_sdk(
        self,
        prompt: str,
        num_images: int,
        business_context: Optional[dict] = None
    ) -> List[str]:
        """
        Generate images using NEW Google GenAI SDK with Gemini 3.0 Pro

        High-quality image generation for professional social media content
        """
        try:
            from google import genai

            # Create client with NEW SDK
            client = genai.Client(api_key=self.google_ai_key)

            # Build rich context prompt
            full_prompt = prompt
            if business_context:
                context_info = f"""
Business Context:
- Name: {business_context.get('business_name', 'Unknown')}
- Industry: {business_context.get('industry', 'General')}
- Description: {business_context.get('description', '')}
- Target Audience: {business_context.get('target_audience', 'General audience')}

Create a professional social media image for: {prompt}

Style Requirements:
- Match the business's industry aesthetic
- Professional social media format (Instagram-ready)
- Eye-catching, scroll-stopping design
- Brand-appropriate visual elements
"""
                full_prompt = context_info
            else:
                full_prompt = f"Create a professional social media image: {prompt}"

            # Generate multiple images
            image_urls = []
            for i in range(num_images):
                try:
                    logger.info(f"🎨 Generating image {i+1}/{num_images} with Gemini 3.0...")

                    # Use NEW SDK to generate image with Gemini 3.0
                    response = client.models.generate_content(
                        model="gemini-3-pro-preview",
                        contents=full_prompt,
                        config={"response_modalities": ['IMAGE']}
                    )

                    # Extract image from response
                    if not response.parts:
                        logger.warning(f"Image {i+1}: No parts in response")
                        continue

                    logger.info(f"Image {i+1}: Response has {len(response.parts)} parts")

                    for part_idx, part in enumerate(response.parts):
                        try:
                            # Check if part has image data
                            if not hasattr(part, 'as_image'):
                                logger.warning(f"Image {i+1}, Part {part_idx}: No as_image() method")
                                continue

                            # Convert to PIL Image and then to base64
                            pil_image = part.as_image()

                            if not pil_image:
                                logger.warning(f"Image {i+1}, Part {part_idx}: as_image() returned None")
                                continue

                            # Save to temporary file
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                pil_image.save(tmp.name)  # Format inferred from extension

                                # Read back as base64
                                with open(tmp.name, 'rb') as f:
                                    image_data = f.read()
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    data_url = f"data:image/png;base64,{image_base64}"
                                    image_urls.append(data_url)

                                    logger.info(f"✅ Generated image {i+1}/{num_images} with Gemini 3.0")
                                    break
                        except Exception as part_error:
                            logger.warning(f"Image {i+1}, Part {part_idx}: {part_error}")
                            continue

                except Exception as e:
                    logger.warning(f"Failed to generate image {i+1}: {e}", exc_info=True)
                    continue

            if not image_urls:
                logger.warning("No images generated, using placeholders")
                return self._generate_placeholder(prompt, num_images)

            return image_urls

        except Exception as e:
            logger.error(f"Gemini 3.0 image generation error: {e}", exc_info=True)
            return self._generate_placeholder(prompt, num_images)

    def _generate_placeholder(self, prompt: str, num_images: int) -> List[str]:
        """Generate placeholder images for testing"""
        import urllib.parse

        placeholders = []
        for i in range(num_images):
            # Use placeholder.co service
            text = urllib.parse.quote(f"Image {i+1}: {prompt[:30]}")
            url = f"https://placehold.co/600x600/4285F4/white?text={text}"
            placeholders.append(url)

        logger.info(f"📷 Generated {num_images} placeholder images")
        return placeholders

    async def generate_video(
        self,
        prompt: str,
        product_images: Optional[List[str]] = None,
        duration_seconds: int = 8,
        aspect_ratio: str = "9:16"
    ) -> Optional[str]:
        """
        Generate video with Veo 3.1 using IMAGE-TO-VIDEO

        Uses NEW Google GenAI SDK with proper flow:
        1. Generate image with Gemini 3.0 Pro
        2. Convert image to video with Veo 3.1
        3. Poll for completion
        4. Download video

        Args:
            prompt: Video generation prompt
            product_images: Business product images (will be enhanced by Gemini first)
            duration_seconds: Video duration (8 seconds for demo)
            aspect_ratio: Aspect ratio (16:9, 9:16)

        Returns:
            Video URL or None
        """
        if not self.google_ai_key:
            logger.warning("⚠️  No API key - skipping video generation")
            return None

        try:
            from google import genai

            # Create client with NEW SDK
            client = genai.Client(api_key=self.google_ai_key)

            logger.info("🎬 Starting Veo 3.1 video generation with image-to-video...")

            # Step 1: Generate image with Gemini 3.0
            logger.info(f"📸 Step 1: Generating image with Gemini 3.0...")

            image_prompt = f"Create a professional product image for video: {prompt}"
            image_response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=image_prompt,
                config={"response_modalities": ['IMAGE']}
            )

            if not image_response.parts:
                logger.error("No image generated for video")
                return None

            # Get the generated image
            generated_image = image_response.parts[0].as_image()
            logger.info(f"✅ Image generated successfully")

            # Step 2: Generate video with Veo 3.1 using the image
            logger.info(f"🎥 Step 2: Generating video with Veo 3.1...")

            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                image=generated_image,
                config={
                    "aspect_ratio": aspect_ratio,
                    "duration_seconds": duration_seconds
                }
            )

            # Step 3: Poll for completion
            logger.info("⏳ Step 3: Waiting for video generation to complete...")

            max_wait = 180  # 3 minutes
            waited = 0
            poll_interval = 10

            while waited < max_wait:
                try:
                    # Get operation status
                    operation = client.operations.get(operation)

                    if operation.done:
                        logger.info("✅ Video generation complete!")

                        # Step 4: Download video
                        video = operation.response.generated_videos[0]

                        # Download to temporary file
                        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                            client.files.download(file=video.video)
                            video.video.save(tmp.name)

                            # Read as base64
                            with open(tmp.name, 'rb') as f:
                                video_data = f.read()
                                video_base64 = base64.b64encode(video_data).decode('utf-8')
                                video_data_url = f"data:video/mp4;base64,{video_base64}"

                                logger.info(f"✅ Video generated successfully: {len(video_data)} bytes")
                                return video_data_url

                    # Wait before polling again
                    await asyncio.sleep(poll_interval)
                    waited += poll_interval
                    logger.info(f"⏳ Video generation progress... ({waited}/{max_wait}s)")

                except Exception as poll_error:
                    logger.warning(f"Polling error: {poll_error}")
                    await asyncio.sleep(poll_interval)
                    waited += poll_interval

            logger.warning("⏰ Video generation timed out")
            return None

        except Exception as e:
            logger.error(f"Veo 3.1 video generation error: {e}", exc_info=True)
            return None


# Global instance
_vertex_service = None


def get_vertex_service() -> VertexService:
    """Get or create Vertex service instance"""
    global _vertex_service
    if _vertex_service is None:
        _vertex_service = VertexService()
    return _vertex_service
