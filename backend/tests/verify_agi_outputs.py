#!/usr/bin/env python3
"""
Verification script for AGI test outputs.

This script validates that all AGI test outputs are present and have valid JSON structure.
Run this after test_agi_service.py to verify test results.
"""
import json
import sys
from pathlib import Path
from typing import List, Tuple


OUTPUT_DIR = Path(__file__).parent / "outputs" / "agi"


def check_file_exists(filename: str) -> Tuple[bool, str]:
    """Check if output file exists"""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        return False, f"File not found: {filename}"

    file_size = filepath.stat().st_size
    if file_size < 10:
        return False, f"File too small: {filename} ({file_size} bytes)"

    return True, f"✅ {filename} ({file_size} bytes)"


def validate_json(filename: str) -> Tuple[bool, str]:
    """Validate JSON structure"""
    filepath = OUTPUT_DIR / filename
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return True, f"✅ Valid JSON: {filename}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {filename} - {str(e)}"
    except Exception as e:
        return False, f"Error reading {filename}: {str(e)}"


def validate_business_context() -> Tuple[bool, str]:
    """Validate business_context.json structure"""
    filepath = OUTPUT_DIR / "business_context.json"
    if not filepath.exists():
        return False, "business_context.json not found"

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        required_keys = ["business_name", "industry", "description"]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            return False, f"Missing keys in business_context.json: {missing_keys}"

        # Check non-empty values
        business_name = data.get("business_name", "")
        industry = data.get("industry", "")
        description = data.get("description", "")

        if not business_name:
            return False, "business_name is empty"
        if not industry:
            return False, "industry is empty"
        if not description or len(description) < 20:
            return False, "description is too short or empty"

        return True, f"✅ Valid business context: {business_name} ({industry})"

    except Exception as e:
        return False, f"Error validating business_context.json: {str(e)}"


def validate_competitors() -> Tuple[bool, str]:
    """Validate competitors.json structure"""
    filepath = OUTPUT_DIR / "competitors.json"
    if not filepath.exists():
        return False, "competitors.json not found"

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        if not isinstance(data, list):
            return False, "competitors.json is not a list"

        if len(data) < 1:
            return False, "No competitors found in competitors.json"

        # Validate first competitor has required fields
        for i, competitor in enumerate(data):
            if not competitor.get("name"):
                return False, f"Competitor {i+1} missing 'name' field"

        return True, f"✅ Valid competitors: {len(data)} competitors found"

    except Exception as e:
        return False, f"Error validating competitors.json: {str(e)}"


def validate_reviews() -> Tuple[bool, str]:
    """Validate reviews.json structure"""
    filepath = OUTPUT_DIR / "reviews.json"
    if not filepath.exists():
        return False, "reviews.json not found"

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        required_keys = ["reviews", "overall_rating", "total_reviews", "sources"]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            return False, f"Missing keys in reviews.json: {missing_keys}"

        reviews = data.get("reviews", [])
        overall_rating = data.get("overall_rating", 0.0)
        total_reviews = data.get("total_reviews", 0)
        sources = data.get("sources", [])

        # Check if rating is valid (0 is acceptable if no reviews found)
        if overall_rating < 0.0 or overall_rating > 5.0:
            return False, f"Invalid overall_rating: {overall_rating}"

        return True, f"✅ Valid reviews: {len(reviews)} reviews, rating {overall_rating}"

    except Exception as e:
        return False, f"Error validating reviews.json: {str(e)}"


def main():
    """Run all validation checks"""
    print("="*70)
    print("AGI TEST OUTPUT VERIFICATION")
    print("="*70)
    print(f"Output Directory: {OUTPUT_DIR}")
    print("="*70)

    if not OUTPUT_DIR.exists():
        print(f"\n❌ Output directory not found: {OUTPUT_DIR}")
        print("   Run test_agi_service.py first to generate outputs")
        sys.exit(1)

    checks = []

    # Check file existence
    print("\n📁 File Existence Checks:")
    files_to_check = [
        "business_context.json",
        "competitors.json",
        "reviews.json"
    ]

    for filename in files_to_check:
        success, message = check_file_exists(filename)
        checks.append(success)
        print(f"   {message}")

    # Check competitor research files
    competitor_research_files = list(OUTPUT_DIR.glob("competitor_research_*.json"))
    if competitor_research_files:
        for filepath in competitor_research_files:
            success, message = check_file_exists(filepath.name)
            checks.append(success)
            print(f"   {message}")

    # Validate JSON structure
    print("\n🔍 JSON Validation Checks:")
    for filename in files_to_check:
        filepath = OUTPUT_DIR / filename
        if filepath.exists():
            success, message = validate_json(filename)
            checks.append(success)
            print(f"   {message}")

    # Validate competitor research files
    if competitor_research_files:
        for filepath in competitor_research_files:
            success, message = validate_json(filepath.name)
            checks.append(success)
            print(f"   {message}")

    # Validate content structure
    print("\n✅ Content Validation Checks:")

    success, message = validate_business_context()
    checks.append(success)
    print(f"   {message}")

    success, message = validate_competitors()
    checks.append(success)
    print(f"   {message}")

    success, message = validate_reviews()
    checks.append(success)
    print(f"   {message}")

    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    passed = sum(checks)
    total = len(checks)
    print(f"Checks Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All validations passed! AGI test outputs are valid.")
        sys.exit(0)
    else:
        failed = total - passed
        print(f"\n❌ {failed} validation(s) failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
