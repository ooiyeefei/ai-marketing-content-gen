#!/usr/bin/env python3
"""
Environment Variable Checker for Social Service Tests

Validates that required and optional environment variables are configured
before running social service tests.
"""
import os
import sys


def check_env():
    """Check all environment variables for social service tests"""
    print("="*80)
    print("SOCIAL SERVICE - ENVIRONMENT VARIABLE CHECK")
    print("="*80)

    # Critical environment variables
    critical_vars = {
        "AGI_API_KEY": "AGI API (required for review scraping fallback)"
    }

    # Optional environment variables
    optional_vars = {
        "GOOGLE_MY_BUSINESS_API_KEY": "Google My Business API",
        "FACEBOOK_ACCESS_TOKEN": "Facebook Marketing API",
        "INSTAGRAM_ACCESS_TOKEN": "Instagram Graph API",
        "GOOGLE_TRENDS_API_KEY": "Google Trends API",
        "FACEBOOK_PAGE_ID": "Facebook Page ID (for testing)",
        "INSTAGRAM_ACCOUNT_ID": "Instagram Account ID (for testing)"
    }

    print("\nCRITICAL (required for tests to pass):")
    print("-" * 80)

    critical_missing = []
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            # Show first 10 chars only for security
            preview = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✓ {var}: {preview}")
            print(f"    Description: {description}")
        else:
            print(f"  ✗ {var}: NOT SET")
            print(f"    Description: {description}")
            critical_missing.append(var)

    print("\nOPTIONAL (tests will skip if missing):")
    print("-" * 80)

    optional_present = []
    optional_missing = []
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            preview = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✓ {var}: {preview}")
            print(f"    Description: {description}")
            optional_present.append(var)
        else:
            print(f"  - {var}: NOT SET (will skip)")
            print(f"    Description: {description}")
            optional_missing.append(var)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    print(f"\nCritical: {len(critical_vars) - len(critical_missing)}/{len(critical_vars)} configured")
    print(f"Optional: {len(optional_present)}/{len(optional_vars)} configured")

    if critical_missing:
        print("\n⚠ MISSING CRITICAL VARIABLES:")
        for var in critical_missing:
            print(f"  - {var}")
        print("\nTo configure:")
        print("  export AGI_API_KEY=your_key_here")
        print("\nTests will FAIL without these variables.")
        return False
    else:
        print("\n✓ All critical variables configured!")

        if optional_missing:
            print(f"\n⚠ {len(optional_missing)} optional variable(s) not configured:")
            for var in optional_missing:
                print(f"  - {var}")
            print("\nThese tests will be SKIPPED (not failed).")
        else:
            print("\n✓ All optional variables configured!")

        print("\nReady to run tests:")
        print("  python tests/test_social_service.py")
        return True


if __name__ == "__main__":
    success = check_env()
    print("\n" + "="*80)
    exit(0 if success else 1)
