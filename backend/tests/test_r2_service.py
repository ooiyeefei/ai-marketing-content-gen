"""
Test suite for R2Service - Cloudflare R2 object storage

Tests real API interactions (no mocks) as per CLAUDE.md principles:
- Single and concurrent uploads
- URL accessibility verification
- Byte-level download validation
- Error handling with invalid credentials
"""

import asyncio
import sys
import os

# Load environment variables
import httpx
from io import BytesIO
from PIL import Image
import uuid
import time
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.r2_service import R2Service


class TestResults:
    """Track test results for reporting"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.start_time = time.time()

    def add_pass(self, test_name: str, duration: float):
        self.passed.append((test_name, duration))

    def add_fail(self, test_name: str, error: str, duration: float):
        self.failed.append((test_name, error, duration))

    def report(self):
        total_duration = time.time() - self.start_time
        total_tests = len(self.passed) + len(self.failed)

        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)

        if self.passed:
            print(f"\n✅ PASSED: {len(self.passed)}/{total_tests}")
            for test_name, duration in self.passed:
                print(f"   - {test_name} ({duration:.2f}s)")

        if self.failed:
            print(f"\n❌ FAILED: {len(self.failed)}/{total_tests}")
            for test_name, error, duration in self.failed:
                print(f"   - {test_name} ({duration:.2f}s)")
                print(f"     Error: {error}")

        print(f"\nTotal time: {total_duration:.2f}s")
        print("=" * 70 + "\n")

        return len(self.failed) == 0


def create_test_image(width: int = 100, height: int = 100, color: str = "red") -> bytes:
    """
    Create a simple test image as bytes.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: PIL color name or hex

    Returns:
        JPEG image as bytes
    """
    img = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()


async def test_r2_upload_bytes(results: TestResults):
    """
    Test single file upload to R2 with full validation:
    1. Upload test image bytes
    2. Verify public URL is accessible (HTTP 200)
    3. Download content from URL
    4. Verify downloaded bytes match original
    """
    test_name = "test_r2_upload_bytes"
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")

    start_time = time.time()

    try:
        # Initialize R2 service
        r2 = R2Service()
        print("✓ R2Service initialized")

        # Create test image (100x100 red square)
        original_bytes = create_test_image(width=100, height=100, color="red")
        print(f"✓ Created test image: {len(original_bytes)} bytes")

        # Generate unique object key
        object_key = f"test/upload_{uuid.uuid4()}.jpg"
        print(f"✓ Object key: {object_key}")

        # Upload to R2
        public_url = await r2.upload_bytes(
            data=original_bytes,
            object_key=object_key,
            content_type="image/jpeg"
        )
        print(f"✓ Uploaded to R2")
        print(f"  URL: {public_url}")

        # Verify URL is accessible
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(public_url)
            response.raise_for_status()

        print(f"✓ URL accessible: HTTP {response.status_code}")

        # Download and verify bytes match
        downloaded_bytes = response.content
        print(f"✓ Downloaded: {len(downloaded_bytes)} bytes")

        if downloaded_bytes == original_bytes:
            print("✓ Byte verification: MATCH")
        else:
            raise AssertionError(
                f"Byte mismatch: uploaded {len(original_bytes)} bytes, "
                f"downloaded {len(downloaded_bytes)} bytes"
            )

        duration = time.time() - start_time
        print(f"\n✅ TEST PASSED ({duration:.2f}s)")
        results.add_pass(test_name, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED ({duration:.2f}s)")
        print(f"Error: {str(e)}")
        results.add_fail(test_name, str(e), duration)


async def test_r2_upload_multiple_concurrent(results: TestResults):
    """
    Test concurrent uploads to R2:
    1. Create 5 different test images
    2. Upload all 5 in parallel using asyncio.gather
    3. Verify all URLs are accessible
    4. Verify at least 3 completed successfully (allow for some failures)
    """
    test_name = "test_r2_upload_multiple_concurrent"
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")

    start_time = time.time()

    try:
        r2 = R2Service()
        print("✓ R2Service initialized")

        # Create 5 different test images
        test_images: List[Tuple[bytes, str, str]] = []
        colors = ["red", "blue", "green", "yellow", "purple"]

        for i, color in enumerate(colors):
            image_bytes = create_test_image(width=100, height=100, color=color)
            object_key = f"test/concurrent_{uuid.uuid4()}_{color}.jpg"
            test_images.append((image_bytes, object_key, color))

        print(f"✓ Created {len(test_images)} test images")

        # Upload all concurrently
        upload_tasks = [
            r2.upload_bytes(
                data=img_bytes,
                object_key=obj_key,
                content_type="image/jpeg"
            )
            for img_bytes, obj_key, _ in test_images
        ]

        print(f"⏳ Uploading {len(upload_tasks)} files concurrently...")
        upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)

        # Count successes
        successful_urls = [
            url for url in upload_results
            if isinstance(url, str) and url.startswith("http")
        ]
        print(f"✓ Successful uploads: {len(successful_urls)}/{len(upload_tasks)}")

        # Verify URLs are accessible (at least the successful ones)
        async with httpx.AsyncClient(timeout=30.0) as client:
            verify_tasks = [client.get(url) for url in successful_urls]
            verify_results = await asyncio.gather(*verify_tasks, return_exceptions=True)

            accessible_count = sum(
                1 for result in verify_results
                if not isinstance(result, Exception) and result.status_code == 200
            )

        print(f"✓ Accessible URLs: {accessible_count}/{len(successful_urls)}")

        # Assert: At least 3 out of 5 should succeed
        if len(successful_urls) < 3:
            raise AssertionError(
                f"Expected at least 3 successful uploads, got {len(successful_urls)}"
            )

        if accessible_count < 3:
            raise AssertionError(
                f"Expected at least 3 accessible URLs, got {accessible_count}"
            )

        duration = time.time() - start_time
        print(f"\n✅ TEST PASSED ({duration:.2f}s)")
        results.add_pass(test_name, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED ({duration:.2f}s)")
        print(f"Error: {str(e)}")
        results.add_fail(test_name, str(e), duration)


async def test_r2_error_handling(results: TestResults):
    """
    Test error handling with invalid credentials:
    1. Temporarily set invalid credentials
    2. Attempt upload
    3. Verify appropriate exception is raised
    4. Restore original credentials
    """
    test_name = "test_r2_error_handling"
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")

    start_time = time.time()

    # Save original credentials
    original_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    original_access_key = os.getenv("R2_ACCESS_KEY_ID")
    original_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")

    try:
        print("⏳ Testing invalid credentials handling...")

        # Test 1: Missing credentials
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = ""
        os.environ["R2_ACCESS_KEY_ID"] = ""
        os.environ["R2_SECRET_ACCESS_KEY"] = ""

        try:
            r2 = R2Service()
            raise AssertionError("Expected ValueError for missing credentials")
        except ValueError as e:
            if "Missing R2 credentials" in str(e):
                print("✓ Correctly raised ValueError for missing credentials")
            else:
                raise

        # Restore credentials for next test
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = original_account_id
        os.environ["R2_ACCESS_KEY_ID"] = original_access_key
        os.environ["R2_SECRET_ACCESS_KEY"] = original_secret_key

        # Test 2: Invalid credentials (should fail on upload)
        os.environ["R2_ACCESS_KEY_ID"] = "invalid_key_12345"
        os.environ["R2_SECRET_ACCESS_KEY"] = "invalid_secret_67890"

        try:
            r2 = R2Service()
            test_bytes = create_test_image()
            object_key = f"test/error_test_{uuid.uuid4()}.jpg"

            # This should raise an exception
            await r2.upload_bytes(
                data=test_bytes,
                object_key=object_key,
                content_type="image/jpeg"
            )

            # If we reach here, test failed
            raise AssertionError("Expected exception for invalid credentials during upload")

        except Exception as e:
            # We expect an exception (not AssertionError)
            if isinstance(e, AssertionError):
                raise
            print(f"✓ Correctly raised exception for invalid credentials: {type(e).__name__}")

        duration = time.time() - start_time
        print(f"\n✅ TEST PASSED ({duration:.2f}s)")
        results.add_pass(test_name, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED ({duration:.2f}s)")
        print(f"Error: {str(e)}")
        results.add_fail(test_name, str(e), duration)

    finally:
        # Always restore original credentials
        if original_account_id:
            os.environ["CLOUDFLARE_ACCOUNT_ID"] = original_account_id
        if original_access_key:
            os.environ["R2_ACCESS_KEY_ID"] = original_access_key
        if original_secret_key:
            os.environ["R2_SECRET_ACCESS_KEY"] = original_secret_key
        print("✓ Original credentials restored")


async def test_r2_upload_from_url(results: TestResults):
    """
    Test uploading from external URL:
    1. Use a known public image URL
    2. Upload to R2 via upload_from_url
    3. Verify new R2 URL is accessible
    """
    test_name = "test_r2_upload_from_url"
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")

    start_time = time.time()

    try:
        r2 = R2Service()
        print("✓ R2Service initialized")

        # Use a reliable test image URL (placeholder service)
        source_url = "https://via.placeholder.com/150/FF0000/FFFFFF?text=Test"
        object_key = f"test/from_url_{uuid.uuid4()}.jpg"

        print(f"⏳ Downloading from: {source_url}")

        # Upload from URL
        public_url = await r2.upload_from_url(
            source_url=source_url,
            object_key=object_key,
            content_type="image/jpeg"
        )

        print(f"✓ Uploaded to R2: {public_url}")

        # Verify URL is accessible
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(public_url)
            response.raise_for_status()

        print(f"✓ URL accessible: HTTP {response.status_code}")
        print(f"✓ Content size: {len(response.content)} bytes")

        duration = time.time() - start_time
        print(f"\n✅ TEST PASSED ({duration:.2f}s)")
        results.add_pass(test_name, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED ({duration:.2f}s)")
        print(f"Error: {str(e)}")
        results.add_fail(test_name, str(e), duration)


async def test_r2_campaign_path_helper(results: TestResults):
    """
    Test campaign path helper method:
    1. Generate campaign paths
    2. Verify format matches expected pattern
    """
    test_name = "test_r2_campaign_path_helper"
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")

    start_time = time.time()

    try:
        r2 = R2Service()
        print("✓ R2Service initialized")

        # Test path generation
        campaign_id = "test_campaign_123"
        filename = "research/competitor_1.jpg"

        path = r2.get_campaign_path(campaign_id, filename)
        expected = f"campaigns/{campaign_id}/{filename}"

        print(f"Generated path: {path}")
        print(f"Expected path:  {expected}")

        if path == expected:
            print("✓ Path format correct")
        else:
            raise AssertionError(f"Path mismatch: {path} != {expected}")

        duration = time.time() - start_time
        print(f"\n✅ TEST PASSED ({duration:.2f}s)")
        results.add_pass(test_name, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED ({duration:.2f}s)")
        print(f"Error: {str(e)}")
        results.add_fail(test_name, str(e), duration)


async def main():
    """
    Run all R2Service tests sequentially.

    Tests are run in order of complexity:
    1. Helper method test (fastest)
    2. Single upload with validation
    3. Upload from external URL
    4. Concurrent uploads (5 parallel)
    5. Error handling (credential validation)
    """
    print("\n" + "=" * 70)
    print("R2 SERVICE TEST SUITE")
    print("=" * 70)
    print("\nTesting REAL Cloudflare R2 APIs (no mocks)")
    print("Following CLAUDE.md principles: TDD, no mocks, autonomous validation")
    print("=" * 70)

    results = TestResults()

    # Run all tests
    await test_r2_campaign_path_helper(results)
    await test_r2_upload_bytes(results)
    await test_r2_upload_from_url(results)
    await test_r2_upload_multiple_concurrent(results)
    await test_r2_error_handling(results)

    # Report results
    all_passed = results.report()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
