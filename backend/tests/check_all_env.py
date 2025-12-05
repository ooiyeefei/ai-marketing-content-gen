#!/usr/bin/env python3
"""
Environment Variables Checker for Orchestrator Tests

Verifies all required environment variables are set before running tests.
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_env_var(name: str, required: bool = True) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(name)

    if value:
        # Mask sensitive values
        if "KEY" in name or "TOKEN" in name or "SECRET" in name:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"{GREEN}✓{RESET} {name}: {masked}")
        else:
            print(f"{GREEN}✓{RESET} {name}: {value}")
        return True
    else:
        if required:
            print(f"{RED}✗{RESET} {name}: NOT SET (REQUIRED)")
        else:
            print(f"{YELLOW}⚠{RESET} {name}: NOT SET (OPTIONAL)")
        return not required


def main():
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 80)

    # Track overall status
    all_required_set = True

    # ========================================================================
    # Core Services (REQUIRED)
    # ========================================================================

    print(f"\n{BLUE}Core Services (REQUIRED){RESET}")
    print("-" * 80)

    required_vars = [
        "CONVEX_URL",
        "AGI_SERVICE_URL",
        "GEMINI_API_KEY",
        "MINIMAX_API_KEY",
    ]

    for var in required_vars:
        if not check_env_var(var, required=True):
            all_required_set = False

    # ========================================================================
    # Storage Services (REQUIRED)
    # ========================================================================

    print(f"\n{BLUE}Storage Services (REQUIRED){RESET}")
    print("-" * 80)

    storage_vars = [
        "R2_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET_NAME",
    ]

    for var in storage_vars:
        if not check_env_var(var, required=True):
            all_required_set = False

    # ========================================================================
    # Social Services (OPTIONAL - Agent 2 features)
    # ========================================================================

    print(f"\n{BLUE}Social Services (OPTIONAL){RESET}")
    print("-" * 80)
    print("Note: Required for full Agent 2 performance analytics")

    optional_vars = [
        "FACEBOOK_PAGE_ID",
        "FACEBOOK_ACCESS_TOKEN",
        "INSTAGRAM_ACCOUNT_ID",
    ]

    social_complete = True
    for var in optional_vars:
        if not check_env_var(var, required=False):
            social_complete = False

    if social_complete:
        print(f"\n{GREEN}✓ Social services fully configured{RESET}")
    else:
        print(f"\n{YELLOW}⚠ Social services partially configured - Agent 2 will skip performance analytics{RESET}")

    # ========================================================================
    # Other Optional Services
    # ========================================================================

    print(f"\n{BLUE}Other Services (OPTIONAL){RESET}")
    print("-" * 80)

    other_optional = [
        "GOOGLE_PLACES_API_KEY",  # For review fetching
        "SANITY_PROJECT_ID",  # For CMS sync
        "SANITY_DATASET",
        "SANITY_API_TOKEN",
    ]

    for var in other_optional:
        check_env_var(var, required=False)

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if all_required_set:
        print(f"{GREEN}✓ All required environment variables are set{RESET}")
        print(f"\n{GREEN}You can run orchestrator tests!{RESET}")
        print("\nRun tests:")
        print("  cd backend/tests")
        print("  python test_orchestrator.py")
        return 0
    else:
        print(f"{RED}✗ Some required environment variables are missing{RESET}")
        print(f"\n{RED}Cannot run orchestrator tests until all required variables are set{RESET}")
        print("\nSet missing variables:")
        print("  export VARIABLE_NAME=value")
        print("\nOr add to .env file:")
        print("  echo 'VARIABLE_NAME=value' >> .env")
        return 1


if __name__ == "__main__":
    sys.exit(main())
