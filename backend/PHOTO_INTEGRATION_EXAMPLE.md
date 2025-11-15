# Google Business Photos Integration

## Overview

This implementation integrates Google Business Photos from Google Maps as style references for video generation. The photos are fetched from the Google Places API and used as reference images in Imagen/Veo to ensure generated videos match the business's actual visual style.

## Architecture

### 1. Photo Fetching (Agent 1: Business Analyst)

**File**: `backend/agents/business_analyst.py`

When analyzing a business with an address, the agent now:
1. Geocodes the address to get the place_id
2. Fetches up to 5 business photos from Google Places API
3. Stores photo metadata (URL, dimensions, attributions) in the business profile

```python
# Example business_profile with photos
{
    'business_name': 'The Hawker',
    'photos': [
        {
            'url': 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=1024&photo_reference=ABC123&key=...',
            'width': 1024,
            'height': 768,
            'photo_reference': 'ABC123',
            'attributions': ['Photo by John Doe']
        },
        # ... up to 4 more photos
    ],
    'from_maps': {...},
    'from_website': {...}
}
```

### 2. Photo Processing (Google Services)

**File**: `backend/services/google_services.py`

Two new methods added:

#### `get_place_photos(place_id: str) -> List[Dict]`
- Fetches photos from Google Places API
- Constructs photo URLs with API key
- Returns list of photo metadata dictionaries
- Handles errors gracefully (returns empty list)
- Respects rate limits (fetches max 5 photos)

#### `download_and_encode_photo(photo_url: str) -> Optional[str]`
- Downloads photo from URL asynchronously
- Converts to base64 encoding for Imagen API
- Includes timeout protection (30s)
- Returns None on failure (network issues, timeout, etc.)

### 3. Reference Image Usage (Agent 3: Creative Producer)

**File**: `backend/agents/creative_producer.py`

Enhanced video generation to use business photos as style references:

#### Process Flow:
1. **Check for photos**: Look in business_profile['photos']
2. **Download and encode**: Use first photo as style reference
3. **Apply to first segment**: Add reference image to Veo config
4. **Graceful fallback**: Continue without reference if photo unavailable

```python
# Veo config with reference image
config = {
    "numberOfVideos": 1,
    "resolution": "720p",
    "aspectRatio": "16:9",
    "referenceImages": [{
        "image": {"imageBytes": "<base64_encoded_image>"},
        "referenceType": "STYLE"
    }]
}
```

## Error Handling

The implementation handles multiple failure scenarios gracefully:

### Scenario 1: No Maps API Key
- **Result**: Photos not fetched
- **Impact**: Video generation continues without style reference
- **Logging**: Warning logged in google_services.py

### Scenario 2: No Photos Available
- **Result**: Empty photos list in business_profile
- **Impact**: Video generation continues without style reference
- **Logging**: Info message logged

### Scenario 3: Photo Download Fails
- **Result**: reference_image_base64 is None
- **Impact**: Video generation continues without style reference
- **Logging**: Error logged with reason (timeout, HTTP error, etc.)

### Scenario 4: Invalid place_id
- **Result**: get_place_photos returns empty list
- **Impact**: Video generation continues without style reference
- **Logging**: Warning logged

## Example Usage

### Input
```json
{
    "business_input": {
        "business_name": "The Hawker",
        "business_address": "123 Main St, Singapore 123456",
        "website_url": "https://thehawker.com",
        "brand_voice": "casual"
    }
}
```

### Agent 1 Output (Business Profile)
```python
{
    'business_name': 'The Hawker',
    'brand_voice': 'casual',
    'photos': [
        {
            'url': 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=1024&photo_reference=CmRa...&key=...',
            'width': 1920,
            'height': 1080,
            'photo_reference': 'CmRa...',
            'attributions': ['Photo by The Hawker']
        }
    ],
    'from_maps': {
        'name': 'The Hawker',
        'rating': 4.5,
        'review_themes': ['authentic cuisine', 'friendly service']
    }
}
```

### Agent 3 Video Generation (with reference)
```
INFO: Generating 3 video segments with Veo
INFO: Attempting to use business photo as style reference
INFO: Successfully prepared business photo as style reference
INFO: Generating segment 1/3
INFO: Adding business photo as STYLE reference to video generation
INFO: Generating initial video with style reference: The Hawker. Wide shot of bustling hawker center...
INFO: Waiting for video generation to complete...
INFO: Video generated successfully: gs://bucket/video_1.mp4
```

## API Rate Limits

### Google Places API
- **Photo References**: Included in Place Details request (no extra cost)
- **Photo Downloads**: Each photo download counts as 1 request
- **Limit Strategy**: Fetch max 5 photos per business
- **Caching**: Photos are downloaded once per content generation session

### Optimization
- Photos are only downloaded when needed (during video generation)
- Failed downloads don't retry automatically
- Reference image only used for first video segment (not repeated)

## Testing

### Manual Test
```bash
# Set environment variables
export GOOGLE_MAPS_API_KEY="your_key_here"
export GCP_PROJECT_ID="your_project_id"
export GCP_REGION="us-central1"

# Run test
cd backend
python -m pytest tests/test_photo_integration.py -v
```

### Expected Logs
```
INFO:services.google_services:Found 3 photos for The Hawker
INFO:agents.business_analyst:Retrieved 3 business photos
INFO:agents.creative_producer:Attempting to use business photo as style reference
INFO:agents.creative_producer:Successfully prepared business photo as style reference
INFO:agents.creative_producer:Adding business photo as STYLE reference to video generation
```

## Configuration

No additional configuration required. The feature uses existing settings:

```python
# config.py
class Settings(BaseSettings):
    google_maps_api_key: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    # ... other settings
```

## Benefits

1. **Visual Consistency**: Generated videos match business's actual aesthetic
2. **Brand Alignment**: Style reference ensures on-brand content
3. **No Manual Upload**: Automatically uses existing Google Business photos
4. **Graceful Degradation**: System works with or without photos
5. **Rate Limit Friendly**: Minimal API calls (max 5 photos per business)

## Limitations

1. **First Segment Only**: Style reference only applied to first video segment
   - Subsequent segments use video extension (not style reference)
   - This is by design to maintain continuity

2. **Single Photo**: Only uses first available photo as reference
   - Could be enhanced to use different photos for different posts
   - Current implementation prioritizes simplicity

3. **No Caching**: Photos downloaded fresh each session
   - Could be enhanced with Cloud Storage caching
   - Trade-off: freshness vs. API efficiency

4. **Style Transfer Only**: Uses STYLE reference type
   - Alternative: SUBJECT reference (for specific objects)
   - Current choice fits most business use cases

## Future Enhancements

### Potential Improvements:
1. **Photo Caching**: Store downloaded photos in Cloud Storage
2. **Smart Selection**: Use different photos for different post themes
3. **Photo Quality Check**: Validate photo resolution/quality before use
4. **Multiple References**: Support multiple reference images per video
5. **Reference Type Selection**: Allow SUBJECT vs STYLE based on content

### Code Locations for Enhancements:
- Photo selection logic: `creative_producer.py:_generate_videos()`
- Caching: Add to `google_services.py:download_and_encode_photo()`
- Quality checks: Add to `business_analyst.py:analyze()`
