import logging
from typing import Dict, List, Optional
import re
import time
import uuid
import httpx
import base64
from google import genai
from google.genai import types as genai_types
from config import settings
from models import ContentPost, VideoSegment, ImageSegment
from services.google_services import GoogleServicesClient
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class CreativeProducerAgent:
    """
    Agent 3: Generates captions, images, and videos for social media posts.
    Uses Gemini for captions, Gemini native image generation for images,
    and Veo for video generation with extension.
    """

    def __init__(self):
        self.genai_client = genai.Client(
            vertexai=True,
            project=settings.project_id,
            location=settings.region
        )
        self.google_services = GoogleServicesClient()
        self.storage_service = StorageService()

    async def produce_content(
        self,
        calendar: List[Dict],
        business_profile: Dict,
        job_id: str = ""
    ) -> List[ContentPost]:
        """
        Generate complete content (captions + videos) for all posts.

        Args:
            calendar: 7-day content calendar from Agent 2
            business_profile: Business profile from Agent 1

        Returns:
            List of ContentPost objects with captions and video segments
        """
        logger.info("Creative Producer Agent: Producing content for 7 posts...")
        logger.info(f"Video generation: {'ENABLED' if settings.enable_video_generation else 'DISABLED (using placeholders)'}")
        logger.info(f"Image generation: {'ENABLED' if settings.enable_image_generation else 'DISABLED (using placeholders)'}")

        posts = []

        for post_plan in calendar:
            logger.info(f"Producing content for Day {post_plan['day']}")

            # Generate caption
            caption = await self._generate_caption(post_plan, business_profile)

            # Extract hashtags from caption
            hashtags = self._extract_hashtags(caption)

            # Generate videos (or placeholders if disabled)
            video_segments = await self._generate_videos(
                post_plan.get('video_prompts', []),
                business_profile,
                job_id=job_id,
                day=post_plan['day']
            )

            # Generate images (or placeholders if disabled)
            image_segments = await self._generate_images(
                post_plan.get('image_prompts', []),
                business_profile,
                job_id=job_id,
                day=post_plan['day']
            )

            # Calculate total duration
            total_duration = sum(seg.duration_seconds for seg in video_segments)

            post = ContentPost(
                day=post_plan['day'],
                platform=post_plan.get('platform', 'instagram'),
                caption=caption,
                video_segments=video_segments,
                image_segments=image_segments,
                total_duration_seconds=total_duration,
                hashtags=hashtags
            )

            posts.append(post)

        logger.info("Creative Producer Agent: Content production complete")
        return posts

    async def _generate_caption(
        self,
        post_plan: Dict,
        business_profile: Dict
    ) -> str:
        """Generate platform-optimized caption with Gemini"""
        try:
            business_name = business_profile.get('business_name', 'us')
            brand_voice = business_profile.get('brand_voice', 'professional')

            prompt = f"""Write an engaging {post_plan.get('platform', 'instagram')} caption for this post:

Concept: {post_plan.get('concept', 'business content')}
Theme: {post_plan.get('caption_theme', 'general')}
Brand Voice: {brand_voice}
CTA: {post_plan.get('cta', 'Learn more')}
Business: {business_name}

Requirements:
- 2-3 sentences maximum
- Include 3-5 relevant hashtags
- Match {brand_voice} tone
- Include the CTA naturally
- Engaging and authentic

Return ONLY the caption text with hashtags."""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.8,
                )
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return f"Check out what's happening at {business_name}! {post_plan.get('cta', 'Visit us today')} #business #local"

    def _extract_hashtags(self, caption: str) -> List[str]:
        """Extract hashtags from caption"""
        hashtags = re.findall(r'#\w+', caption)
        return hashtags

    async def _fetch_and_encode_image(self, url: str) -> Optional[str]:
        """
        Download image from URL and convert to base64 for Imagen reference.

        Args:
            url: Image URL to download

        Returns:
            Base64-encoded image string or None if download fails
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Downloading reference image: {url}")
                response = await client.get(url)

                if response.status_code != 200:
                    logger.error(f"Failed to download image: HTTP {response.status_code}")
                    return None

                # Encode to base64
                encoded = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"Successfully encoded reference image ({len(response.content)} bytes)")
                return encoded

        except httpx.TimeoutException:
            logger.error("Image download timed out after 30s")
            return None
        except Exception as e:
            logger.error(f"Error downloading/encoding image: {e}")
            return None

    async def _generate_videos(
        self,
        video_prompts: List[str],
        business_profile: Dict,
        job_id: str = "",
        day: int = 0
    ) -> List[VideoSegment]:
        """
        Generate video segments using Veo 2.0 with extension.
        If video generation is disabled, returns placeholder segments.

        Process:
        1. Generate first segment with optional business photo reference
        2. For subsequent segments, use previous Video object for extension
        3. Veo uses last frame for seamless continuation

        Args:
            video_prompts: List of video generation prompts
            business_profile: Business profile including photos
            job_id: Job ID for organizing files in GCS
            day: Day number for organizing files
        """
        if not video_prompts:
            return []

        # Check if video generation is disabled
        if not settings.enable_video_generation:
            logger.info(f"Video generation DISABLED - creating {len(video_prompts)} placeholder segments")
            placeholders = []
            for i, prompt in enumerate(video_prompts, 1):
                placeholders.append(VideoSegment(
                    segment_number=i,
                    uri=f"placeholder://video-segment-{i}",
                    duration_seconds=settings.video_duration_seconds,
                    prompt_used=prompt
                ))
            return placeholders

        logger.info(f"Generating {len(video_prompts)} video segments with Veo")

        # Prepare reference image from business photos (if available)
        reference_image_base64 = None
        business_photos = business_profile.get('photos', [])

        if business_photos and len(business_photos) > 0:
            logger.info("Attempting to use business photo as style reference")
            # Use the first photo as style reference
            first_photo_url = business_photos[0].get('url')
            if first_photo_url:
                reference_image_base64 = await self._fetch_and_encode_image(first_photo_url)
                if reference_image_base64:
                    logger.info("Successfully prepared business photo as style reference")
                else:
                    logger.warning("Failed to encode business photo, proceeding without reference")
        else:
            logger.info("No business photos available, generating without style reference")

        segments = []
        previous_video_gcs_uri = None  # Store GCS URI (gs://) for video extension

        for i, prompt in enumerate(video_prompts, 1):
            logger.info(f"Generating segment {i}/{len(video_prompts)}")

            try:
                # Only use reference image for first segment
                ref_image = reference_image_base64 if i == 1 else None

                # Generate video segment (following official docs)
                result = await self._generate_single_video_segment(
                    prompt=prompt,
                    segment_number=i,
                    previous_video_gcs_uri=previous_video_gcs_uri,  # Pass GCS URI for extension
                    business_context=business_profile.get('business_name', ''),
                    reference_image_base64=ref_image,
                    job_id=job_id,
                    day=day
                )

                if result and result.get('uri'):
                    segment = VideoSegment(
                        segment_number=i,
                        uri=result['uri'],  # Public HTTP URL for frontend
                        duration_seconds=settings.video_duration_seconds,
                        prompt_used=prompt
                    )
                    segments.append(segment)
                    # Store GCS URI for next segment extension
                    previous_video_gcs_uri = result.get('gcs_uri')
                    logger.info(f"Segment {i} completed. Will extend from: {previous_video_gcs_uri}")
                else:
                    logger.warning(f"Failed to generate segment {i}")
                    # Don't continue to next segment if this one failed
                    break

            except Exception as e:
                logger.error(f"Error generating segment {i}: {e}")
                break

        return segments

    async def _generate_single_video_segment(
        self,
        prompt: str,
        segment_number: int,
        previous_video_gcs_uri: Optional[str] = None,
        business_context: str = "",
        reference_image_base64: Optional[str] = None,
        job_id: str = "",
        day: int = 0
    ) -> Dict:
        """
        Generate single video segment with Veo 2.0 following official Google Cloud documentation.

        Args:
            prompt: Visual prompt for video generation
            segment_number: Segment number (for file naming)
            previous_video_gcs_uri: GCS URI (gs://bucket/path) of previous video for extension
            business_context: Business name/context
            reference_image_base64: Base64-encoded reference image for first frame
            job_id: Job ID for organizing files in GCS
            day: Day number for organizing files

        Returns:
            Dict with 'uri' (public URL) and 'gcs_uri' (gs:// path) keys or None
        """
        try:
            import asyncio
            from google.genai import types as genai_types
            from google.genai.types import Video

            # Enhance prompt with business context
            full_prompt = prompt
            if business_context:
                full_prompt = f"{business_context}. {prompt}"

            logger.info(f"Generating video with Veo 2.0: {full_prompt[:100]}...")

            # Determine output GCS path
            output_gcs_uri = f"gs://{settings.storage_bucket}/videos/{job_id}/day{day}/"

            # Build generate_videos config (following official docs)
            config = genai_types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=settings.video_duration_seconds,
                aspect_ratio="9:16",  # Vertical video for Instagram/TikTok
                output_gcs_uri=output_gcs_uri,
                enhance_prompt=True
            )

            # Build generate_videos payload
            generate_payload = {
                'model': 'veo-2.0-generate-001',
                'prompt': full_prompt,
                'config': config
            }

            # Add reference image if provided (for first segment, image-to-video)
            if reference_image_base64 and not previous_video_gcs_uri:
                logger.info("Adding reference image to video generation (image-to-video)")
                generate_payload['image'] = {
                    'image_bytes': reference_image_base64,
                    'mime_type': 'image/jpeg'
                }

            # Add previous video for extension (for subsequent segments, video-to-video)
            if previous_video_gcs_uri:
                logger.info(f"Extending from previous video: {previous_video_gcs_uri}")
                # Following official docs: use Video object with GCS URI
                generate_payload['video'] = Video(
                    uri=previous_video_gcs_uri,
                    mime_type='video/mp4'
                )

            # Generate video using Veo
            logger.info("Submitting video generation request to Veo...")
            operation = self.genai_client.models.generate_videos(**generate_payload)

            # Poll operation until complete (following official docs pattern)
            max_polls = 60  # 10 minutes max
            poll_interval = 15  # 15 seconds (matching official docs)
            polls = 0

            while not operation.done and polls < max_polls:
                await asyncio.sleep(poll_interval)
                polls += 1
                logger.info(f"Video generation in progress... ({polls * poll_interval}s elapsed)")
                operation = self.genai_client.operations.get(operation=operation)

            if not operation.done:
                logger.error(f"Video generation timed out after {max_polls * poll_interval} seconds")
                return None

            # Extract video from operation result (following official docs)
            if hasattr(operation, 'result') and operation.result:
                result = operation.result
                if hasattr(result, 'generated_videos') and result.generated_videos:
                    videos = result.generated_videos
                    if videos and len(videos) > 0:
                        first_video = videos[0]
                        video_object = first_video.video

                        if not video_object or not video_object.uri:
                            logger.error("Generated video is missing URI")
                            return None

                        video_gcs_uri = video_object.uri  # This is the gs:// URI
                        logger.info(f"Video generated successfully: {video_gcs_uri}")

                        # Convert GCS URI to public HTTP URL
                        # gs://bucket/path -> https://storage.googleapis.com/bucket/path
                        if video_gcs_uri.startswith('gs://'):
                            gcs_path = video_gcs_uri[5:]  # Remove 'gs://'
                            public_url = f"https://storage.googleapis.com/{gcs_path}"
                            logger.info(f"Public URL: {public_url}")

                            return {
                                'uri': public_url,  # Public HTTP URL for frontend
                                'gcs_uri': video_gcs_uri  # GCS URI for video extension
                            }
                        else:
                            logger.error(f"Unexpected URI format: {video_gcs_uri}")
                            return None
                    else:
                        logger.error("No videos in result")
                        return None
                else:
                    logger.error("Result missing generated_videos")
                    return None
            else:
                logger.error("Operation missing result")
                return None

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def _generate_images(
        self,
        image_prompts: List[str],
        business_profile: Dict,
        job_id: str = "",
        day: int = 0
    ) -> List[ImageSegment]:
        """
        Generate image segments using Gemini native image generation (gemini-2.5-flash-image).
        If image generation is disabled, returns placeholder segments.

        Args:
            image_prompts: List of prompts for image generation (limited to 3)
            business_profile: Business profile from Agent 1

        Returns:
            List of ImageSegment objects with base64 data URIs
        """
        if not image_prompts:
            return []

        # Check if image generation is disabled
        if not settings.enable_image_generation:
            logger.info(f"Image generation DISABLED - creating {len(image_prompts)} placeholder segments")
            placeholders = []
            for i, prompt in enumerate(image_prompts[:settings.max_images_per_post], 1):
                placeholders.append(ImageSegment(
                    segment_number=i,
                    uri=f"placeholder://image-segment-{i}",
                    prompt_used=prompt
                ))
            return placeholders

        logger.info(f"Generating {len(image_prompts)} images with Gemini native image generation")

        images = []

        # Limit to exactly 3 images per post
        for i, prompt in enumerate(image_prompts[:settings.max_images_per_post], 1):
            logger.info(f"Generating image {i}/{min(len(image_prompts), settings.max_images_per_post)}")

            try:
                result = await self._generate_single_image(
                    prompt=prompt,
                    segment_number=i,
                    business_profile=business_profile,
                    job_id=job_id,
                    day=day
                )

                if result and result.get('uri'):
                    image = ImageSegment(
                        segment_number=i,
                        uri=result['uri'],
                        prompt_used=prompt
                    )
                    images.append(image)
                else:
                    logger.warning(f"Failed to generate image {i}")

            except Exception as e:
                logger.error(f"Error generating image {i}: {e}")
                continue

        logger.info(f"Generated {len(images)} images successfully")
        return images

    async def _generate_single_image(
        self,
        prompt: str,
        segment_number: int,
        business_profile: Dict = None,
        job_id: str = "",
        day: int = 0
    ) -> Optional[Dict]:
        """
        Generate single image with Gemini native image generation (gemini-2.5-flash-image).
        Uses actual business photos as style references to match the brand's visual identity.
        Uploads to GCS and returns public URL.

        Args:
            prompt: Visual prompt for image generation
            segment_number: Image number (for logging)
            business_profile: Complete business profile including photos
            job_id: Job ID for organizing files in GCS
            day: Day number for organizing files

        Returns:
            Dict with 'uri' key (GCS public URL) or None if generation fails
        """
        try:
            business_profile = business_profile or {}
            business_name = business_profile.get('business_name', '')

            # Enhance prompt with business context
            full_prompt = prompt
            if business_name:
                full_prompt = f"{business_name}. {prompt}"

            # Fetch business photos for style reference
            reference_images = []
            business_photos = business_profile.get('photos', [])

            if business_photos and len(business_photos) > 0:
                logger.info(f"Found {len(business_photos)} business photos, using first 3 as style references")
                # Use up to 3 photos as style references
                for photo in business_photos[:3]:
                    photo_url = photo.get('url')
                    if photo_url:
                        image_base64 = await self._fetch_and_encode_image(photo_url)
                        if image_base64:
                            reference_images.append(image_base64)
                            logger.info(f"Added business photo as style reference")
                        else:
                            logger.warning(f"Failed to fetch business photo: {photo_url}")

            # Build multimodal prompt with text + reference images
            if reference_images:
                logger.info(f"Generating image with {len(reference_images)} style reference(s)")

                # Create a detailed style-matching prompt
                style_prompt = f"""Based on the provided reference images showing the actual brand's visual style,
generate a new image that matches this aesthetic. The image should capture the same:
- Photography style and lighting
- Color palette and mood
- Brand personality and vibe
- Food presentation style (if food business)
- Overall visual identity

Create: {full_prompt}

Make sure the generated image looks authentic and consistent with the brand's existing visual identity shown in the references."""

                # Build contents array with text + images
                contents = [style_prompt]
                for ref_img in reference_images:
                    contents.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": ref_img
                        }
                    })

                response = self.genai_client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        mediaResolution="MEDIA_RESOLUTION_MEDIUM"
                    )
                )
            else:
                logger.warning("No business photos available, generating without style references")
                logger.info(f"Generating image with prompt: {full_prompt}")

                response = self.genai_client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=full_prompt,
                    config=genai_types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        mediaResolution="MEDIA_RESOLUTION_MEDIUM"
                    )
                )

            # Extract image from response parts
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    # Get image data and mime type
                    # Check type and decode if needed
                    raw_data = part.inline_data.data
                    logger.info(f"Raw data type: {type(raw_data).__name__}, first 50 chars: {str(raw_data)[:50]}")

                    if isinstance(raw_data, str):
                        # It's a base64 string, decode it
                        image_bytes = base64.b64decode(raw_data)
                    elif isinstance(raw_data, bytes):
                        # Already bytes, check if it's base64-encoded text or binary
                        try:
                            # Try to decode as UTF-8 - if it succeeds, it might be base64 text
                            text = raw_data.decode('utf-8')
                            if text.startswith('iVBOR') or text.startswith('/9j/'):
                                # Looks like base64, decode it
                                image_bytes = base64.b64decode(text)
                            else:
                                image_bytes = raw_data
                        except:
                            # Not text, must be binary
                            image_bytes = raw_data
                    else:
                        image_bytes = raw_data

                    mime_type = part.inline_data.mime_type or 'image/jpeg'
                    logger.info(f"Image generated successfully ({len(image_bytes)} bytes), type after processing: {type(image_bytes).__name__}")

                    # Upload to GCS and get public URL
                    public_url = self.storage_service.upload_image(
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                        job_id=job_id,
                        day=day,
                        segment_number=segment_number
                    )

                    if public_url:
                        logger.info(f"Image uploaded to GCS: {public_url}")
                        return {'uri': public_url}
                    else:
                        # Fall back to base64 data URI if GCS upload fails
                        logger.warning("GCS upload failed, falling back to base64 data URI")
                        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                        data_uri = f"data:{mime_type};base64,{image_b64}"
                        return {'uri': data_uri}

            logger.error("No image data in response")
            return None

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
