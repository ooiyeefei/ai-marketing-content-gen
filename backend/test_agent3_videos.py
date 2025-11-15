import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.creative_producer import CreativeProducerAgent


async def test_video_generation():
    """
    Test video generation with Veo.
    WARNING: This makes real API calls and takes 2-5 minutes per video.
    """
    agent = CreativeProducerAgent()

    # Test with 2 segments (extension demo)
    video_prompts = [
        "Close-up of hands preparing fresh ingredients, bright kitchen lighting",
        "Chef plating the finished dish, garnishing with herbs, warm lighting"
    ]

    business_profile = {
        'business_name': 'The Hawker'
    }

    print("=" * 60)
    print("Testing Creative Producer Agent - Video Generation")
    print("=" * 60)
    print(f"\nBusiness: {business_profile['business_name']}")
    print(f"Video segments to generate: {len(video_prompts)}")
    print("\nPrompts:")
    for i, prompt in enumerate(video_prompts, 1):
        print(f"  {i}. {prompt}")

    print("\n" + "-" * 60)
    print("Starting video generation (this will take several minutes)...")
    print("-" * 60)

    segments = await agent._generate_videos(video_prompts, business_profile)

    print(f"\n{'=' * 60}")
    print(f"Generated {len(segments)} segments:")
    print("=" * 60)
    for seg in segments:
        print(f"\n  Segment {seg.segment_number}:")
        print(f"    URI: {seg.uri}")
        print(f"    Duration: {seg.duration_seconds}s")
        print(f"    Prompt: {seg.prompt_used}")

    print("\n" + "=" * 60)
    print("Video generation test completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Uncomment to test (will make real API calls)
    # asyncio.run(test_video_generation())
    print("=" * 60)
    print("Video generation test DISABLED by default.")
    print("=" * 60)
    print("\nThis test makes real Veo API calls which:")
    print("  - Take 2-5 minutes per video segment")
    print("  - Incur costs on your GCP project")
    print("  - Require valid GCP credentials and project setup")
    print("\nTo enable this test:")
    print("  1. Uncomment the asyncio.run() line at the bottom of this file")
    print("  2. Ensure GCP_PROJECT_ID, GCP_REGION, and STORAGE_BUCKET are set")
    print("  3. Run: python test_agent3_videos.py")
    print("\n" + "=" * 60)
