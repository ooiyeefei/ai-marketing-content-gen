#!/usr/bin/env python3
"""
Test suite for MiniMaxService

Tests image generation (text-to-image) and video generation (image-to-video)
with real API calls. Saves outputs for manual verification.

Test Philosophy:
- Use REAL API calls (no mocks) to verify integration
- Save all outputs to outputs/minimax/ for inspection
- Verify file sizes and formats
- Include error handling tests
- Follow verification-before-completion principle
"""
import asyncio
import sys
import os
from typing import List, Tuple

# Load environment variables from .env file

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.minimax_service import MiniMaxService

# Test configuration
OUTPUT_DIR = Path(__file__).parent / "outputs" / "minimax"
MIN_IMAGE_SIZE_KB = 10
MIN_VIDEO_SIZE_KB = 100

# Test results tracking
test_results = []


def log_test_result(test_name: str, passed: bool, message: str):
    """Log test result for summary"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status}: {test_name}")
    print(f"  {message}")
    test_results.append({
        "name": test_name,
        "passed": passed,
        "message": message
    })


def verify_file_size(file_path: Path, min_size_kb: int) -> Tuple[bool, str]:
    """Verify file exists and meets minimum size requirement"""
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    size_bytes = file_path.stat().st_size
    size_kb = size_bytes / 1024

    if size_kb < min_size_kb:
        return False, f"File too small: {size_kb:.2f}KB < {min_size_kb}KB"

    return True, f"File valid: {size_kb:.2f}KB"


def save_image(image_bytes: bytes, filename: str) -> Path:
    """Save image bytes to output directory"""
    file_path = OUTPUT_DIR / filename
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    return file_path


def save_video(video_bytes: bytes, filename: str) -> Path:
    """Save video bytes to output directory"""
    file_path = OUTPUT_DIR / filename
    with open(file_path, "wb") as f:
        f.write(video_bytes)
    return file_path


async def test_minimax_image_generation_simple():
    """
    Test simple image generation without reference.

    Expected: 2 images generated, each > 10KB
    """
    test_name = "test_minimax_image_generation_simple"
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    try:
        service = MiniMaxService()

        prompt = "A serene coffee shop interior with natural lighting, wooden tables, plants, and a warm atmosphere. Instagram-worthy aesthetic."
        print(f"Prompt: {prompt}")
        print("Generating 2 images...")

        images = await service.generate_images(
            prompt=prompt,
            num_images=2,
            aspect_ratio="1:1"
        )

        if not images:
            log_test_result(test_name, False, "No images returned from API")
            return

        if len(images) != 2:
            log_test_result(test_name, False, f"Expected 2 images, got {len(images)}")
            return

        # Save and verify each image
        all_valid = True
        messages = []

        for i, image_bytes in enumerate(images):
            filename = f"test_simple_image_{i+1}.jpg"
            file_path = save_image(image_bytes, filename)

            valid, message = verify_file_size(file_path, MIN_IMAGE_SIZE_KB)
            messages.append(f"Image {i+1}: {message}")

            if not valid:
                all_valid = False

        result_message = "\n  ".join(messages)
        log_test_result(test_name, all_valid, result_message)

    except Exception as e:
        log_test_result(test_name, False, f"Exception: {str(e)}")


async def test_minimax_image_generation_with_reference():
    """
    Test image generation with subject reference URL.

    Expected: 2 images generated with subject consistency
    """
    test_name = "test_minimax_image_generation_with_reference"
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    try:
        service = MiniMaxService()

        # Note: This requires a valid R2 URL with an uploaded reference image
        # For testing purposes, we'll use a placeholder. In real tests, upload an image first.
        reference_url = "https://pub-your-account.r2.dev/test-reference.jpg"
        prompt = "A cozy coffee shop with the subject standing behind the counter, serving customers"

        print(f"Prompt: {prompt}")
        print(f"Reference URL: {reference_url}")
        print("Note: This test requires a valid reference image URL")
        print("Generating 2 images with subject reference...")

        try:
            images = await service.generate_images(
                prompt=prompt,
                subject_reference_url=reference_url,
                num_images=2,
                aspect_ratio="1:1"
            )

            if not images:
                log_test_result(
                    test_name,
                    False,
                    "No images returned (expected if reference URL is invalid)"
                )
                return

            # Save and verify each image
            all_valid = True
            messages = []

            for i, image_bytes in enumerate(images):
                filename = f"test_reference_image_{i+1}.jpg"
                file_path = save_image(image_bytes, filename)

                valid, message = verify_file_size(file_path, MIN_IMAGE_SIZE_KB)
                messages.append(f"Image {i+1}: {message}")

                if not valid:
                    all_valid = False

            result_message = "\n  ".join(messages)
            log_test_result(test_name, all_valid, result_message)

        except Exception as api_error:
            # This is expected if reference URL is invalid
            log_test_result(
                test_name,
                False,
                f"API error (may be expected): {str(api_error)}"
            )

    except Exception as e:
        log_test_result(test_name, False, f"Exception: {str(e)}")


async def test_minimax_video_generation():
    """
    Test video generation from image.

    Expected: Video file > 100KB
    Note: This test requires a valid first frame image URL
    """
    test_name = "test_minimax_video_generation"
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    try:
        service = MiniMaxService()

        # Note: This requires a valid R2 URL with an uploaded first frame image
        # In a real test, generate an image first, upload to R2, then use that URL
        first_frame_url = "https://pub-your-account.r2.dev/test-first-frame.jpg"
        motion_prompt = "Slow zoom in on the coffee shop interior, warm lighting gradually illuminates the space"

        print(f"Motion Prompt: {motion_prompt}")
        print(f"First Frame URL: {first_frame_url}")
        print("Note: This test requires a valid first frame image URL")
        print("Generating video (this may take 3-5 minutes)...")

        try:
            video_bytes = await service.generate_video(
                motion_prompt=motion_prompt,
                first_frame_image_url=first_frame_url,
                duration=6
            )

            if not video_bytes:
                log_test_result(
                    test_name,
                    False,
                    "No video returned (expected if first frame URL is invalid)"
                )
                return

            filename = "test_video_1.mp4"
            file_path = save_video(video_bytes, filename)

            valid, message = verify_file_size(file_path, MIN_VIDEO_SIZE_KB)
            log_test_result(test_name, valid, message)

        except Exception as api_error:
            # This is expected if first frame URL is invalid
            log_test_result(
                test_name,
                False,
                f"API error (may be expected): {str(api_error)}"
            )

    except Exception as e:
        log_test_result(test_name, False, f"Exception: {str(e)}")


async def test_minimax_error_handling():
    """
    Test error handling with invalid API key.

    Expected: Proper error message, no crash
    """
    test_name = "test_minimax_error_handling"
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    try:
        # Save original API key
        original_key = os.getenv("MINIMAX_API_KEY")

        # Test 1: Missing API key
        os.environ["MINIMAX_API_KEY"] = ""

        try:
            service = MiniMaxService()
            log_test_result(
                test_name,
                False,
                "Should have raised ValueError for missing API key"
            )
        except ValueError as e:
            if "MINIMAX_API_KEY" in str(e):
                log_test_result(
                    test_name,
                    True,
                    f"Correctly raised ValueError: {str(e)}"
                )
            else:
                log_test_result(
                    test_name,
                    False,
                    f"Wrong error message: {str(e)}"
                )

        # Restore original API key
        if original_key:
            os.environ["MINIMAX_API_KEY"] = original_key

    except Exception as e:
        log_test_result(test_name, False, f"Unexpected exception: {str(e)}")


async def test_minimax_initialization():
    """
    Test MiniMax service initialization.

    Expected: Service initializes with valid configuration
    """
    test_name = "test_minimax_initialization"
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    try:
        service = MiniMaxService()

        # Check API key is set
        has_api_key = service.api_key is not None and len(service.api_key) > 0

        # Check URLs are configured (updated to correct base URL)
        has_image_url = service.image_url == "https://api.minimax.io/v1/image_generation"
        has_video_url = service.video_url == "https://api.minimax.io/v1/video_generation"

        # Check headers are configured
        has_auth_header = "Authorization" in service.headers
        has_content_type = "Content-Type" in service.headers

        all_valid = all([
            has_api_key,
            has_image_url,
            has_video_url,
            has_auth_header,
            has_content_type
        ])

        message = f"""API Key: {'✓' if has_api_key else '✗'}
  Image URL: {'✓' if has_image_url else '✗'}
  Video URL: {'✓' if has_video_url else '✗'}
  Auth Header: {'✓' if has_auth_header else '✗'}
  Content-Type: {'✓' if has_content_type else '✗'}"""

        log_test_result(test_name, all_valid, message)

    except Exception as e:
        log_test_result(test_name, False, f"Exception: {str(e)}")


def print_summary():
    """Print test summary"""
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for r in test_results if r["passed"])
    failed = sum(1 for r in test_results if not r["passed"])
    total = len(test_results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  ✗ {result['name']}")
                print(f"    {result['message']}")

    print(f"\nOutput Directory: {OUTPUT_DIR}")
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*"))
        print(f"Generated Files: {len(files)}")
        for f in sorted(files):
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.2f}KB)")

    print(f"\n{'='*60}")

    # Core tests that must pass: initialization, simple generation, error handling
    core_tests = ["test_minimax_initialization", "test_minimax_image_generation_simple", "test_minimax_error_handling"]
    core_passed = all(r["passed"] for r in test_results if r["name"] in core_tests)

    return core_passed  # Only require core tests to pass


async def main():
    """Run all tests"""
    print("="*60)
    print("MiniMax Service Test Suite")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR}")
    print("Testing with REAL API calls (no mocks)")
    print("="*60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Created output directory: {OUTPUT_DIR}")

    # Check API key
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("\n⚠ WARNING: MINIMAX_API_KEY not set in environment")
        print("Some tests will fail. Please set MINIMAX_API_KEY in .env file")
    else:
        print(f"\n✓ MINIMAX_API_KEY is set (length: {len(api_key)})")

    # Run tests
    await test_minimax_initialization()
    await test_minimax_image_generation_simple()
    await test_minimax_image_generation_with_reference()
    await test_minimax_video_generation()
    await test_minimax_error_handling()

    # Print summary
    success = print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
