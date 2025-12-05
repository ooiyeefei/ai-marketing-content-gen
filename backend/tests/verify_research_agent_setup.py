#!/usr/bin/env python3
"""
Pre-flight check script for Research Agent tests

Verifies:
1. All required environment variables are set
2. All Python dependencies are installed
3. Services are initialized correctly
4. Output directories exist

Run this before executing test_research_agent.py
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_mark(passed):
    return f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"

def log(message, status=None):
    if status is True:
        print(f"{GREEN}✓{RESET} {message}")
    elif status is False:
        print(f"{RED}✗{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"  {message}")

print("\n" + "=" * 70)
print("Research Agent Tests - Pre-Flight Check")
print("=" * 70 + "\n")

# ============================================================================
# Check 1: Environment Variables
# ============================================================================

print("1. Checking Environment Variables...")

required_vars = {
    "AGI_API_KEY": "AGI API for web research",
    "CONVEX_URL": "Convex database",
    "CLOUDFLARE_ACCOUNT_ID": "Cloudflare R2 storage",
    "R2_ACCESS_KEY_ID": "R2 access key",
    "R2_SECRET_ACCESS_KEY": "R2 secret key",
    "R2_BUCKET": "R2 bucket name"
}

env_passed = True
for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        masked = value[:8] + "..." if len(value) > 8 else "***"
        log(f"{var}: {masked} ({description})", True)
    else:
        log(f"{var}: Missing! ({description})", False)
        env_passed = False

if not env_passed:
    log("\n⚠️ Some environment variables are missing!", "warning")
    log("Please add them to backend/.env", "warning")
    log("See backend/.env.example for reference", "warning")

# ============================================================================
# Check 2: Python Dependencies
# ============================================================================

print("\n2. Checking Python Dependencies...")

dependencies = [
    ("httpx", "HTTP client for API calls"),
    ("pydantic", "Data validation"),
    ("asyncio", "Async support"),
    ("uuid", "ID generation"),
    ("json", "JSON parsing"),
    ("pathlib", "File paths"),
    ("datetime", "Timestamps")
]

deps_passed = True
for module, description in dependencies:
    try:
        __import__(module)
        log(f"{module}: Installed ({description})", True)
    except ImportError:
        log(f"{module}: Missing! ({description})", False)
        deps_passed = False

# Check Convex separately (might need special installation)
try:
    __import__("convex")
    log("convex: Installed (Convex database client)", True)
except ImportError:
    log("convex: Not installed - install with: pip install convex", False)
    deps_passed = False

if not deps_passed:
    log("\n⚠️ Some dependencies are missing!", "warning")
    log("Install with: pip install -r backend/requirements.txt", "warning")

# ============================================================================
# Check 3: Module Imports
# ============================================================================

print("\n3. Checking Module Imports...")

sys.path.insert(0, str(Path(__file__).parent.parent))

imports_passed = True

try:
    from agents.research_agent import ResearchAgent
    log("ResearchAgent: Importable", True)
except Exception as e:
    log(f"ResearchAgent: Cannot import - {e}", False)
    imports_passed = False

try:
    from services.agi_service import AGIService
    log("AGIService: Importable", True)
except Exception as e:
    log(f"AGIService: Cannot import - {e}", False)
    imports_passed = False

try:
    from services.convex_service import ConvexService
    log("ConvexService: Importable", True)
except Exception as e:
    log(f"ConvexService: Cannot import - {e}", False)
    imports_passed = False

try:
    from services.r2_service import R2Service
    log("R2Service: Importable", True)
except Exception as e:
    log(f"R2Service: Cannot import - {e}", False)
    imports_passed = False

try:
    from models import ResearchOutput
    log("ResearchOutput: Importable", True)
except Exception as e:
    log(f"ResearchOutput: Cannot import - {e}", False)
    imports_passed = False

# ============================================================================
# Check 4: Output Directories
# ============================================================================

print("\n4. Checking Output Directories...")

output_dir = Path(__file__).parent / "outputs" / "agents" / "research"
output_dir.mkdir(parents=True, exist_ok=True)

if output_dir.exists():
    log(f"Output directory exists: {output_dir}", True)
else:
    log(f"Output directory created: {output_dir}", True)

# ============================================================================
# Check 5: Service Initialization (if env vars present)
# ============================================================================

if env_passed and imports_passed:
    print("\n5. Testing Service Initialization...")

    try:
        from services.agi_service import AGIService
        agi = AGIService()
        log("AGIService: Initialized successfully", True)
    except Exception as e:
        log(f"AGIService: Initialization failed - {e}", False)

    try:
        from services.convex_service import ConvexService
        convex = ConvexService()
        log("ConvexService: Initialized successfully", True)
    except Exception as e:
        log(f"ConvexService: Initialization failed - {e}", False)

    try:
        from services.r2_service import R2Service
        r2 = R2Service()
        log("R2Service: Initialized successfully", True)
    except Exception as e:
        log(f"R2Service: Initialization failed - {e}", False)

# ============================================================================
# Final Summary
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

all_passed = env_passed and deps_passed and imports_passed

if all_passed:
    print(f"{GREEN}✅ ALL CHECKS PASSED{RESET}")
    print("\nYou're ready to run Research Agent tests!")
    print("\nRun tests with:")
    print("  cd backend/tests")
    print("  python test_research_agent.py")
    exit_code = 0
else:
    print(f"{RED}❌ SOME CHECKS FAILED{RESET}")
    print("\nPlease fix the issues above before running tests.")

    if not env_passed:
        print("\n📋 To fix environment variables:")
        print("  1. Copy backend/.env.example to backend/.env")
        print("  2. Edit backend/.env and add your API keys")

    if not deps_passed:
        print("\n📋 To fix dependencies:")
        print("  pip install -r backend/requirements.txt")

    if not imports_passed:
        print("\n📋 To fix imports:")
        print("  Make sure you're in the correct directory")
        print("  Check that all service files exist in backend/services/")

    exit_code = 1

print("=" * 70 + "\n")
sys.exit(exit_code)
