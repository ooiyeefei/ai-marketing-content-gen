# Google Business Photos Integration Flow

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                      │
│  { business_address: "123 Main St", business_name: "Coffee Shop" }     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT 1: BUSINESS ANALYST                            │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 1. Geocode Address → place_id                                     │ │
│  │    "123 Main St" → "ChIJ..."                                      │ │
│  ├───────────────────────────────────────────────────────────────────┤ │
│  │ 2. Fetch Place Details                                            │ │
│  │    - Name, Rating, Reviews                                        │ │
│  │    - Business Types                                               │ │
│  ├───────────────────────────────────────────────────────────────────┤ │
│  │ 3. Fetch Business Photos                                          │ │
│  │    GoogleServicesClient.get_place_photos(place_id)                │ │
│  │    Returns: [photo1, photo2, ...]                                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BUSINESS PROFILE                                  │
│  {                                                                      │
│    business_name: "Coffee Shop",                                       │
│    photos: [                                                            │
│      {                                                                  │
│        url: "https://maps.googleapis.com/.../photo?ref=ABC&key=...",   │
│        width: 1920,                                                     │
│        height: 1080                                                     │
│      },                                                                 │
│      ... (up to 5 photos)                                               │
│    ],                                                                   │
│    from_maps: {...},                                                    │
│    content_themes: [...]                                                │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                AGENT 2: CONTENT STRATEGIST                              │
│  Generates 7-day content calendar                                       │
│  (No changes - passes business_profile through)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  AGENT 3: CREATIVE PRODUCER                             │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ FOR EACH POST:                                                    │ │
│  │                                                                   │ │
│  │ 1. Check for photos in business_profile                          │ │
│  │    ├─ Photos exist? → Proceed to step 2                          │ │
│  │    └─ No photos? → Generate without reference                    │ │
│  │                                                                   │ │
│  │ 2. Download & Encode First Photo                                 │ │
│  │    ┌─────────────────────────────────────────────────────────┐  │ │
│  │    │ _fetch_and_encode_image(photo_url)                      │  │ │
│  │    │  ├─ HTTP GET photo_url (timeout: 30s)                   │  │ │
│  │    │  ├─ Check status code == 200                            │  │ │
│  │    │  └─ Convert to base64                                   │  │ │
│  │    └─────────────────────────────────────────────────────────┘  │ │
│  │                                                                   │ │
│  │ 3. Generate Video Segments (or Images)                           │ │
│  │    ┌─────────────────────────────────────────────────────────┐  │ │
│  │    │ SEGMENT 1: WITH REFERENCE                               │  │ │
│  │    │  config = {                                              │  │ │
│  │    │    "numberOfVideos": 1,                                  │  │ │
│  │    │    "resolution": "720p",                                 │  │ │
│  │    │    "referenceImages": [{                                 │  │ │
│  │    │      "image": {"imageBytes": base64_photo},              │  │ │
│  │    │      "referenceType": "STYLE"                            │  │ │
│  │    │    }]                                                     │  │ │
│  │    │  }                                                        │  │ │
│  │    │  → Veo generates video matching photo style              │  │ │
│  │    └─────────────────────────────────────────────────────────┘  │ │
│  │    ┌─────────────────────────────────────────────────────────┐  │ │
│  │    │ SEGMENT 2+: VIDEO EXTENSION                             │  │ │
│  │    │  Uses previous_video_object for continuity              │  │ │
│  │    │  (No reference image needed - extends from segment 1)   │  │ │
│  │    └─────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       GENERATED CONTENT                                 │
│  [                                                                      │
│    {                                                                    │
│      day: 1,                                                            │
│      caption: "Check out our cozy atmosphere! ☕ #CoffeeShop",          │
│      video_segments: [                                                  │
│        {                                                                │
│          segment_number: 1,                                             │
│          uri: "gs://bucket/video1.mp4",                                 │
│          prompt_used: "Wide shot of coffee shop interior"               │
│          // Generated WITH style from business photo                    │
│        },                                                               │
│        {                                                                │
│          segment_number: 2,                                             │
│          uri: "gs://bucket/video2.mp4",                                 │
│          prompt_used: "Close-up of barista making latte"                │
│          // Extended from segment 1 (inherits style)                    │
│        }                                                                │
│      ]                                                                  │
│    },                                                                   │
│    ... (6 more posts)                                                   │
│  ]                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHOTO INTEGRATION WITH FALLBACKS                     │
└─────────────────────────────────────────────────────────────────────────┘

1. Get Photos
   ├─ Success → photos = [...]
   └─ Failure → photos = []
                  └─ Log warning
                     └─ Continue without photos

2. Download Photo
   ├─ Success → reference_image_base64 = "..."
   └─ Failure (timeout/404/etc) → reference_image_base64 = None
                                    └─ Log error
                                       └─ Continue without reference

3. Generate Video
   ├─ With reference → config includes referenceImages
   │                    └─ Style matches business photo
   └─ Without reference → config without referenceImages
                          └─ Style from prompt only

CRITICAL: At no point does photo failure block content generation
```

## API Interactions

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GOOGLE MAPS PLACES API                          │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
           ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
           │  Geocoding  │  │Place Details│  │Photo Fetch  │
           │   Request   │  │   Request   │  │  (5 photos) │
           └─────────────┘  └─────────────┘  └─────────────┘
                  │                │                 │
                  └────────────────┴─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Photo URLs with    │
                        │  embedded API keys   │
                        └──────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  HTTP GET (async)    │
                        │   Photo Download     │
                        └──────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Base64 Encoding     │
                        └──────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         IMAGEN/VEO API                                 │
│   GenerateVideosRequest with referenceImages in config                │
└────────────────────────────────────────────────────────────────────────┘
```

## Code Call Stack

```
main.py
 └─ POST /generate-content
     └─ orchestrator.run_pipeline()
         │
         ├─ Agent 1: business_analyst.analyze()
         │   ├─ google_services.get_place_details()
         │   │   └─ gmaps.place()
         │   │
         │   └─ google_services.get_place_photos(place_id)  ← NEW
         │       ├─ gmaps.place(fields=['photos'])
         │       └─ return [photo_metadata, ...]
         │
         ├─ Agent 2: content_strategist.create_calendar()
         │   └─ (receives business_profile with photos)
         │
         └─ Agent 3: creative_producer.produce_content()
             │
             ├─ FOR EACH POST:
             │   │
             │   ├─ Check business_profile['photos']  ← NEW
             │   │
             │   ├─ _fetch_and_encode_image(photo_url)  ← NEW
             │   │   └─ httpx.AsyncClient.get(photo_url)
             │   │   └─ base64.b64encode(response.content)
             │   │
             │   └─ _generate_videos()
             │       └─ _generate_single_video_segment(
             │              reference_image_base64=...  ← NEW
             │          )
             │           └─ genai_client.models.generate_videos(
             │                  config={'referenceImages': [...]}  ← NEW
             │              )
             │
             └─ return [ContentPost, ...]
```

## Key Decision Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DECISION TREE                               │
└─────────────────────────────────────────────────────────────────────┘

1. Should we fetch photos?
   │
   ├─ business_address provided? → YES → Fetch photos
   └─ No address? → NO → Skip photos (photos = [])

2. Should we use reference image?
   │
   ├─ photos.length > 0? → YES → Download first photo
   │   │
   │   ├─ Download successful? → YES → Use as reference
   │   └─ Download failed? → NO → Generate without reference
   │
   └─ No photos? → NO → Generate without reference

3. Which segments get reference image?
   │
   ├─ Segment 1? → YES → Apply reference image
   └─ Segment 2+? → NO → Use video extension (inherits style)

4. For images (Imagen 3)?
   │
   └─ ALL images get reference → Consistent style across images
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────────┐
│                   TIMING BREAKDOWN (per business)                   │
└─────────────────────────────────────────────────────────────────────┘

get_place_photos()              ~0.5-1s   (1 API call)
download_and_encode_photo()     ~1-3s     (1 HTTP request)
                                ─────────
TOTAL ADDED TIME:               ~2-4s

Original Pipeline:              ~15-20 minutes (video generation)
With Photo Integration:         ~15-20 minutes (negligible impact)

Photo fetching is parallel to other analysis steps
Photo download happens once per business, cached in memory
```

## Security & Privacy

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SECURITY CONSIDERATIONS                           │
└─────────────────────────────────────────────────────────────────────┘

1. API Key Protection:
   ✓ API key read from environment variable
   ✓ Not logged or exposed in responses
   ✓ Embedded in photo URLs (required by Google)

2. Photo Attributions:
   ✓ Stored in photo metadata
   ✓ Available for proper crediting if needed

3. Rate Limiting:
   ✓ Max 5 photos per business (respects quotas)
   ✓ No retry loops (fail fast)

4. Data Privacy:
   ✓ Photos are public (from Google Business Profile)
   ✓ No caching of photos (fresh each time)
   ✓ Base64 data only in memory (not persisted)
```

## Summary

The integration seamlessly adds Google Business Photos to the content generation pipeline with:

- ✓ **Minimal latency** (2-4 seconds added)
- ✓ **Robust error handling** (graceful fallbacks)
- ✓ **API efficiency** (max 5 photos, no caching overhead)
- ✓ **Zero blocking** (photos never prevent content generation)
- ✓ **Visual consistency** (style references ensure brand alignment)
