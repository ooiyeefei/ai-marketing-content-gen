#!/usr/bin/env python3
"""
Test script to verify Veo 2.0 video generation works correctly.
This follows the official Google Cloud documentation pattern.
"""

import asyncio
import sys
from google import genai
from google.genai.types import GenerateVideosConfig
from config import settings

async def test_simple_video_generation():
    """Test basic text-to-video generation with Veo 2.0"""

    print("=" * 60)
    print("Testing Veo 2.0 Video Generation")
    print("=" * 60)

    # Check configuration
    print(f"\nConfiguration:")
    print(f"  Project: {settings.project_id}")
    print(f"  Region: {settings.region}")
    print(f"  Bucket: {settings.storage_bucket}")
    print(f"  Video generation enabled: {settings.enable_video_generation}")

    if not settings.enable_video_generation:
        print("\n⚠️  WARNING: Video generation is DISABLED in .env")
        print("   Set ENABLE_VIDEOS=true to test actual generation")
        return False

    if not settings.storage_bucket:
        print("\n❌ ERROR: STORAGE_BUCKET not configured in .env")
        return False

    try:
        # Initialize GenAI client (uses Application Default Credentials)
        print("\n✓ Initializing Google GenAI client...")
        client = genai.Client(
            vertexai=True,
            project=settings.project_id,
            location=settings.region
        )

        # Test prompt
        prompt = "A delicious burger with melted cheese, fresh lettuce, and crispy bacon on a wooden table"

        print(f"\n✓ Generating 5-second video with prompt:")
        print(f"  '{prompt}'")

        # Output GCS path
        output_gcs_uri = f"gs://{settings.storage_bucket}/test-videos/"
        print(f"\n✓ Output will be saved to: {output_gcs_uri}")

        # Generate video (following official docs)
        config = GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=5,
            aspect_ratio="9:16",  # Vertical format
            output_gcs_uri=output_gcs_uri,
            enhance_prompt=True
        )

        print("\n✓ Submitting generation request to Veo 2.0...")
        operation = client.models.generate_videos(
            model='veo-2.0-generate-001',
            prompt=prompt,
            config=config
        )

        print(f"  Operation name: {operation.name}")

        # Poll until complete
        poll_count = 0
        max_polls = 40  # 10 minutes max

        while not operation.done and poll_count < max_polls:
            await asyncio.sleep(15)
            poll_count += 1
            elapsed = poll_count * 15
            print(f"  ⏳ Generating... ({elapsed}s elapsed)")
            operation = client.operations.get(operation=operation)

        if not operation.done:
            print(f"\n❌ ERROR: Video generation timed out after {poll_count * 15} seconds")
            return False

        # Check result
        if hasattr(operation, 'result') and operation.result:
            result = operation.result
            if hasattr(result, 'generated_videos') and result.generated_videos:
                videos = result.generated_videos
                if videos and len(videos) > 0:
                    video = videos[0].video

                    print("\n" + "=" * 60)
                    print("✅ SUCCESS! Video generated")
                    print("=" * 60)
                    print(f"\nVideo GCS URI: {video.uri}")

                    # Convert to public URL
                    if video.uri.startswith('gs://'):
                        gcs_path = video.uri[5:]
                        public_url = f"https://storage.googleapis.com/{gcs_path}"
                        print(f"Public URL: {public_url}")

                    print(f"\nVideo properties:")
                    if hasattr(video, 'aspect_ratio'):
                        print(f"  Aspect ratio: {video.aspect_ratio}")
                    if hasattr(video, 'mime_type'):
                        print(f"  MIME type: {video.mime_type}")

                    return True
                else:
                    print("\n❌ ERROR: No videos in result")
                    return False
            else:
                print("\n❌ ERROR: Result missing generated_videos")
                return False
        else:
            print("\n❌ ERROR: Operation missing result")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    success = await test_simple_video_generation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
