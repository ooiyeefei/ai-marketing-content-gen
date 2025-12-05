# MiniMax Service Test Suite

## Overview

Comprehensive test suite for MiniMaxService that verifies:
- Image generation (text-to-image)
- Image generation with subject reference
- Video generation (image-to-video)
- Error handling
- Service initialization

## Test Philosophy

- **Real API Calls**: Uses actual MiniMax API (no mocks)
- **Evidence-Based**: Saves all outputs for manual verification
- **Clear Criteria**: File size and format validation
- **Error Handling**: Tests graceful failure scenarios

## Prerequisites

### 1. Environment Variables

Set the following in your `.env` file:

```bash
MINIMAX_API_KEY=your_minimax_api_key_here
```

### 2. Dependencies

Ensure you have the required packages:

```bash
pip install httpx
```

## Running Tests

### Run All Tests

```bash
cd backend
python3 tests/test_minimax_service.py
```

### Expected Output

```
============================================================
MiniMax Service Test Suite
============================================================
Output directory: backend/tests/outputs/minimax
Testing with REAL API calls (no mocks)
============================================================

✓ MINIMAX_API_KEY is set (length: 32)

============================================================
Running: test_minimax_initialization
============================================================

✓ PASS: test_minimax_initialization
  API Key: ✓
  Image URL: ✓
  Video URL: ✓
  Auth Header: ✓
  Content-Type: ✓

... (more tests)

============================================================
TEST SUMMARY
============================================================

Total Tests: 5
Passed: 5
Failed: 0

Output Directory: backend/tests/outputs/minimax
Generated Files: 5
  - test_simple_image_1.jpg (45.23KB)
  - test_simple_image_2.jpg (43.87KB)
  - test_reference_image_1.jpg (48.12KB)
  - test_reference_image_2.jpg (46.91KB)
  - test_video_1.mp4 (523.45KB)
```

## Test Cases

### 1. test_minimax_initialization

**Purpose**: Verify service initializes correctly

**Checks**:
- API key is set
- Image URL configured
- Video URL configured
- Auth headers present
- Content-Type header set

**Expected**: All checks pass

---

### 2. test_minimax_image_generation_simple

**Purpose**: Test basic image generation without reference

**Input**:
```python
prompt = "A serene coffee shop interior with natural lighting"
num_images = 2
aspect_ratio = "1:1"
```

**Expected**:
- 2 images generated
- Each image > 10KB
- Files saved to `outputs/minimax/test_simple_image_*.jpg`

**Verification**:
```bash
# Check files exist
ls -lh backend/tests/outputs/minimax/test_simple_image_*.jpg

# Open images to verify quality
open backend/tests/outputs/minimax/test_simple_image_1.jpg
```

---

### 3. test_minimax_image_generation_with_reference

**Purpose**: Test image generation with subject reference URL

**Note**: This test requires a valid R2 URL with a reference image.

**Input**:
```python
prompt = "A cozy coffee shop with the subject standing behind the counter"
subject_reference_url = "https://pub-your-account.r2.dev/test-reference.jpg"
num_images = 2
```

**Expected**:
- 2 images generated with subject consistency
- Each image > 10KB
- Files saved to `outputs/minimax/test_reference_image_*.jpg`

**Setup**:
1. Upload a reference image to R2
2. Update the `reference_url` in the test
3. Run the test

---

### 4. test_minimax_video_generation

**Purpose**: Test video generation from first frame image

**Note**: This test requires a valid R2 URL with a first frame image.

**Input**:
```python
motion_prompt = "Slow zoom in on the coffee shop interior"
first_frame_image_url = "https://pub-your-account.r2.dev/test-first-frame.jpg"
duration = 6
```

**Expected**:
- Video generated
- Video > 100KB
- File saved to `outputs/minimax/test_video_1.mp4`
- Generation takes 3-5 minutes

**Setup**:
1. Generate an image using test #2
2. Upload to R2
3. Update the `first_frame_url` in the test
4. Run the test

**Verification**:
```bash
# Check file size
ls -lh backend/tests/outputs/minimax/test_video_1.mp4

# Play video
open backend/tests/outputs/minimax/test_video_1.mp4
```

---

### 5. test_minimax_error_handling

**Purpose**: Test error handling for invalid configurations

**Tests**:
- Missing API key raises ValueError
- Error message is clear
- No crashes or unhandled exceptions

**Expected**: Test passes by catching expected errors

---

## Output Directory Structure

```
backend/tests/outputs/minimax/
├── test_simple_image_1.jpg         # Generated image (simple)
├── test_simple_image_2.jpg         # Generated image (simple)
├── test_reference_image_1.jpg      # Generated image (with reference)
├── test_reference_image_2.jpg      # Generated image (with reference)
└── test_video_1.mp4                # Generated video
```

## Success Criteria

### All Tests Pass

- ✅ test_minimax_initialization
- ✅ test_minimax_image_generation_simple
- ✅ test_minimax_image_generation_with_reference
- ✅ test_minimax_video_generation
- ✅ test_minimax_error_handling

### File Validation

- ✅ All images > 10KB
- ✅ All videos > 100KB
- ✅ Files are valid formats (JPEG/MP4)
- ✅ Files can be opened in viewers

### Manual Verification

After tests pass, manually verify:

1. **Images**: Open each image file
   - Check visual quality
   - Verify prompt was followed
   - Confirm aspect ratio is correct

2. **Video**: Play video file
   - Check motion follows prompt
   - Verify duration is correct (6 seconds)
   - Confirm video quality

## Troubleshooting

### Test Fails: "MINIMAX_API_KEY not set"

**Solution**: Add your MiniMax API key to `.env`:
```bash
echo "MINIMAX_API_KEY=your_key_here" >> .env
```

### Test Fails: "No images returned from API"

**Possible causes**:
1. Invalid API key
2. API rate limit exceeded
3. Network issues

**Solution**:
1. Verify API key is correct
2. Wait a few minutes and retry
3. Check internet connection

### Test Fails: "File too small"

**Possible causes**:
1. API returned error image
2. Incomplete download

**Solution**:
1. Check API response in logs
2. Retry the test
3. Verify API key has sufficient credits

### Reference/Video Tests Skip

**Expected behavior**: These tests require valid R2 URLs

**To enable**:
1. Run test #2 (simple image generation)
2. Upload an image to R2
3. Update URLs in test file
4. Run tests again

## Integration with Full Test Suite

This test is part of the comprehensive test plan:

```bash
# Run all service tests
cd backend/tests
python3 test_minimax_service.py
python3 test_agi_service.py
python3 test_gemini_service.py
python3 test_convex_service.py
python3 test_r2_service.py
```

See `TEST_PLAN.md` for full test strategy.

## API Documentation

MiniMax API endpoints used:

1. **Image Generation**
   - Endpoint: `https://api.minimax.chat/v1/text_to_image`
   - Model: `image-01`
   - Timeout: 120 seconds

2. **Video Generation**
   - Endpoint: `https://api.minimax.chat/v1/video_generation`
   - Model: `video-01`
   - Timeout: 30 seconds (initial)
   - Polling: 10 second intervals, max 300 seconds

## Notes

- Image generation typically takes 5-15 seconds
- Video generation typically takes 3-5 minutes
- All API calls are asynchronous using `httpx.AsyncClient`
- Images are returned as base64-encoded data
- Videos are downloaded from a temporary URL
- Test outputs are persistent for manual inspection

## Contact

For issues or questions, refer to:
- MiniMax API docs: https://api.minimax.chat/docs
- Service implementation: `backend/services/minimax_service.py`
- Test plan: `backend/tests/TEST_PLAN.md`
