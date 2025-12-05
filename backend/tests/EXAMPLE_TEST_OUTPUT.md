# Example Test Output - AGI Service

This document shows what the test output should look like when running `test_agi_service.py`.

## Command
```bash
cd backend/tests
python test_agi_service.py
```

## Expected Console Output

```
======================================================================
AGI SERVICE TEST SUITE
======================================================================
Testing: Web Research & Review Scraping
Mode: REAL API CALLS (no mocks)
Output Directory: /path/to/backend/tests/outputs/agi
======================================================================
✅ Output directory created: /path/to/backend/tests/outputs/agi

🚀 Starting test execution...


======================================================================
Test: test_agi_scrape_business_context
======================================================================
Input URL: https://www.bluebottlecoffee.com

📡 Initializing AGI service...
🔍 Extracting business context from https://www.bluebottlecoffee.com...
⏱️  This may take 60-120 seconds...

📊 Results:
   Business Name: Blue Bottle Coffee
   Industry: coffee
   Description: Blue Bottle Coffee is a specialty coffee roaster and retailer...

   💾 Saved to: /path/to/outputs/agi/business_context.json
✅ PASS: test_agi_scrape_business_context
   Extracted context for Blue Bottle Coffee in coffee industry

======================================================================
Test: test_agi_discover_competitors
======================================================================

📡 Initializing AGI service...
🔍 Discovering competitors for Blue Bottle Coffee...
⏱️  This may take 120-180 seconds (includes web searches)...

📊 Discovered 3 competitors:
   1. Sightglass Coffee
      Website: https://sightglasscoffee.com
      Rating: 4.5
   2. Ritual Coffee Roasters
      Website: https://ritualcoffee.com
      Rating: 4.6
   3. Philz Coffee
      Website: https://philzcoffee.com
      Rating: 4.4

   💾 Saved to: /path/to/outputs/agi/competitors.json
✅ PASS: test_agi_discover_competitors
   Discovered 3 competitors autonomously

======================================================================
Test: test_agi_scrape_online_reviews
======================================================================
Business: Blue Bottle Coffee
Location: San Francisco, CA

📡 Initializing AGI service...
🔍 Scraping online reviews for Blue Bottle Coffee...
⏱️  This may take 120-180 seconds (includes web searches + scraping)...

📊 Results:
   Overall Rating: 4.4
   Total Reviews: 2,345
   Reviews Scraped: 20
   Sources: Google Maps, Yelp

   Sample Reviews:
   1. [5⭐] Best coffee in the city! The baristas really know their craft and the... (Source: Google Maps)
   2. [4⭐] Great atmosphere and excellent pour-over. A bit pricey but worth it for... (Source: Google Maps)
   3. [5⭐] Love this place! The attention to detail is incredible. Every cup is per... (Source: Yelp)

   💾 Saved to: /path/to/outputs/agi/reviews.json
✅ PASS: test_agi_scrape_online_reviews
   Scraped 20 reviews from 2 sources

======================================================================
Test: test_agi_research_competitor
======================================================================
Researching: Sightglass Coffee
URL: https://sightglasscoffee.com

📡 Initializing AGI service...
🔍 Deep research on Sightglass Coffee...
⏱️  This may take 120-180 seconds...

📊 Results:
   Competitor: Sightglass Coffee
   Pricing Strategy: premium
   Brand Voice: artisanal, community-focused
   Menu Items: 15
   Content Themes: 5

   💾 Saved to: /path/to/outputs/agi/competitor_research_sightglass_coffee.json
✅ PASS: test_agi_research_competitor
   Completed deep research on Sightglass Coffee

======================================================================
Test: test_agi_error_handling
======================================================================

📡 Initializing AGI service...

🧪 Test 1: Invalid URL
   Input: https://this-is-definitely-not-a-real-website-123456789.com
   ✅ Handled gracefully (returned empty/minimal data)

🧪 Test 2: Empty business name for review scraping
   ✅ Handled gracefully (returned empty results)

🧪 Test 3: Invalid location
   ✅ Handled gracefully (returned empty results)

✅ PASS: test_agi_error_handling
   All error scenarios handled gracefully without crashes

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0
⏭️  Skipped: 0
Duration: 487.32s
======================================================================

📁 Output Files:
   - business_context.json (1432 bytes)
   - competitors.json (2784 bytes)
   - reviews.json (4821 bytes)
   - competitor_research_sightglass_coffee.json (2156 bytes)
```

## Verification Output

```bash
cd backend/tests
python verify_agi_outputs.py
```

```
======================================================================
AGI TEST OUTPUT VERIFICATION
======================================================================
Output Directory: /path/to/backend/tests/outputs/agi
======================================================================

📁 File Existence Checks:
   ✅ business_context.json (1432 bytes)
   ✅ competitors.json (2784 bytes)
   ✅ reviews.json (4821 bytes)
   ✅ competitor_research_sightglass_coffee.json (2156 bytes)

🔍 JSON Validation Checks:
   ✅ Valid JSON: business_context.json
   ✅ Valid JSON: competitors.json
   ✅ Valid JSON: reviews.json
   ✅ Valid JSON: competitor_research_sightglass_coffee.json

✅ Content Validation Checks:
   ✅ Valid business context: Blue Bottle Coffee (coffee)
   ✅ Valid competitors: 3 competitors found
   ✅ Valid reviews: 20 reviews, rating 4.4

======================================================================
VERIFICATION SUMMARY
======================================================================
Checks Passed: 12/12

✅ All validations passed! AGI test outputs are valid.
```

## Generated JSON Files

### business_context.json
```json
{
  "business_name": "Blue Bottle Coffee",
  "industry": "coffee",
  "description": "Blue Bottle Coffee is a specialty coffee roaster and retailer committed to sourcing, roasting, and brewing the world's finest coffee.",
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "price_range": "premium",
  "specialties": [
    "specialty coffee",
    "pour-over",
    "single-origin beans"
  ],
  "brand_voice": "elegant, artisanal, quality-focused",
  "target_audience": "coffee enthusiasts, professionals"
}
```

### competitors.json (truncated)
```json
[
  {
    "name": "Sightglass Coffee",
    "website": "https://sightglasscoffee.com",
    "location": "San Francisco, CA",
    "google_rating": 4.5,
    "review_count": 876,
    "social_handles": {
      "instagram": "@sightglasscoffee"
    },
    "description": "Small-batch roastery with multiple SF locations"
  },
  {
    "name": "Ritual Coffee Roasters",
    "website": "https://ritualcoffee.com",
    "location": "San Francisco, CA",
    "google_rating": 4.6,
    "review_count": 1243,
    "social_handles": {
      "instagram": "@ritualcoffeeroasters"
    },
    "description": "Direct-trade coffee with emphasis on sustainability"
  }
]
```

### reviews.json (truncated)
```json
{
  "reviews": [
    {
      "rating": 5,
      "text": "Best coffee in the city! The baristas really know their craft...",
      "date": "2025-01-15",
      "source": "Google Maps",
      "reviewer_name": "Sarah M."
    },
    {
      "rating": 4,
      "text": "Great atmosphere and excellent pour-over. A bit pricey but...",
      "date": "2025-01-10",
      "source": "Google Maps",
      "reviewer_name": "John D."
    }
  ],
  "customer_photos": [
    "https://maps.google.com/photos/..."
  ],
  "overall_rating": 4.4,
  "total_reviews": 2345,
  "sources": [
    "Google Maps",
    "Yelp"
  ]
}
```

## Test Skipped Example

If `AGI_API_KEY` is not set:

```
======================================================================
Test: test_agi_scrape_business_context
======================================================================
Input URL: https://www.bluebottlecoffee.com

⏭️  SKIP: test_agi_scrape_business_context
   Reason: AGI_API_KEY not set in environment

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 0
❌ Failed: 0
⏭️  Skipped: 5
Duration: 0.05s
======================================================================
```

## Test Failure Example

If API returns invalid data:

```
======================================================================
Test: test_agi_scrape_business_context
======================================================================
Input URL: https://www.bluebottlecoffee.com

📡 Initializing AGI service...
🔍 Extracting business context from https://www.bluebottlecoffee.com...

   ⚠️  Missing keys: ['business_name', 'industry']
❌ FAIL: test_agi_scrape_business_context
   Error: Missing required keys in response

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 0
❌ Failed: 1
⏭️  Skipped: 4
Duration: 72.45s

❌ FAILED TESTS:
   - test_agi_scrape_business_context: Missing required keys in response
======================================================================
```

## Notes

- Test output is colorized with emojis for easy reading
- Each test shows progress (🔍, ⏱️, 📊, 💾)
- Pass/fail status clearly indicated (✅/❌)
- Duration tracking helps identify slow tests
- Output files saved for manual inspection
- Verification script provides second layer of validation
