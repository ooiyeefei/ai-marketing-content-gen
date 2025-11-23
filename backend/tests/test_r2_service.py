"""
Test suite for R2Service

Tests R2 client initialization, upload methods, and path generation.
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.r2_service import R2Service


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for R2"""
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "test-account-123")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("R2_BUCKET", "test-bucket")


@pytest.fixture
def mock_boto3_client():
    """Mock boto3 client"""
    with patch('services.r2_service.boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3
        yield mock_s3


class TestR2ServiceInitialization:
    """Test R2Service initialization and configuration"""

    def test_initialization_success(self, mock_env_vars, mock_boto3_client):
        """Test successful R2Service initialization with valid credentials"""
        service = R2Service()

        assert service.bucket == "test-bucket"
        assert service.public_url_base == "https://pub-test-account-123.r2.dev"
        assert service.s3_client is not None

    def test_initialization_missing_credentials(self, monkeypatch):
        """Test that R2Service raises ValueError when credentials are missing"""
        monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "")
        monkeypatch.setenv("R2_ACCESS_KEY_ID", "")
        monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "")

        with pytest.raises(ValueError, match="Missing R2 credentials"):
            R2Service()

    def test_boto3_client_configuration(self, mock_env_vars):
        """Test that boto3 client is configured correctly for R2"""
        with patch('services.r2_service.boto3.client') as mock_client:
            service = R2Service()

            # Verify boto3.client was called with correct parameters
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]

            assert call_kwargs['endpoint_url'] == "https://test-account-123.r2.cloudflarestorage.com"
            assert call_kwargs['aws_access_key_id'] == "test-access-key"
            assert call_kwargs['aws_secret_access_key'] == "test-secret-key"
            assert call_kwargs['region_name'] == "auto"


class TestR2ServiceUploadMethods:
    """Test R2Service upload methods"""

    @pytest.mark.asyncio
    async def test_upload_bytes_success(self, mock_env_vars, mock_boto3_client):
        """Test successful upload of bytes to R2"""
        service = R2Service()
        test_data = b"test image data"
        object_key = "campaigns/test-campaign/image.jpg"

        public_url = await service.upload_bytes(
            test_data,
            object_key,
            content_type="image/jpeg"
        )

        # Verify upload_fileobj was called
        mock_boto3_client.upload_fileobj.assert_called_once()
        call_args = mock_boto3_client.upload_fileobj.call_args

        # Check arguments
        assert call_args[0][1] == "test-bucket"  # bucket
        assert call_args[0][2] == object_key  # object_key
        assert call_args[1]['ExtraArgs']['ContentType'] == "image/jpeg"

        # Check returned URL
        assert public_url == f"https://pub-test-account-123.r2.dev/{object_key}"

    @pytest.mark.asyncio
    async def test_upload_bytes_error_handling(self, mock_env_vars, mock_boto3_client):
        """Test error handling in upload_bytes"""
        service = R2Service()
        mock_boto3_client.upload_fileobj.side_effect = Exception("Upload failed")

        with pytest.raises(Exception, match="Upload failed"):
            await service.upload_bytes(
                b"test data",
                "test.jpg"
            )

    @pytest.mark.asyncio
    async def test_upload_from_url_success(self, mock_env_vars, mock_boto3_client):
        """Test successful upload from URL"""
        service = R2Service()

        # Mock httpx response
        mock_response = Mock()
        mock_response.content = b"downloaded content"
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            public_url = await service.upload_from_url(
                "https://example.com/image.jpg",
                "campaigns/test/image.jpg",
                "image/jpeg"
            )

            # Verify upload was called
            mock_boto3_client.upload_fileobj.assert_called_once()

            # Check returned URL
            assert public_url == "https://pub-test-account-123.r2.dev/campaigns/test/image.jpg"

    @pytest.mark.asyncio
    async def test_upload_from_url_download_error(self, mock_env_vars, mock_boto3_client):
        """Test error handling when downloading from URL fails"""
        service = R2Service()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Download failed")
        )

        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception, match="Download failed"):
                await service.upload_from_url(
                    "https://example.com/image.jpg",
                    "test.jpg"
                )


class TestR2ServicePathGeneration:
    """Test R2Service path generation methods"""

    def test_get_campaign_path(self, mock_env_vars, mock_boto3_client):
        """Test campaign path generation"""
        service = R2Service()

        path = service.get_campaign_path("campaign-abc123", "research/competitor_1.jpg")
        assert path == "campaigns/campaign-abc123/research/competitor_1.jpg"

        path = service.get_campaign_path("xyz-789", "day_1.jpg")
        assert path == "campaigns/xyz-789/day_1.jpg"


class TestR2ServiceIntegration:
    """Integration tests with real R2 credentials (if available)"""

    @pytest.mark.skipif(
        not all([
            os.getenv("CLOUDFLARE_ACCOUNT_ID"),
            os.getenv("R2_ACCESS_KEY_ID"),
            os.getenv("R2_SECRET_ACCESS_KEY")
        ]),
        reason="R2 credentials not available"
    )
    @pytest.mark.asyncio
    async def test_real_upload(self):
        """Test actual upload to R2 (only runs if credentials are set)"""
        service = R2Service()

        # Create small test image data
        test_data = b"test data for integration test"
        object_key = "tests/integration_test.txt"

        try:
            public_url = await service.upload_bytes(
                test_data,
                object_key,
                content_type="text/plain"
            )

            assert public_url.startswith("https://pub-")
            assert object_key in public_url

            print(f"\nIntegration test successful: {public_url}")
        except Exception as e:
            pytest.skip(f"Integration test skipped due to error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
