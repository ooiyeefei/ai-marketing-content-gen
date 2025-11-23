#!/usr/bin/env python3
"""Simple test for Social Service initialization"""
import sys
from services.social_service import SocialService

def test_social_initialization():
    """Test Social service initialization"""
    try:
        service = SocialService()
        print("✓ Social Service initialized")

        # Verify the service has the expected methods
        assert hasattr(service, 'get_google_reviews')
        assert hasattr(service, 'get_facebook_insights')
        assert hasattr(service, 'get_instagram_insights')
        assert hasattr(service, 'get_location_trends')
        print("✓ All expected methods present")

        # Verify environment variables are read (may be None)
        print(f"  - GMB API Key: {'configured' if service.gmb_api_key else 'not configured'}")
        print(f"  - Facebook Token: {'configured' if service.facebook_token else 'not configured'}")
        print(f"  - Instagram Token: {'configured' if service.instagram_token else 'not configured'}")
        print(f"  - Trends API Key: {'configured' if service.trends_api_key else 'not configured'}")

        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_social_initialization()
    sys.exit(0 if success else 1)
