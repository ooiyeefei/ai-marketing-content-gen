#!/usr/bin/env python3
"""
Quick environment check for BrandMind AI tests
"""
import os
import sys
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key not in os.environ:
                    os.environ[key] = value

print("=" * 70)
print("BrandMind AI - Environment Check")
print("=" * 70)
print()

# Critical keys for tests
critical = {
    "GEMINI_API_KEY": "Gemini AI for analysis and generation",
    "AGI_API_KEY": "AGI API for web research",
    "MINIMAX_API_KEY": "MiniMax for image/video generation",
    "CONVEX_URL": "Convex database URL",
    "CLOUDFLARE_ACCOUNT_ID": "Cloudflare account for R2",
    "R2_ACCESS_KEY_ID": "R2 storage access key",
    "R2_SECRET_ACCESS_KEY": "R2 storage secret key",
    "R2_BUCKET": "R2 storage bucket name",
}

# Optional keys (graceful degradation)
optional = {
    "GOOGLE_MY_BUSINESS_API_KEY": "Google My Business (AGI fallback available)",
    "FACEBOOK_ACCESS_TOKEN": "Facebook insights (optional)",
    "INSTAGRAM_ACCESS_TOKEN": "Instagram insights (optional)",
    "GOOGLE_TRENDS_API_KEY": "Google Trends (optional)",
}

missing_critical = []
missing_optional = []

print("CRITICAL APIs (required for tests):")
print("-" * 70)
for key, description in critical.items():
    present = bool(os.getenv(key))
    status = "✓" if present else "✗"
    print(f"  {status} {key:30s} {description}")
    if not present:
        missing_critical.append(key)
print()

print("OPTIONAL APIs (graceful degradation):")
print("-" * 70)
for key, description in optional.items():
    present = bool(os.getenv(key))
    status = "✓" if present else "○"
    print(f"  {status} {key:30s} {description}")
    if not present:
        missing_optional.append(key)
print()

# Check for alternative variable names
print("VARIABLE NAME ALIASES:")
print("-" * 70)
aliases = [
    ("CONVEX_URL", "VITE_CONVEX_URL"),
    ("R2_BUCKET", "R2_BUCKET_NAME"),
]

for expected, alternative in aliases:
    has_expected = bool(os.getenv(expected))
    has_alternative = bool(os.getenv(alternative))

    if not has_expected and has_alternative:
        print(f"  ⚠ Found {alternative} but tests expect {expected}")
        print(f"    Add this to .env: {expected}={os.getenv(alternative)}")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

if not missing_critical:
    print("✓ All critical API keys present")
else:
    print(f"✗ Missing {len(missing_critical)} critical keys:")
    for key in missing_critical:
        print(f"  - {key}")
    print()
    print("ACTION REQUIRED:")

    # Check for aliases
    if not os.getenv("CONVEX_URL") and os.getenv("VITE_CONVEX_URL"):
        print(f"  1. Add to .env: CONVEX_URL={os.getenv('VITE_CONVEX_URL')}")

    if not os.getenv("R2_BUCKET") and os.getenv("R2_BUCKET_NAME"):
        print(f"  2. Add to .env: R2_BUCKET={os.getenv('R2_BUCKET_NAME')}")

    if not os.getenv("GEMINI_API_KEY"):
        print("  3. Get GEMINI_API_KEY from: https://aistudio.google.com/app/apikey")
        print("     Add to .env: GEMINI_API_KEY=your-key-here")

    if not os.getenv("CLOUDFLARE_ACCOUNT_ID"):
        print("  4. Get CLOUDFLARE_ACCOUNT_ID from: https://dash.cloudflare.com/")
        print("     Add to .env: CLOUDFLARE_ACCOUNT_ID=your-account-id")

if missing_optional:
    print()
    print(f"○ Missing {len(missing_optional)} optional keys (tests will skip gracefully):")
    for key in missing_optional:
        print(f"  - {key}")

print()
print("=" * 70)

if missing_critical:
    print("STATUS: ✗ NOT READY - Add missing critical keys")
    sys.exit(1)
else:
    print("STATUS: ✓ READY TO RUN TESTS")
    sys.exit(0)
