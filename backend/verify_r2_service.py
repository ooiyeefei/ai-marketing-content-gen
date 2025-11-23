"""
Verification script for R2Service implementation
Tests basic functionality without pytest dependency
"""
import os
import sys
from unittest.mock import Mock, patch

# Add services to path
sys.path.insert(0, os.path.dirname(__file__))

from services.r2_service import R2Service


def test_initialization():
    """Test R2Service initialization"""
    print("\n=== Test 1: R2Service Initialization ===")

    # Set up mock environment
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test-account-123"
    os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"
    os.environ["R2_BUCKET"] = "test-bucket"

    with patch('services.r2_service.boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3

        try:
            service = R2Service()

            # Verify initialization
            assert service.bucket == "test-bucket", "Bucket name mismatch"
            assert service.public_url_base == "https://pub-test-account-123.r2.dev", "Public URL base mismatch"
            assert service.s3_client is not None, "S3 client not initialized"

            # Verify boto3.client was called correctly
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs['endpoint_url'] == "https://test-account-123.r2.cloudflarestorage.com"
            assert call_kwargs['aws_access_key_id'] == "test-access-key"
            assert call_kwargs['aws_secret_access_key'] == "test-secret-key"
            assert call_kwargs['region_name'] == "auto"

            print("✓ Initialization successful")
            print(f"  - Bucket: {service.bucket}")
            print(f"  - Public URL Base: {service.public_url_base}")
            print(f"  - S3 Client configured with R2 endpoint")
            return True
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            return False


def test_missing_credentials():
    """Test that missing credentials raise error"""
    print("\n=== Test 2: Missing Credentials Validation ===")

    # Clear environment variables
    for key in ["CLOUDFLARE_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"]:
        os.environ.pop(key, None)

    try:
        service = R2Service()
        print("✗ Should have raised ValueError for missing credentials")
        return False
    except ValueError as e:
        if "Missing R2 credentials" in str(e):
            print(f"✓ Correctly raised ValueError: {e}")
            return True
        else:
            print(f"✗ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"✗ Wrong exception type: {e}")
        return False


def test_get_campaign_path():
    """Test campaign path generation"""
    print("\n=== Test 3: Campaign Path Generation ===")

    # Set up environment
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test-account-123"
    os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"

    with patch('services.r2_service.boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3

        try:
            service = R2Service()

            # Test path generation
            path1 = service.get_campaign_path("campaign-abc123", "research/competitor_1.jpg")
            path2 = service.get_campaign_path("xyz-789", "day_1.jpg")

            expected1 = "campaigns/campaign-abc123/research/competitor_1.jpg"
            expected2 = "campaigns/xyz-789/day_1.jpg"

            assert path1 == expected1, f"Path mismatch: {path1} != {expected1}"
            assert path2 == expected2, f"Path mismatch: {path2} != {expected2}"

            print("✓ Path generation works correctly")
            print(f"  - Campaign path 1: {path1}")
            print(f"  - Campaign path 2: {path2}")
            return True
        except Exception as e:
            print(f"✗ Path generation failed: {e}")
            return False


def test_upload_bytes_interface():
    """Test upload_bytes method interface"""
    print("\n=== Test 4: Upload Bytes Interface ===")

    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test-account-123"
    os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"

    with patch('services.r2_service.boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3

        try:
            service = R2Service()

            # Verify method exists and has correct signature
            assert hasattr(service, 'upload_bytes'), "upload_bytes method not found"
            assert callable(service.upload_bytes), "upload_bytes is not callable"

            # Check method is async
            import inspect
            assert inspect.iscoroutinefunction(service.upload_bytes), "upload_bytes is not async"

            print("✓ upload_bytes method exists and is async")
            print(f"  - Signature: {inspect.signature(service.upload_bytes)}")
            return True
        except Exception as e:
            print(f"✗ upload_bytes interface check failed: {e}")
            return False


def test_upload_from_url_interface():
    """Test upload_from_url method interface"""
    print("\n=== Test 5: Upload From URL Interface ===")

    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test-account-123"
    os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"

    with patch('services.r2_service.boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3

        try:
            service = R2Service()

            # Verify method exists and has correct signature
            assert hasattr(service, 'upload_from_url'), "upload_from_url method not found"
            assert callable(service.upload_from_url), "upload_from_url is not callable"

            # Check method is async
            import inspect
            assert inspect.iscoroutinefunction(service.upload_from_url), "upload_from_url is not async"

            print("✓ upload_from_url method exists and is async")
            print(f"  - Signature: {inspect.signature(service.upload_from_url)}")
            return True
        except Exception as e:
            print(f"✗ upload_from_url interface check failed: {e}")
            return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("R2Service Verification Tests")
    print("=" * 60)

    tests = [
        test_initialization,
        test_missing_credentials,
        test_get_campaign_path,
        test_upload_bytes_interface,
        test_upload_from_url_interface,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
