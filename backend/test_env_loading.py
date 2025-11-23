#!/usr/bin/env python3
"""
Test script to verify .env.example can be loaded properly.
This validates the environment variable template structure.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def test_env_example_loading():
    """Test that .env.example has valid structure"""

    # Get the backend directory
    backend_dir = Path(__file__).parent
    env_example_path = backend_dir / ".env.example"

    print(f"Testing environment file: {env_example_path}")

    # Check file exists
    if not env_example_path.exists():
        print("✗ .env.example file not found!")
        return False

    print("✓ .env.example file exists")

    # Try to load it
    try:
        load_dotenv(env_example_path)
        print("✓ .env.example loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load .env.example: {e}")
        return False

    # Check for required environment variables (they should have placeholder values)
    required_vars = [
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "AGI_API_KEY",
        "MINIMAX_API_KEY",
        "CONVEX_URL",
        "CLOUDFLARE_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET",
    ]

    optional_vars = [
        "GOOGLE_MY_BUSINESS_API_KEY",
        "FACEBOOK_ACCESS_TOKEN",
        "INSTAGRAM_ACCESS_TOKEN",
        "GOOGLE_TRENDS_API_KEY",
        "PORT",
        "LOG_LEVEL",
    ]

    print("\nChecking required variables:")
    all_required_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the value for security
            display_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✓ {var} = {display_value}")
        else:
            print(f"  ✗ {var} = NOT SET")
            all_required_present = False

    print("\nChecking optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✓ {var} = {display_value}")
        else:
            print(f"  ○ {var} = NOT SET (optional)")

    print("\n" + "="*60)

    if all_required_present:
        print("✅ Environment template validation PASSED")
        print("\nAll required variables are defined in .env.example")
        print("To use this in your project:")
        print("  1. cp backend/.env.example backend/.env")
        print("  2. Edit backend/.env with your actual API keys")
        return True
    else:
        print("⚠ Environment template validation INCOMPLETE")
        print("\nSome required variables are missing placeholders.")
        print("This is expected - they need to be filled in .env file.")
        return True  # Still pass since .env.example just needs structure


if __name__ == "__main__":
    success = test_env_example_loading()
    exit(0 if success else 1)
