# AGI API Issue Analysis

## Problem Summary

AGI agents consistently fail after 2-3 minutes with `502 Bad Gateway` errors. The agent receives the extraction task but **never sends any THOUGHT or ACTION messages back**.

## Evidence from Latest Test (Session 8f655ccc-918c-487e-a2bd-1670bd5848fb)

**Timeline:**
- `09:52:00`: Session created ✅
- `09:52:02`: Message sent successfully ✅
- `09:52:05`: Start polling messages (after_id=0)
- `09:52:05-09:54:00`: **Polling stuck at after_id=352433 - NO NEW MESSAGES**
- `09:54:08`: 502 Bad Gateway error after 2+ minutes ❌

**Key Observation:**
The agent NEVER responds after receiving the task. No THOUGHT messages, no ACTION messages, nothing. This means the agent isn't even starting to work on the task.

## Root Cause Analysis

This is **NOT a prompt complexity issue**. We've simplified the prompts extensively:

### What We've Tried:

1. **Website Extraction (SIMPLIFIED):**
   - 3-minute time limit
   - Clear "WHEN TO FINISH" criteria
   - Explicit field requirements
   - NO developer tools
   - Text-only extraction (no images)

2. **Google Maps (SIMPLIFIED):**
   - 3-minute time limit
   - Text fields only (no photo URLs)
   - Description-based photo approach

3. **Instagram (DISABLED):**
   - Completely skipped to avoid CAPTCHA issues

### The Real Problem:

**The AGI API agent is not responding AT ALL.** This suggests:

1. **Agent Infrastructure Issue**: The agent process may be crashing or hanging before it can send any messages
2. **API Rate Limiting**: We may have hit rate limits from previous test sessions
3. **Session Initialization Problem**: Something fails during agent initialization that prevents ANY message output
4. **Prompt Parsing Failure**: The agent may be failing to parse our JSON output requirement

## What the Logs Show

**Normal Flow (Expected):**
```
09:52:02 - AGI message sent
09:52:05 - AGI USER: [prompt]
09:52:08 - AGI THOUGHT: "I'll help extract..."
09:52:10 - AGI ACTION: navigate to URL
09:52:15 - AGI THOUGHT: "I can see..."
[continues with thoughts/actions]
09:52:45 - AGI DONE: {extracted_data}
```

**Actual Flow (Broken):**
```
09:52:02 - AGI message sent
09:52:05 - AGI USER: [prompt]
[SILENCE - NO MESSAGES]
[POLLING CONTINUES FOR 2+ MINUTES]
09:54:08 - 502 Bad Gateway
```

## Comparison to Previous Successful Sessions

Looking at the old log (`/tmp/full_flow_instagram_demo.log`), the **website extraction worked perfectly**:

```
09:22:40 - Session created
09:22:42 - Message sent
09:22:46 - USER message
09:22:51 - THOUGHT message (agent started working!)
09:23:02 - THOUGHT message
[... continues with regular thoughts ...]
09:24:12 - DONE message (completed in 1.5 minutes!)
```

The **Google Maps extraction got stuck** trying to use developer tools, but it at least STARTED working (sent THOUGHT messages).

## Why Current Test is Different

**Previous test (successful website extraction):**
- Simple prompt asking for basic business info
- Agent immediately started sending THOUGHT messages
- Completed in 1.5 minutes

**Current test (no response):**
- MORE DETAILED prompt with explicit requirements
- Agent receives prompt but NEVER responds
- Times out with 502 after 2+ minutes of silence

## Possible Solutions

### 1. API Rate Limiting Reset
We've run many tests today. The AGI API may have rate-limited our account.

**Action:** Wait 30-60 minutes before trying again

### 2. Simplify Prompt Further
Current prompt is ~350 lines with detailed examples. Try an ultra-minimal prompt:

```
Visit https://www.ozumosanfrancisco.com/

Extract and return ONLY JSON:
{
  "business_name": "name",
  "industry": "category",
  "location": "city, state",
  "description": "1 sentence",
  "instagram": "@handle"
}

Do this in 2 minutes maximum.
```

### 3. Test with Simple URL
Try a simpler website first to verify AGI API is working:

```python
session_id = await self._create_session()
result = await self._send_message(
    session_id,
    "Visit google.com and tell me what you see",
    "https://www.google.com"
)
```

### 4. Check AGI API Status
Contact AGI support or check their status page to see if there are known issues.

## Recommendation

Given that:
1. Website extraction worked perfectly yesterday/earlier today
2. Current test shows agent NEVER responds (not even first THOUGHT)
3. Multiple attempts with different prompts all fail the same way

**Most Likely Cause:** AGI API rate limiting or infrastructure issue

**Recommended Action:**
1. Wait 1 hour
2. Test with ultra-simple prompt ("visit google.com and describe what you see")
3. If that works, gradually add back complexity
4. If that fails, contact AGI support

## Files with Updated Prompts

All extraction prompts have been updated per user requirements:

- `/home/fei/fei/code/groot-veo-licious-gems/aws-prod-agent-hack/backend/services/agi_service.py`:
  - Lines 278-359: `_extract_from_website()` - includes unique_selling_point, instagram_account, menu_info
  - Lines 390-452: `_extract_from_google_maps()` - includes photo descriptions
  - Lines 463-571: `_extract_from_instagram()` - 1-2 minutes, 3 posts, CAPTCHA handling

**The code is ready.** The issue is with the AGI API not responding.
