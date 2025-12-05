# MiniMax Service Test - Quick Start

## Prerequisites

1. **Set API Key** (required):
   ```bash
   # Add to backend/.env
   MINIMAX_API_KEY=your_minimax_api_key_here
   ```

2. **Install Dependencies** (if needed):
   ```bash
   pip install httpx
   ```

## Run Tests

```bash
cd backend
python3 tests/test_minimax_service.py
```

## What Gets Tested

| Test | What It Does | Output | Expected |
|------|--------------|--------|----------|
| **Initialization** | Verify service setup | Console output | API key loaded, URLs configured |
| **Simple Image** | Generate 2 images | `test_simple_image_1.jpg`<br>`test_simple_image_2.jpg` | Each > 10KB |
| **Reference Image** | Generate with subject | `test_reference_image_1.jpg`<br>`test_reference_image_2.jpg` | Each > 10KB (needs R2 URL) |
| **Video** | Generate video | `test_video_1.mp4` | > 100KB, 6s duration (needs R2 URL) |
| **Error Handling** | Test invalid configs | Console output | Proper error messages |

## Expected Runtime

- **With API Key**: ~30 seconds (without video test)
- **With Video Test**: ~5 minutes (video generation is slow)
- **Without API Key**: ~1 second (tests fail gracefully)

## Success Looks Like

```
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

## Verify Outputs

```bash
# List generated files
ls -lh backend/tests/outputs/minimax/

# Open images (macOS)
open backend/tests/outputs/minimax/test_simple_image_1.jpg

# Open images (Linux)
xdg-open backend/tests/outputs/minimax/test_simple_image_1.jpg

# Play video (macOS)
open backend/tests/outputs/minimax/test_video_1.mp4

# Play video (Linux)
vlc backend/tests/outputs/minimax/test_video_1.mp4
```

## Troubleshooting

### "MINIMAX_API_KEY not set"
➜ Add your API key to `backend/.env`

### "No images returned from API"
➜ Check API key is valid, verify internet connection

### Reference/Video tests skip
➜ Expected! These need R2 URLs. See `README_MINIMAX_TESTS.md` for setup

### Images generated but too small
➜ Retry test, may be temporary API issue

## Next Steps

1. **Run test** to verify MiniMax integration works
2. **Check outputs** to verify image quality
3. **Move to next test**: `test_agi_service.py`
4. **See full plan**: `TEST_PLAN.md`

## Documentation

- **Full guide**: `README_MINIMAX_TESTS.md`
- **Service code**: `../services/minimax_service.py`
- **Test plan**: `TEST_PLAN.md`
