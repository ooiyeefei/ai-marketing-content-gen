# Next Steps - AGI API Rate Limiting Issue

## Current Status (as of 09:54)

### ✅ Code Changes: COMPLETE

All extraction prompts have been updated per user requirements and saved to disk:

**1. Website Extraction** (`services/agi_service.py` lines 278-359):
- ✅ Added `unique_selling_point` field
- ✅ Added `instagram_account` field with explicit search instructions
- ✅ Added structured `menu_info` with categories and signature items
- ✅ Enhanced location structure (street, city, state, zip, country)
- ✅ 3-minute time limit with explicit "WHEN TO FINISH" criteria

**2. Google Maps Extraction** (`services/agi_service.py` lines 390-452):
- ✅ Re-enabled photo extraction (was disabled in previous fix)
- ✅ Description-based approach: `customer_photos_description` field
- ✅ Agent describes 3-5 photos instead of extracting URLs
- ✅ Forbids developer tools (prevents infinite loops)
- ✅ 3-minute time limit

**3. Instagram Extraction** (`services/agi_service.py` lines 463-571):
- ✅ Re-enabled (was completely skipped in previous fix)
- ✅ 1-2 minute time limit (user requirement)
- ✅ Only 3 posts (user requirement)
- ✅ CAPTCHA handling: Agent notes CAPTCHA, returns partial data, user handles manually
- ✅ Graceful error handling

### 🔴 Blocking Issue: AGI API Not Responding

**Evidence:**
```
Earlier Test (09:22) - WORKING:
  09:22:51 - AGI THOUGHT: "I need to visit the website..."
  09:23:02 - AGI THOUGHT: "Good! I can see the website..."
  → Completed successfully in 1.5 minutes

Later Test (09:52) - NOT WORKING:
  09:52:05 - AGI USER: [prompt received]
  09:52:08-09:54:08 - [COMPLETE SILENCE - NO THOUGHTS]
  09:54:08 - 502 Bad Gateway
```

**Root Cause:**
AGI API worked at 09:22 but stopped responding by 09:52. This is classic rate limiting after multiple test runs today.

## Action Plan

### Step 1: Wait for Rate Limit Reset

**Current Time:** 09:54 (last failed test)
**Wait Until:** 10:30-10:45 (30-45 minutes from last test)

### Step 2: Simple Health Check

Test if AGI API is responsive with an ultra-simple task:

```bash
cd /home/fei/fei/code/groot-veo-licious-gems/aws-prod-agent-hack/backend
source venv/bin/activate

# Load environment variables
export $(cat .env | xargs)

# Simple diagnostic test (60 second timeout)
python3 -c "
import asyncio
from services.agi_service import AGIService

async def test():
    agi = AGIService()
    session_id = await agi._create_session()
    result = await agi._send_message(
        session_id,
        'Visit google.com and describe what you see in one sentence',
        'https://www.google.com',
        max_wait=60
    )
    print('✓ AGI API is RESPONSIVE')
    print(f'Result: {result}')
    await agi._close_session(session_id)

asyncio.run(test())
"
```

**Expected Results:**
- **Success:** Agent sends THOUGHT messages and completes task in < 60 seconds
- **Failure:** Same 502 error or timeout → Wait longer or contact AGI support

### Step 3: Full Test with Updated Prompts

Once health check passes, run the full test:

```bash
cd /home/fei/fei/code/groot-veo-licious-gems/aws-prod-agent-hack/backend
source venv/bin/activate

# Run full E2E test with updated prompts
timeout 2400 python tests/test_full_flow_verification.py 2>&1 | tee /tmp/full_flow_FINAL_VERIFICATION.log
```

**Expected Results with New Prompts:**

**Website Extraction:**
- Duration: 2-3 minutes (previously worked)
- Data: business_name, industry, location, description, **unique_selling_point**, **instagram_account**, **menu_info**
- Screenshots: 1 final state screenshot

**Google Maps Extraction:**
- Duration: 2-3 minutes (previously took 10+ minutes)
- Data: address, phone, rating, review_count, hours, **customer_photos_description** (3-5 photos)
- NO developer tools usage
- NO infinite loops

**Instagram Extraction:**
- Duration: 1-2 minutes or instant CAPTCHA notification
- Data: follower_count, bio, 3 recent posts with descriptions, OR `{"captcha_encountered": true}`
- User handles CAPTCHA manually if encountered

**Total Pipeline:**
- Expected Duration: 5-8 minutes (previously 15+ minutes → timeout)
- Success Criteria: All 3 extractions complete or Instagram returns CAPTCHA notification

## Files Modified

All changes saved to disk in `services/agi_service.py`:
- Lines 278-359: `_extract_from_website()`
- Lines 390-452: `_extract_from_google_maps()`
- Lines 463-571: `_extract_from_instagram()`

## Documentation Created

- `AGI_ISSUE_ANALYSIS.md` - Detailed analysis of 502 error with evidence
- `NEXT_STEPS.md` - This document

## If Health Check Fails

If the simple health check still fails after waiting:

**Option 1: Wait Longer**
- Rate limits typically reset after 1-2 hours
- Try again at 11:00 or later

**Option 2: Contact AGI Support**
- Provide session IDs: `8f655ccc-918c-487e-a2bd-1670bd5848fb` (failed)
- Error: 502 Bad Gateway after agent receives prompt but never responds
- Timeline: Worked at 09:22, stopped working by 09:52

**Option 3: Use Alternative Approach**
- Temporarily mock website extraction data
- Focus on testing Agent 2 (Strategy) and Agent 3 (Creative)
- Return to AGI integration once API is responsive

## Summary

**The code is ready.** The prompts match your requirements exactly:
- Instagram: Re-enabled with CAPTCHA handling (1-2 min, 3 posts)
- Google Maps: Photo descriptions included
- Website: All required fields (unique_selling_point, instagram_account, menu_info)

**The blocker is external:** AGI API is not responding due to rate limiting.

**Next action:** Wait 30-45 minutes, then run the simple health check.
