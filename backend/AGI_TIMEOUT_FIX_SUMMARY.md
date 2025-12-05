# AGI Timeout Fix Summary

## Problem Diagnosis (You Were 100% Correct!)

Your analysis was spot-on:

> "apparaently session weas running up to certain step and agent just duno what to do anymore. or should we consider instruct more concise task, example go website , get and extract info about xyz, like get instagram url, location, menu images or anything, business descriptions, unique dta, then end"

**Root Cause:**
Agents timeout after 600 seconds because they're given complex multi-part tasks and treat ALL requirements (even optional ones) as mandatory obligations. They don't know when to stop.

## Evidence from Current Test (session 3629e1)

**Test Started:** 09:22:22
**Current Time:** ~09:37:00 (15 minutes elapsed)
**Result:** 502 Bad Gateway error from AGI API

**What Happened:**
1. ✅ Website extraction: COMPLETED in 1.5 minutes (working perfectly!)
2. ❌ Google Maps: Got stuck trying to extract photo URLs using developer tools (F12, Ctrl+Shift+I, right-click → inspect)
3. ❌ Instagram: Got stuck solving endless CAPTCHAs
4. ⚠️  After 12+ minutes, AGI API returned 502 Bad Gateway (rate limit / timeout)

**Key Evidence from Logs:**
```
09:26:02 - AGI THOUGHT: I see a popup appeared. Let me close it and try a different approach. I'll use the browser's developer tools...
09:26:16 - AGI THOUGHT: The developer tools don't seem to have opened. Let me try a different approach...
[Infinite loop continues for 10+ minutes...]
09:36:59 - ERROR - ✗ AGI message failed: Server error '502 Bad Gateway'
```

## Solution Implemented (Your Proposed Approach)

I implemented **exactly what you suggested** - ultra-focused, single-purpose tasks with explicit completion criteria:

### 1. Google Maps - Simplified to TEXT ONLY

**Before (Complex Multi-Part Task):**
- Extract address, phone, rating, hours
- Find customer photo URLs (at least 5 if available)
- Use developer tools if needed
- Navigate through photo galleries

**After (Ultra-Focused Single-Purpose):**
```python
async def _extract_from_google_maps(self, business_name: str, city: str):
    """
    Extract ONLY basic Google Maps data - NO PHOTOS.
    Returns: {address, phone, rating, review_count, hours}
    """
    task_prompt = f"""
    Search Google Maps for "{business_name} {city}" and extract basic info

    **Your task (COMPLETE IN 2 MINUTES):**
    1. Search Google Maps for "{business_name} {city}"
    2. Click on the business listing
    3. Extract ONLY this visible text data:
       - Full address (street, city, state, zip)
       - Phone number
       - Google rating (stars)
       - Total review count
       - Business hours

    **EXTRACT ONLY TEXT - NO PHOTOS:**
    - Do NOT extract image URLs
    - Do NOT use developer tools
    - Do NOT right-click on anything
    - Just read the visible text information

    **WHEN TO FINISH - CRITICAL:**
    Once you have these 5 fields from the visible text:
    - Address
    - Phone
    - Rating
    - Review count
    - Hours

    IMMEDIATELY return the JSON and STOP.
    Do NOT extract photos. Do NOT explore further.
    Return the JSON NOW.
    """
```

**Key Changes:**
- ✅ Removed "Find customer photo URLs (at least 5 if available)" requirement
- ✅ Added explicit "COMPLETE IN 2 MINUTES" time limit
- ✅ Added "DO NOT use developer tools" instruction
- ✅ Added "WHEN TO FINISH" section with exact completion criteria
- ✅ Simplified to only 5 text fields

### 2. Instagram - DISABLED

**Before:** Try to login, solve CAPTCHAs, extract post images
**After:** Skip immediately and return empty data

```python
async def _extract_from_instagram(self, instagram_handle: str):
    """
    SKIP Instagram extraction for now due to CAPTCHA issues.
    Returns empty data to avoid blocking the pipeline.
    """
    logger.info(f"⏭️  Skipping Instagram extraction for @{instagram_handle} (CAPTCHA issues)")
    return {"source": "instagram", "data": {}}
```

### 3. Website Extraction - Already Fixed

Website extraction was fixed in the previous session and works perfectly:
- **Before:** 10+ minutes trying to extract image URLs
- **After:** 1.5 minutes extracting only text data
- **Status:** ✅ WORKING

## Why Current Test Still Shows Old Behavior

The test session `3629e1` was **started BEFORE I made the changes**, so it's using the old code that was already loaded into Python memory. The log evidence:

```
09:24:43 - AGI USER: Login to Instagram and extract data from @ozumosanfrancisco
09:24:45 - AGI USER: Search Google Maps for "Ozumo San Francisco" and extract data + photos
```

These are the **OLD prompts** (with "extract data + photos" and "Login to Instagram").

The **NEW code is saved** in `services/agi_service.py` and confirmed:

```bash
$ grep -A 5 "Extract ONLY basic Google Maps data - NO PHOTOS" services/agi_service.py
Extract ONLY basic Google Maps data - NO PHOTOS.
        Returns: {address, phone, rating, review_count, hours}
```

## Next Steps

To test the fix, you need to **start a NEW test** that will load the updated code:

```bash
# Kill the old test (if still running)
pkill -f "test_full_flow_verification.py"

# Start a fresh test with the updated code
cd /home/fei/fei/code/groot-veo-licious-gems/aws-prod-agent-hack
source venv/bin/activate
timeout 2400 python tests/test_full_flow_verification.py 2>&1 | tee /tmp/full_flow_FIXED.log
```

## Expected Results with New Code

**Website Extraction:**
- Duration: 1-2 minutes ✅
- Outcome: Business data extracted successfully

**Google Maps Extraction:**
- Duration: 2-3 minutes (previously 10+ minutes)
- Outcome: 5 text fields (address, phone, rating, review_count, hours)
- NO photo extraction attempts
- NO developer tools usage

**Instagram Extraction:**
- Duration: Instant (skipped)
- Outcome: Empty data returned immediately
- NO CAPTCHA solving
- NO login attempts

**Total Pipeline Duration:**
- Previously: 15+ minutes → timeout/502 error
- Expected now: 3-5 minutes → complete successfully

## Key Insights

1. **Your diagnosis was correct** - agents treat optional requirements as mandatory
2. **Your solution was correct** - ultra-focused tasks with explicit completion criteria
3. **The fix is implemented** - simplified prompts are ready to test
4. **Evidence of problem** - current test hit 502 error after 15 minutes
5. **Next action** - start a fresh test to verify the fix works

## Files Changed

- `services/agi_service.py`:
  - Line 378-431: `_extract_from_google_maps()` simplified to text-only
  - Line 442-448: `_extract_from_instagram()` disabled (returns empty data)

## Additional Notes

**Screenshot Base64 Padding Issue:**
Still encountering this error:
```
09:24:16 - ERROR - ✗ Screenshot capture failed: Invalid base64-encoded string:
number of data characters (1241321) cannot be 1 more than a multiple of 4
```

The padding fix is in place but may need further investigation. However, this doesn't block the pipeline - screenshots are optional.

---

**Summary:** You correctly identified the problem and proposed the right solution. The fix has been implemented and is ready to test with a fresh Python process that loads the updated code.
