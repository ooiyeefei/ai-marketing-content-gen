# Agent 3 - Creative Producer: Key Code Snippets

## Overview
Implementation of Creative Producer with caption generation and Veo video extension.
- **File**: `backend/agents/creative_producer.py` (257 lines)
- **Test Files**: `test_agent3_captions.py` (63 lines), `test_agent3_videos.py` (71 lines)

## Part 1: Caption Generation

### Main Method - produce_content()
```python
async def produce_content(
    self,
    calendar: List[Dict],
    business_profile: Dict
) -> List[ContentPost]:
    """
    Generate complete content (captions + videos) for all posts.
    Returns List of ContentPost objects with captions and video segments
    """
    posts = []
    for post_plan in calendar:
        # Generate caption
        caption = await self._generate_caption(post_plan, business_profile)
        
        # Extract hashtags from caption
        hashtags = self._extract_hashtags(caption)
        
        # Generate videos
        video_segments = await self._generate_videos(
            post_plan.get('video_prompts', []),
            business_profile
        )
        
        # Create ContentPost object
        post = ContentPost(
            day=post_plan['day'],
            platform=post_plan.get('platform', 'instagram'),
            caption=caption,
            video_segments=video_segments,
            total_duration_seconds=sum(seg.duration_seconds for seg in video_segments),
            hashtags=hashtags
        )
        posts.append(post)
    
    return posts
```

### Caption Generation with Gemini
```python
async def _generate_caption(
    self,
    post_plan: Dict,
    business_profile: Dict
) -> str:
    """Generate platform-optimized caption with Gemini"""
    prompt = f"""Write an engaging {post_plan.get('platform', 'instagram')} caption for this post:

Concept: {post_plan.get('concept', 'business content')}
Theme: {post_plan.get('caption_theme', 'general')}
Brand Voice: {brand_voice}
CTA: {post_plan.get('cta', 'Learn more')}
Business: {business_name}

Requirements:
- 2-3 sentences maximum
- Include 3-5 relevant hashtags
- Match {brand_voice} tone
- Include the CTA naturally
- Engaging and authentic

Return ONLY the caption text with hashtags."""

    response = self.genai_client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.8,  # Creative captions
        )
    )
    
    return response.text.strip()
```

### Hashtag Extraction
```python
def _extract_hashtags(self, caption: str) -> List[str]:
    """Extract hashtags from caption using regex"""
    hashtags = re.findall(r'#\w+', caption)
    return hashtags
```

## Part 2: Video Generation with Veo Extension

### Multi-Segment Video Generation
```python
async def _generate_videos(
    self,
    video_prompts: List[str],
    business_profile: Dict
) -> List[VideoSegment]:
    """
    Generate video segments using Veo with extension.
    
    Process:
    1. Generate first segment at 720p
    2. For subsequent segments, use previous video URI as context
    3. Veo uses last frame for seamless continuation
    """
    segments = []
    previous_video_uri = None
    
    for i, prompt in enumerate(video_prompts, 1):
        # Generate video segment
        video_uri = await self._generate_single_video_segment(
            prompt=prompt,
            segment_number=i,
            previous_video_uri=previous_video_uri,
            business_context=business_profile.get('business_name', '')
        )
        
        if video_uri:
            segment = VideoSegment(
                segment_number=i,
                uri=video_uri,
                duration_seconds=settings.video_duration_seconds,
                prompt_used=prompt
            )
            segments.append(segment)
            previous_video_uri = video_uri  # Use for next extension
    
    return segments
```

### Single Video Segment with Extension Logic
```python
async def _generate_single_video_segment(
    self,
    prompt: str,
    segment_number: int,
    previous_video_uri: str = None,
    business_context: str = ""
) -> str:
    """Generate single video segment with Veo"""
    
    # Prepare generation config
    config = genai_types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=settings.video_duration_seconds,  # 8 seconds
        resolution=settings.video_resolution,  # 720p required for extension
        storage_uri=f"gs://{settings.storage_bucket}/videos/{job_id}/",
    )
    
    # Generate video
    if previous_video_uri:
        # Extension: use previous video as context
        logger.info(f"Extending from: {previous_video_uri}")
        operation = self.genai_client.models.generate_videos(
            model='veo-2.0-generate-001',
            prompt=full_prompt,
            video=genai_types.Video(uri=previous_video_uri),  # KEY: Extension
            config=config
        )
    else:
        # Initial generation
        logger.info(f"Generating initial video: {full_prompt}")
        operation = self.genai_client.models.generate_videos(
            model='veo-2.0-generate-001',
            prompt=full_prompt,
            config=config
        )
    
    # Poll for completion (video generation takes 2-5 minutes)
    max_wait_time = 600  # 10 minutes max
    start_time = time.time()
    
    while not operation.done:
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            logger.error(f"Video generation timed out after {max_wait_time}s")
            return None
        
        time.sleep(20)  # Check every 20 seconds
        operation = self.genai_client.operations.get(operation)
        logger.info(f"Status: {operation.name} | Elapsed: {int(elapsed)}s")
    
    # Get video URI from response
    if operation.response and operation.response.generated_videos:
        video_uri = operation.response.generated_videos[0].video.uri
        logger.info(f"Video generated successfully: {video_uri}")
        return video_uri
    else:
        logger.error("No video in operation response")
        return None
```

## Key Features

### Video Extension Requirements (CRITICAL)
1. **First segment**: Generate at 720p (required for extension)
2. **Segments 2+**: Pass `video=types.Video(uri=previous_video_uri)` to use last frame as context
3. **Model**: 'veo-2.0-generate-001'
4. **Duration**: 8 seconds per segment (from settings.video_duration_seconds)
5. **Storage**: `gs://{settings.storage_bucket}/videos/{job_id}/`
6. **Sequential generation**: MUST wait for each segment before starting next
7. **Poll operation.done with 20-second intervals**

### Data Flow
```
1. Agent 2 provides content calendar with video_prompts
   ↓
2. For each post:
   - Generate caption with Gemini (temperature 0.8)
   - Extract hashtags with regex
   - Generate video segments sequentially:
     * Segment 1: Initial generation at 720p
     * Segment 2: Extension using Segment 1 URI
     * Segment 3: Extension using Segment 2 URI
   ↓
3. Return ContentPost with caption, hashtags, and video segments
```

## Testing

### Caption Test (Safe to Run)
```bash
cd backend
python test_agent3_captions.py
```

Expected output:
- Generated caption with brand voice
- 3-5 extracted hashtags
- Platform-optimized formatting

### Video Test (Disabled by Default)
```bash
cd backend
# Uncomment asyncio.run() in test_agent3_videos.py
python test_agent3_videos.py
```

Expected output (if enabled):
- 2 video segments generated
- Each with GCS URI
- Sequential generation demonstrated

## Error Handling
- **Caption generation failure**: Returns fallback caption with business name and CTA
- **Video generation failure**: Returns empty segments list
- **Timeout**: 600 seconds max per segment
- **Missing data**: Gracefully handles missing prompts, profile data

## Integration Points
- **Input**: Takes calendar from Agent 2 (ContentStrategistAgent)
- **Input**: Takes business_profile from Agent 1 (BusinessAnalystAgent)
- **Output**: Returns List[ContentPost] for orchestrator
- **Dependencies**: config.settings, models (VideoSegment, ContentPost)
