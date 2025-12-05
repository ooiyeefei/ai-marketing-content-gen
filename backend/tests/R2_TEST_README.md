# R2 Service Test Suite

Comprehensive test suite for Cloudflare R2 object storage service that follows CLAUDE.md principles: **no mocks, real API calls, autonomous validation**.

## Test Script

**File:** `backend/tests/test_r2_service.py` (452 lines)

## Test Cases

### 1. test_r2_campaign_path_helper
Tests the campaign path generation helper method.

**What it does:**
- Generates object keys using `get_campaign_path()` method
- Verifies format matches expected pattern: `campaigns/{campaign_id}/{filename}`

**Success criteria:**
- Path format is correct
- Handles nested paths (e.g., `research/competitor_1.jpg`)

### 2. test_r2_upload_bytes
Tests single file upload with full validation.

**What it does:**
1. Creates a 100x100 pixel red test image (JPEG bytes)
2. Uploads to R2 using `upload_bytes()`
3. Verifies public URL is accessible (HTTP 200)
4. Downloads the file from the public URL
5. Compares downloaded bytes with original bytes

**Success criteria:**
- Upload completes without errors
- Public URL returns HTTP 200
- Downloaded bytes match original bytes exactly

### 3. test_r2_upload_from_url
Tests uploading from external URL.

**What it does:**
1. Uses a public placeholder image URL (via.placeholder.com)
2. Uploads to R2 using `upload_from_url()`
3. Verifies new R2 URL is accessible

**Success criteria:**
- External URL download succeeds
- Upload to R2 succeeds
- Public R2 URL is accessible

### 4. test_r2_upload_multiple_concurrent
Tests concurrent uploads (5 parallel).

**What it does:**
1. Creates 5 different test images (red, blue, green, yellow, purple)
2. Uploads all 5 concurrently using `asyncio.gather()`
3. Verifies at least 3 out of 5 succeed (allows some failures)
4. Checks all successful URLs are accessible

**Success criteria:**
- At least 3 out of 5 uploads succeed
- All successful URLs return HTTP 200
- Concurrent execution doesn't block

### 5. test_r2_error_handling
Tests error handling with invalid credentials.

**What it does:**
1. Tests missing credentials (empty env vars)
   - Expects `ValueError` with "Missing R2 credentials"
2. Tests invalid credentials (fake keys)
   - Attempts upload, expects exception during upload
3. Restores original credentials

**Success criteria:**
- Missing credentials raises `ValueError` immediately
- Invalid credentials raise exception during upload
- Original credentials are restored after test

## Running the Tests

### Prerequisites

1. **Environment variables** must be set in `.env`:
   ```bash
   CLOUDFLARE_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET=your_bucket_name
   ```

2. **Dependencies** must be installed:
   ```bash
   pip install boto3 httpx pillow
   ```

3. **R2 bucket** must have public access enabled for the test URLs to work.

### Run Command

```bash
cd backend/tests
python test_r2_service.py
```

### Alternative: Run from backend directory

```bash
cd backend
python tests/test_r2_service.py
```

## Expected Output

```
======================================================================
R2 SERVICE TEST SUITE
======================================================================

Testing REAL Cloudflare R2 APIs (no mocks)
Following CLAUDE.md principles: TDD, no mocks, autonomous validation
======================================================================

======================================================================
TEST: test_r2_campaign_path_helper
======================================================================
✓ R2Service initialized
Generated path: campaigns/test_campaign_123/research/competitor_1.jpg
Expected path:  campaigns/test_campaign_123/research/competitor_1.jpg
✓ Path format correct

✅ TEST PASSED (0.05s)

======================================================================
TEST: test_r2_upload_bytes
======================================================================
✓ R2Service initialized
✓ Created test image: 812 bytes
✓ Object key: test/upload_a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
✓ Uploaded to R2
  URL: https://pub-your-account-id.r2.dev/test/upload_a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
✓ URL accessible: HTTP 200
✓ Downloaded: 812 bytes
✓ Byte verification: MATCH

✅ TEST PASSED (2.34s)

... [continues for all tests]

======================================================================
TEST RESULTS SUMMARY
======================================================================

✅ PASSED: 5/5
   - test_r2_campaign_path_helper (0.05s)
   - test_r2_upload_bytes (2.34s)
   - test_r2_upload_from_url (1.87s)
   - test_r2_upload_multiple_concurrent (5.12s)
   - test_r2_error_handling (0.98s)

Total time: 10.36s
======================================================================
```

## Test Files Created

The tests create temporary files in your R2 bucket under the `test/` prefix:

```
test/upload_{uuid}.jpg              # Single upload test
test/from_url_{uuid}.jpg            # Upload from URL test
test/concurrent_{uuid}_red.jpg      # Concurrent upload tests
test/concurrent_{uuid}_blue.jpg
test/concurrent_{uuid}_green.jpg
test/concurrent_{uuid}_yellow.jpg
test/concurrent_{uuid}_purple.jpg
test/error_test_{uuid}.jpg          # Error handling test (if credentials valid)
```

## Cleanup

The tests do NOT automatically clean up test files from R2. You may want to periodically delete files under the `test/` prefix.

### Manual cleanup (using AWS CLI):

```bash
aws s3 rm s3://your-bucket/test/ --recursive \
  --endpoint-url https://your-account-id.r2.cloudflarestorage.com
```

## Troubleshooting

### Error: "Missing R2 credentials in environment variables"

**Cause:** Environment variables not set or `.env` file not loaded.

**Fix:**
1. Check `.env` file exists in `backend/` directory
2. Verify all required variables are set
3. Try running from `backend/` directory (not `backend/tests/`)

### Error: "URL accessible: HTTP 403"

**Cause:** R2 bucket doesn't have public access enabled.

**Fix:**
1. Go to Cloudflare dashboard > R2 > Your bucket
2. Settings > Public access > Enable
3. Note the public URL domain

### Error: "Byte mismatch: uploaded X bytes, downloaded Y bytes"

**Cause:** Content transformation or compression by R2/CDN.

**Fix:** This should not happen with JPEG images. If it does, verify:
1. Content-Type is set to "image/jpeg"
2. No CDN transformation rules are active
3. Check R2 bucket settings for compression

### Error: "At least 3 successful uploads expected, got X"

**Cause:** Network issues or rate limiting.

**Fix:**
1. Check internet connection
2. Verify R2 API rate limits not exceeded
3. Try running test again after a few minutes

## Integration with TEST_PLAN.md

This test suite fulfills the requirements from `backend/tests/TEST_PLAN.md`:

**Section 1.5 R2 Service:**
- ✅ test_r2_upload_bytes() - Upload image, verify URL accessible
- ✅ test_r2_upload_multiple_concurrent() - 5 parallel uploads
- ✅ test_r2_error_handling() - Invalid credentials handling

**Additional tests:**
- test_r2_upload_from_url() - External URL download and upload
- test_r2_campaign_path_helper() - Path generation utility

## CLAUDE.md Compliance

This test suite follows all CLAUDE.md principles:

1. **No Mocks or Dummy Data** ✅
   - Uses real Cloudflare R2 API
   - Creates actual test images with PIL
   - Verifies actual HTTP responses
   - Downloads and compares real bytes

2. **Truly Autonomous** ✅
   - Tests autonomously verify byte integrity
   - Concurrent tests verify parallelism
   - Error tests verify graceful handling
   - No human intervention needed

3. **Test-Driven Development** ✅
   - Each test has clear purpose
   - Tests verify specific behavior
   - Pass/fail criteria are measurable
   - Evidence-based validation (byte comparison, HTTP status)

4. **Verification Before Completion** ✅
   - Every upload is verified with HTTP GET
   - Bytes are compared for integrity
   - Concurrent uploads are counted and verified
   - Test results are summarized with timing

## Exit Codes

- **0:** All tests passed
- **1:** At least one test failed

Use in CI/CD:
```bash
python test_r2_service.py
if [ $? -eq 0 ]; then
  echo "R2 tests passed"
else
  echo "R2 tests failed"
  exit 1
fi
```

## Performance Benchmarks

Expected execution times (with good network):

| Test | Expected Time |
|------|---------------|
| test_r2_campaign_path_helper | < 0.1s |
| test_r2_upload_bytes | 2-3s |
| test_r2_upload_from_url | 1-2s |
| test_r2_upload_multiple_concurrent | 4-6s |
| test_r2_error_handling | < 1s |
| **Total** | **8-12s** |

Slower times may indicate:
- Network latency
- R2 API slowness
- Rate limiting
- Large file transfers

## Contact

For issues or questions about this test suite, refer to:
- `backend/tests/TEST_PLAN.md` - Overall test strategy
- `CLAUDE.md` - Development principles
- `backend/services/r2_service.py` - R2 service implementation
