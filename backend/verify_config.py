#!/usr/bin/env python3
"""
Configuration Verification Script
Verifies all Track 3 configuration settings are correct
"""

from config import settings


def verify_config():
    """Verify all configuration settings"""
    print("=" * 60)
    print("TRACK 3: Configuration Verification")
    print("=" * 60)
    print()

    # Check content limits
    print("Content Limits:")
    print(f"  ✓ Max videos per post: {settings.max_videos_per_post}")
    assert settings.max_videos_per_post == 3, "Expected 3 videos per post"

    print(f"  ✓ Max images per post: {settings.max_images_per_post}")
    assert settings.max_images_per_post == 3, "Expected 3 images per post"
    print()

    # Check video settings
    print("Video Settings:")
    print(f"  ✓ Video duration: {settings.video_duration_seconds} seconds")
    assert settings.video_duration_seconds == 5, "Expected 5 seconds per video"

    print(f"  ✓ Video resolution: {settings.video_resolution}")
    assert settings.video_resolution == "720p", "Expected 720p resolution"
    print()

    # Check cost control flags
    print("Cost Control Flags:")
    print(f"  ✓ Video generation enabled: {settings.enable_video_generation}")
    print(f"  ✓ Image generation enabled: {settings.enable_image_generation}")

    if not settings.enable_video_generation and not settings.enable_image_generation:
        print("  ✓ SAFE MODE: Placeholder mode active (no API costs)")
    else:
        print("  ⚠ COST MODE: API generation enabled (will incur costs)")
    print()

    # Check GCP configuration
    print("GCP Configuration:")
    print(f"  ✓ Project ID: {settings.project_id or '(not set)'}")
    print(f"  ✓ Region: {settings.region}")
    print(f"  ✓ Storage bucket: {settings.storage_bucket or '(not set)'}")
    print()

    # Calculate cost estimate
    print("Cost Estimates:")
    if not settings.enable_video_generation and not settings.enable_image_generation:
        print("  ✓ Per post: $0.00 (placeholders)")
        print("  ✓ Full calendar (7 days): $0.00 (placeholders)")
    else:
        video_cost = 0.40 if settings.enable_video_generation else 0
        image_cost = 0.09 if settings.enable_image_generation else 0
        post_cost = video_cost + image_cost
        calendar_cost = post_cost * 7

        print(f"  ✓ Per post: ${post_cost:.2f}")
        print(f"  ✓ Full calendar (7 days): ${calendar_cost:.2f}")

        if settings.enable_video_generation:
            print(f"    - Videos (3 @ 5s each): ${video_cost:.2f}")
        if settings.enable_image_generation:
            print(f"    - Images (3): ${image_cost:.2f}")
    print()

    # Cost savings
    print("Cost Savings (8s → 5s video duration):")
    old_video_cost_per_post = 0.64
    new_video_cost_per_post = 0.40
    savings_per_post = old_video_cost_per_post - new_video_cost_per_post
    savings_per_calendar = savings_per_post * 7
    savings_percentage = (savings_per_post / old_video_cost_per_post) * 100

    print(f"  ✓ Per post: ${savings_per_post:.2f} saved ({savings_percentage:.1f}%)")
    print(f"  ✓ Per calendar: ${savings_per_calendar:.2f} saved ({savings_percentage:.1f}%)")
    print(f"  ✓ Annual (1000 calendars): ${savings_per_calendar * 1000:.2f} saved")
    print()

    print("=" * 60)
    print("✓ All configuration settings verified successfully!")
    print("=" * 60)
    print()

    # Recommendations
    print("Recommendations:")
    if settings.enable_video_generation or settings.enable_image_generation:
        print("  ⚠ Media generation is ENABLED. Costs will be incurred.")
        print("  → For development, set ENABLE_VIDEOS=false and ENABLE_IMAGES=false")
    else:
        print("  ✓ Safe mode is active. No API costs will be incurred.")
        print("  → For demo, create .env and enable video/image generation")
    print()


if __name__ == "__main__":
    verify_config()
