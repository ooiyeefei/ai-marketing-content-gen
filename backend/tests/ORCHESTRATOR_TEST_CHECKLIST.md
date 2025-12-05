# Orchestrator Test Execution Checklist

Use this checklist before running the orchestrator tests to ensure everything is ready.

---

## Pre-Flight Checklist

### 1. Environment Setup

- [ ] All required environment variables set
- [ ] Convex URL configured
- [ ] AGI Service URL configured (Claude API)
- [ ] Gemini API key set
- [ ] Minimax API key set
- [ ] R2 credentials configured
- [ ] (Optional) Facebook/Instagram credentials for Agent 2

**Verify:**
```bash
cd backend/tests
python check_all_env.py
```

Expected: All required variables show ✅

---

### 2. Service Health Checks

- [ ] AGI Service (Claude) is running
- [ ] Gemini API accessible
- [ ] Minimax API accessible
- [ ] Convex database accessible
- [ ] R2 storage accessible

**Verify:**
```bash
# Check AGI Service
curl $AGI_SERVICE_URL/health

# Check Gemini API
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```

---

### 3. Network & Resources

- [ ] Stable internet connection (required for 60-90 min)
- [ ] Sufficient disk space (>100MB for outputs)
- [ ] API quotas available (see cost estimates)
- [ ] Time available (60-90 minutes minimum)

**Check disk space:**
```bash
df -h /home/fei/fei/code/groot-veo-licious-gems/aws-prod-agent-hack/backend/tests/outputs
```

---

### 4. Output Directory

- [ ] Output directory exists
- [ ] Write permissions verified
- [ ] Previous outputs backed up (if needed)

**Verify:**
```bash
ls -la outputs/orchestrator/
# Should exist and be writable
```

---

## Test Execution Checklist

### Before Running

- [ ] Read QUICKSTART_ORCHESTRATOR.md
- [ ] Understand expected runtime (60-90 min)
- [ ] Understand expected cost (~$1)
- [ ] Clear on success criteria
- [ ] Know how to cancel (Ctrl+C)

---

### During Execution

**Watch for these milestones:**

- [ ] Test starts (10 second countdown)
- [ ] Test 1 starts: Full Pipeline
  - [ ] Agent 1 starts (0-25% progress)
  - [ ] Agent 2 starts (25-50% progress)
  - [ ] Agent 3 starts (50-100% progress)
  - [ ] Campaign completes
- [ ] Test 2 starts: Progress Tracking
  - [ ] Progress monitored
  - [ ] Final state verified
- [ ] Test 3 starts: Error Recovery
  - [ ] Error cases tested
  - [ ] Graceful handling verified
- [ ] Final report generated

---

### After Execution

- [ ] Check final report exists
- [ ] Verify all tests passed
- [ ] Review campaign data quality
- [ ] Check output file sizes
- [ ] Verify no errors in logs

**Verify:**
```bash
# Check results
cat outputs/orchestrator/FINAL_REPORT.json | grep success_rate

# List all outputs
ls -lh outputs/orchestrator/
```

---

## Data Verification Checklist

### Test 1: Full Pipeline

**Check campaign data completeness:**

- [ ] Campaign ID generated
- [ ] Business name extracted
- [ ] Research complete:
  - [ ] Business context populated
  - [ ] 3+ competitors found
  - [ ] Market insights identified
- [ ] Analytics complete:
  - [ ] Customer sentiment analyzed
  - [ ] Positive/negative themes identified
  - [ ] (Optional) Social performance analyzed
- [ ] Creative complete:
  - [ ] 7 days of content generated
  - [ ] Each day has caption
  - [ ] Each day has theme
  - [ ] Each day has hashtags

**Verify:**
```bash
cat outputs/orchestrator/test1_verification_report.json
# Should show all checks passed
```

---

### Test 2: Progress Tracking

**Check progress milestones:**

- [ ] Progress started at 0%
- [ ] Progress reached 25% (Agent 1 complete)
- [ ] Progress reached 50% (Agent 2 complete)
- [ ] Progress reached 100% (Agent 3 complete)
- [ ] Final status is "completed"
- [ ] No status = "failed"

**Verify:**
```bash
cat outputs/orchestrator/test2_final_progress.json
# Should show progress: 100, status: "completed"
```

---

### Test 3: Error Recovery

**Check error handling:**

- [ ] Invalid URL handled gracefully
- [ ] Empty URL handled gracefully
- [ ] Error messages are descriptive
- [ ] No partial data corruption
- [ ] Convex status updated to "failed"

**Verify:**
```bash
cat outputs/orchestrator/test3_error_recovery_results.json
# Should show all test cases passed
```

---

## Performance Verification Checklist

### Timing Checks

- [ ] Test 1 completed in < 30 minutes
- [ ] Test 2 completed in < 30 minutes
- [ ] Test 3 completed in < 10 minutes
- [ ] Total runtime < 90 minutes

**Check:**
```bash
cat outputs/orchestrator/FINAL_REPORT.json | grep total_duration
```

---

### Data Quality Checks

- [ ] All images > 10KB
- [ ] All videos > 100KB (if generated)
- [ ] All R2 URLs accessible
- [ ] All Convex data retrievable
- [ ] JSON files valid (parse without errors)

**Check:**
```bash
# Verify JSON files
cat outputs/orchestrator/*.json | python -m json.tool > /dev/null
echo $?  # Should be 0
```

---

## Troubleshooting Checklist

### If Test 1 Fails

- [ ] Check Agent 1 logs for errors
- [ ] Verify AGI Service is running
- [ ] Verify business URL is accessible
- [ ] Check Lightpanda status
- [ ] Verify Convex connection
- [ ] Check API quotas

**Debug:**
```bash
cat outputs/orchestrator/test1_error_report.json
```

---

### If Test 2 Fails

- [ ] Check progress updates in Convex
- [ ] Verify Convex connection
- [ ] Check for timeout issues
- [ ] Review progress history

**Debug:**
```bash
cat outputs/orchestrator/test2_error_report.json
```

---

### If Test 3 Fails

- [ ] Check error messages
- [ ] Verify error handling logic
- [ ] Check Convex status updates
- [ ] Review error recovery flow

**Debug:**
```bash
cat outputs/orchestrator/test3_error_recovery_results.json
```

---

## Success Criteria Verification

### Critical Requirements

- [ ] ✅ All 3 tests passed
- [ ] ✅ No unhandled exceptions
- [ ] ✅ All agents executed successfully
- [ ] ✅ Complete campaign data returned
- [ ] ✅ Progress tracking accurate
- [ ] ✅ Error handling works

### Performance Requirements

- [ ] ✅ Total time < 90 minutes
- [ ] ✅ Test 1 < 30 minutes
- [ ] ✅ Test 2 < 30 minutes
- [ ] ✅ Test 3 < 10 minutes

### Data Quality Requirements

- [ ] ✅ Business context complete
- [ ] ✅ 3+ competitors found
- [ ] ✅ 5+ market insights
- [ ] ✅ Customer sentiment analyzed
- [ ] ✅ 7 days of content generated
- [ ] ✅ All images valid
- [ ] ✅ All videos valid

---

## Final Verification

### Output Files

- [ ] test1_full_pipeline_response.json exists
- [ ] test1_verification_report.json exists
- [ ] test1_summary.json exists
- [ ] test2_progress_tracking_response.json exists
- [ ] test2_final_progress.json exists
- [ ] test2_summary.json exists
- [ ] test3_error_recovery_results.json exists
- [ ] test3_summary.json exists
- [ ] FINAL_REPORT.json exists

**Count files:**
```bash
ls -1 outputs/orchestrator/*.json | wc -l
# Should be 9 or more
```

---

### Data Integrity

- [ ] All JSON files parseable
- [ ] All required fields present
- [ ] No null/empty critical fields
- [ ] All IDs match across files
- [ ] Timestamps make sense

**Validate:**
```bash
# Parse all JSON files
for f in outputs/orchestrator/*.json; do
  echo "Checking $f..."
  cat "$f" | python -m json.tool > /dev/null || echo "FAILED: $f"
done
```

---

## Next Steps Checklist

After all checks pass:

- [ ] Review campaign data quality
- [ ] Check generated content relevance
- [ ] Test with different business URLs
- [ ] Measure learning/improvement
- [ ] Prepare demo materials
- [ ] Document any issues found
- [ ] Update cost estimates (if needed)

---

## Quick Command Reference

```bash
# Pre-flight check
python check_all_env.py

# Run tests
python test_orchestrator.py
# OR
./RUN_ORCHESTRATOR_TESTS.sh

# Check results
cat outputs/orchestrator/FINAL_REPORT.json | grep success_rate

# View campaign
cat outputs/orchestrator/test1_full_pipeline_response.json | python -m json.tool

# Check errors
cat outputs/orchestrator/*error*.json

# Validate JSON
cat outputs/orchestrator/*.json | python -m json.tool > /dev/null && echo "All JSON valid"

# Clean outputs
rm -rf outputs/orchestrator/*.json
```

---

## Sign-Off

- [ ] All pre-flight checks passed
- [ ] All tests executed successfully
- [ ] All data verified
- [ ] All outputs saved
- [ ] No errors or warnings
- [ ] Ready for next phase

**Date:** _______________
**Tester:** _______________
**Notes:** _______________

---

**Use this checklist to ensure thorough testing before demo/production!**
