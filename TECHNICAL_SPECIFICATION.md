# Autonomous Marketing Intelligence Agent - Technical Specification

**Project Name:** BrandMind AI
**Version:** 1.0
**Date:** November 20, 2025
**Hackathon:** Production Agents Hackathon (Nov 21, 2025)
**Target:** 6+ sponsor integrations, autonomous operation, production-grade

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Agent Specifications](#agent-specifications)
4. [Data Models](#data-models)
5. [API Integrations](#api-integrations)
6. [Technology Stack](#technology-stack)
7. [User Flows](#user-flows)
8. [Success Criteria](#success-criteria)
9. [Implementation Phases](#implementation-phases)
10. [Deployment Strategy](#deployment-strategy)

---

## 1. Executive Summary

### Problem Statement
Small businesses and marketing agencies spend 10-20 hours/week creating social media content. Current solutions either:
- Cost $2-5K/month for agency services
- Require significant manual work
- Generate generic, off-brand content
- Lack competitive intelligence

### Solution
**BrandMind AI** is a fully autonomous 4-agent system that:
- Researches your business & competitors automatically
- Learns and remembers brand voice, visual style, successful campaigns
- Generates on-brand images, videos, and captions
- Publishes content across platforms
- Tracks performance and improves over time

### Value Proposition
**Input:** Business URL + Social media handles
**Output:** 7 days of branded content (captions + images + videos) + competitive insights
**Time:** 5 minutes of setup → Autonomous operation
**Cost:** $99-299/month vs $2-5K/month agencies

### Key Differentiators
1. **Autonomous Research** - Discovers brand context without manual input
2. **Agent Memory** - Redis vectors store learnings, improves over time
3. **Competitive Intelligence** - Real-time competitor monitoring
4. **Multi-Platform Publishing** - Sanity CMS + API orchestration
5. **Performance Learning** - Adapts based on engagement metrics

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Input Form   │  │ Dashboard    │  │ Content Calendar    │   │
│  │ (URL + SM)   │  │ (Insights)   │  │ (Sanity CMS View)   │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                   Backend API (FastAPI)                          │
│                   Orchestrator + Event Bus                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼                ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐  ┌─────────────┐
│   Agent 1    │    │   Agent 2    │    │   Agent 3    │  │   Agent 4   │
│   Research   │───▶│   Strategy   │───▶│   Creative   │─▶│ Orchestrate │
│  & Discovery │    │   Planner    │    │  Production  │  │  & Publish  │
└──────┬───────┘    └──────────────┘    └──────┬───────┘  └──────┬──────┘
       │                                        │                  │
       ▼                                        ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        External Services                             │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────┤
│ Lightpanda   │ Redis VL     │ Claude API   │ Sanity CMS   │ Postman │
│ Web Scraping │ Vector DB    │ Anthropic    │ Content Mgmt │ API Hub │
├──────────────┼──────────────┼──────────────┼──────────────┼─────────┤
│ Google Vertex AI            │ AWS Services                │         │
│ - Imagen 3 (images)         │ - ECS/Fargate (containers)  │         │
│ - Veo 2 (videos)            │ - S3 (storage)              │         │
│ - Vertex Search             │ - Lambda (functions)        │         │
│ - Grounded Generation       │ - CloudWatch (monitoring)   │         │
└─────────────────────────────┴─────────────────────────────┴─────────┘
```

### Data Flow

```
1. User Input (Business URL + Social handles)
   │
   ▼
2. Agent 1: Research & Discovery
   ├─ Lightpanda scrapes: website, competitors, social media
   ├─ Vertex AI Search: industry trends, target audience
   ├─ Grounded Generation: factual business data
   └─ Redis: Store embeddings of all research
   │
   ▼
3. Agent 2: Brand Strategy
   ├─ Redis Vector Search: Retrieve similar past campaigns
   ├─ Claude: Analyze patterns, generate 7-day strategy
   ├─ Postman: Query analytics APIs for performance data
   └─ Redis: Store strategy + decisions
   │
   ▼
4. Agent 3: Creative Production
   ├─ Claude: Generate captions, hashtags, CTAs
   ├─ Imagen 3: Generate images with style references
   ├─ Veo 2: Generate videos (8-24 seconds)
   ├─ Redis: Cache generations, store assets
   └─ S3: Upload final media files
   │
   ▼
5. Agent 4: Content Orchestration
   ├─ Sanity CMS: Publish content calendar
   ├─ Postman: Schedule posts via social media APIs
   ├─ Redis: Track published content
   └─ CloudWatch: Monitor engagement, trigger improvements
```

---

## 3. Agent Specifications

### Agent 1: Research & Discovery Agent

**Responsibility:** Autonomously discover business context, competitors, and market intelligence

#### Inputs
- Business website URL
- Social media handles (optional: Instagram, Facebook, Twitter, LinkedIn)
- Competitor URLs (optional, or auto-discover)

#### Processing Steps

1. **Website Analysis** (Duration: 30-60s)
   ```python
   async def analyze_website(business_url: str) -> BusinessContext:
       # Use Lightpanda for fast scraping
       browser = await lightpanda.connect()
       page = await browser.goto(business_url)

       # Extract content
       html = await page.content()
       images = await page.query_selector_all('img')

       # Use Claude to analyze
       analysis = await claude.analyze({
           "html": html,
           "images": [img.src for img in images],
           "task": "Extract: business description, products/services,
                    brand colors, tone of voice, target audience"
       })

       # Store in Redis with embeddings
       await redis.store_with_embeddings(
           key=f"business:{business_url}",
           data=analysis,
           embeddings=await claude.get_embeddings(analysis)
       )

       return analysis
   ```

2. **Product Image Collection** (Duration: 20-30s)
   ```python
   async def collect_product_images(business_url: str) -> List[Image]:
       # Scrape product pages
       product_pages = await lightpanda.scrape_links(
           business_url,
           filters=['product', 'shop', 'portfolio']
       )

       images = []
       for page_url in product_pages[:10]:  # Limit to 10 pages
           page_images = await lightpanda.extract_images(page_url)
           images.extend(page_images)

       # Filter for high-quality product images
       filtered = await claude.filter_images(
           images,
           criteria="product photos, not logos or icons, >500px width"
       )

       # Store in Redis and S3
       for img in filtered:
           s3_url = await s3.upload(img)
           await redis.store(f"product_images:{business_url}", s3_url)

       return filtered
   ```

3. **Competitor Research** (Duration: 60-90s)
   ```python
   async def research_competitors(
       business_context: BusinessContext
   ) -> CompetitorInsights:
       # Use Vertex AI Search to find competitors
       competitors = await vertex_search.query(
           f"{business_context.industry} companies similar to
            {business_context.business_name}"
       )

       insights = []
       for competitor in competitors[:3]:  # Top 3 competitors
           # Scrape their social media with Lightpanda
           if competitor.instagram:
               posts = await lightpanda.scrape_instagram(
                   competitor.instagram,
                   limit=10
               )

               # Analyze with Claude
               analysis = await claude.analyze_posts(posts, [
                   "content themes",
                   "posting frequency",
                   "engagement patterns",
                   "visual style",
                   "caption tone"
               ])

               insights.append({
                   "competitor": competitor.name,
                   "analysis": analysis,
                   "top_posts": posts[:3]
               })

       # Store in Redis vectors
       await redis.store_competitor_insights(
           business_url=business_context.url,
           insights=insights
       )

       return insights
   ```

4. **Industry Trends** (Duration: 30-45s)
   ```python
   async def research_industry_trends(
       business_context: BusinessContext
   ) -> TrendAnalysis:
       # Use Grounded Generation API for factual data
       trends = await vertex_grounded_generation.query(
           prompt=f"What are the current trends in {business_context.industry}?
                   What content performs well on social media in this industry?",
           grounding_source="google_search"
       )

       # Use Claude to synthesize actionable insights
       actionable = await claude.synthesize(
           data=trends,
           task="Extract 3-5 actionable content themes for social media"
       )

       # Store with embeddings
       await redis.store_with_embeddings(
           key=f"trends:{business_context.industry}",
           data=actionable,
           ttl=86400  # Cache for 24 hours
       )

       return actionable
   ```

5. **Brand Voice Extraction** (Duration: 20-30s)
   ```python
   async def extract_brand_voice(
       website_content: str,
       social_posts: List[str]
   ) -> BrandVoice:
       # Use Claude to analyze tone and voice
       voice_analysis = await claude.analyze({
           "website_copy": website_content,
           "social_posts": social_posts,
           "task": """Analyze and extract:
                   - Tone: (professional/casual/playful/authoritative)
                   - Vocabulary: (technical/simple/trendy/formal)
                   - Perspective: (1st person/3rd person)
                   - Personality traits: (3-5 adjectives)
                   - Do's and Don'ts for content creation
                   """
       })

       # Store in Redis
       await redis.set(f"brand_voice:{business_url}", voice_analysis)

       return voice_analysis
   ```

#### Outputs
```python
@dataclass
class ResearchOutput:
    business_context: BusinessContext
    product_images: List[str]  # S3 URLs
    competitor_insights: CompetitorInsights
    industry_trends: TrendAnalysis
    brand_voice: BrandVoice
    redis_keys: List[str]  # For downstream agents
```

#### Error Handling
- **Website unreachable:** Use Grounded Generation with business name + industry
- **No product images found:** Use generic industry images as fallback
- **Competitor scraping blocked:** Skip competitor analysis, rely on trends
- **Timeout:** Return partial results, continue asynchronously

#### Performance Targets
- Total execution time: 2-4 minutes
- Success rate: >95% for public websites
- Data quality: Claude validates all extracted data

---

### Agent 2: Brand Strategy Agent

**Responsibility:** Create data-driven 7-day content strategy based on research

#### Inputs
```python
@dataclass
class StrategyInputs:
    research_output: ResearchOutput  # From Agent 1
    redis_keys: List[str]
    past_campaigns: Optional[List[Campaign]]  # If returning user
    performance_metrics: Optional[Dict]  # If available
```

#### Processing Steps

1. **Retrieve Relevant Context** (Duration: 10-15s)
   ```python
   async def retrieve_context(redis_keys: List[str]) -> StrategyContext:
       # Vector search for similar past campaigns
       similar_campaigns = await redis_vector_search(
           query_embedding=await claude.embed(
               f"{business_context.industry} {business_context.products}"
           ),
           index="campaigns",
           top_k=5
       )

       # Get competitor insights
       competitor_data = await redis.get_all(
           pattern=f"competitor:{business_url}:*"
       )

       # Get trending themes
       trends = await redis.get(f"trends:{business_context.industry}")

       return StrategyContext(
           similar_campaigns=similar_campaigns,
           competitors=competitor_data,
           trends=trends
       )
   ```

2. **Analyze Performance Data** (Duration: 15-20s)
   ```python
   async def analyze_performance(
       business_url: str
   ) -> PerformanceInsights:
       # Use Postman to query social media analytics APIs
       apis = [
           postman.instagram_insights_api,
           postman.facebook_insights_api,
           postman.twitter_analytics_api
       ]

       insights = []
       for api in apis:
           try:
               data = await api.query({
                   "metrics": ["engagement_rate", "reach", "impressions"],
                   "timeframe": "last_30_days"
               })
               insights.append(data)
           except Exception as e:
               logger.warning(f"Failed to fetch {api.name}: {e}")

       # Use Claude to synthesize patterns
       patterns = await claude.analyze({
           "data": insights,
           "task": "What content types, posting times, and themes
                   performed best?"
       })

       return patterns
   ```

3. **Generate Content Strategy** (Duration: 30-45s)
   ```python
   async def generate_strategy(
       context: StrategyContext
   ) -> ContentStrategy:
       # Use Claude with extended thinking
       strategy = await claude.generate({
           "model": "claude-sonnet-4.5",
           "temperature": 0.7,
           "system": """You are a social media strategist. Create a
                       7-day content calendar that:
                       - Aligns with brand voice
                       - Incorporates industry trends
                       - Differentiates from competitors
                       - Balances content types (educational, promotional,
                         entertaining)
                       - Optimizes for engagement""",
           "context": {
               "brand_voice": context.brand_voice,
               "products": context.products,
               "trends": context.trends,
               "competitors": context.competitor_insights,
               "past_performance": context.performance_data
           },
           "output_format": {
               "days": [
                   {
                       "day": 1,
                       "theme": "str",
                       "content_type": "image|video|carousel",
                       "caption_direction": "str",
                       "image_concept": "str",
                       "video_concept": "str (if applicable)",
                       "cta": "str",
                       "hashtags": ["str"]
                   }
               ]
           }
       })

       # Store in Redis
       await redis.set(
           f"strategy:{business_url}:{timestamp}",
           strategy,
           ex=604800  # 7 days
       )

       return strategy
   ```

4. **Validate Strategy** (Duration: 10-15s)
   ```python
   async def validate_strategy(
       strategy: ContentStrategy,
       brand_voice: BrandVoice
   ) -> ValidationResult:
       # Use Claude to validate against brand guidelines
       validation = await claude.validate({
           "strategy": strategy,
           "brand_voice": brand_voice,
           "checks": [
               "tone_consistency",
               "theme_diversity",
               "competitor_differentiation",
               "trend_alignment",
               "engagement_potential"
           ]
       })

       if validation.score < 0.8:
           # Regenerate strategy with feedback
           return await generate_strategy(
               context,
               feedback=validation.issues
           )

       return validation
   ```

#### Outputs
```python
@dataclass
class ContentStrategy:
    business_url: str
    campaign_id: str
    created_at: datetime
    days: List[DayPlan]

@dataclass
class DayPlan:
    day: int  # 1-7
    theme: str
    content_type: Literal["image", "video", "carousel"]
    caption_direction: str  # High-level guidance
    image_concept: str  # Detailed prompt for Imagen
    video_concept: Optional[str]  # Detailed prompt for Veo
    cta: str  # Call to action
    hashtags: List[str]
    optimal_post_time: str  # Based on analytics
```

#### Error Handling
- **No past campaigns:** Rely on industry best practices
- **No analytics data:** Use competitor insights as proxy
- **Low validation score:** Retry up to 3 times with feedback

#### Performance Targets
- Total execution time: 60-90 seconds
- Strategy quality score: >0.8 (Claude self-validation)
- Theme diversity: All 7 days have distinct themes

---

### Agent 3: Creative Production Agent

**Responsibility:** Generate on-brand images, videos, and captions

#### Inputs
```python
@dataclass
class CreativeInputs:
    content_strategy: ContentStrategy  # From Agent 2
    brand_voice: BrandVoice  # From Agent 1
    product_images: List[str]  # S3 URLs from Agent 1
    redis_keys: List[str]
```

#### Processing Steps

1. **Generate Captions** (Duration: 20-30s per day)
   ```python
   async def generate_captions(
       day_plan: DayPlan,
       brand_voice: BrandVoice
   ) -> Caption:
       # Use Claude with brand voice context
       caption = await claude.generate({
           "model": "claude-sonnet-4.5",
           "temperature": 0.8,
           "system": f"""You are a social media copywriter.
                        Brand voice: {brand_voice.tone}
                        Writing style: {brand_voice.style}
                        Do's: {brand_voice.dos}
                        Don'ts: {brand_voice.donts}""",
           "prompt": f"""Create an engaging social media caption for:
                        Theme: {day_plan.theme}
                        Direction: {day_plan.caption_direction}
                        CTA: {day_plan.cta}

                        Requirements:
                        - 150-200 characters (first line must hook)
                        - Include emoji (but not excessive)
                        - End with clear CTA
                        - No hashtags in caption (separate)""",
           "output_format": {
               "hook": "str",  # First line
               "body": "str",  # Main message
               "cta": "str",   # Call to action
               "full_caption": "str"
           }
       })

       # Cache in Redis
       await redis.set(
           f"caption:{day_plan.day}:{timestamp}",
           caption,
           ex=86400
       )

       return caption
   ```

2. **Generate Images with Style References** (Duration: 45-60s per image)
   ```python
   async def generate_image(
       day_plan: DayPlan,
       product_images: List[str]
   ) -> Image:
       # Download reference images from S3
       references = await asyncio.gather(*[
           s3.download(url) for url in product_images[:3]
       ])

       # Use Google Vertex AI Imagen 3
       image = await vertex_imagen.generate({
           "prompt": f"""{day_plan.image_concept}

                        Style: Match the visual style, colors, and mood
                               of the reference images.
                        Quality: High resolution, professional photography
                        Composition: Rule of thirds, good lighting
                        Colors: Use brand colors: {brand_voice.colors}""",
           "reference_images": references,
           "aspect_ratio": "1:1",  # Instagram square
           "number_of_images": 2,  # Generate 2, pick best
           "safety_settings": "BLOCK_MEDIUM_AND_ABOVE"
       })

       # Use Claude to pick best image
       best = await claude.select_best({
           "images": image.candidates,
           "criteria": "brand alignment, visual appeal, clarity"
       })

       # Upload to S3
       s3_url = await s3.upload(
           best,
           bucket="brandmind-generated-assets",
           key=f"images/{campaign_id}/{day_plan.day}.jpg"
       )

       # Cache in Redis
       await redis.set(
           f"image:{day_plan.day}:{timestamp}",
           s3_url,
           ex=86400
       )

       return s3_url
   ```

3. **Generate Videos** (Duration: 90-120s per video)
   ```python
   async def generate_video(
       day_plan: DayPlan,
       brand_voice: BrandVoice
   ) -> Video:
       # Use Google Vertex AI Veo 2
       video = await vertex_veo.generate({
           "prompt": f"""{day_plan.video_concept}

                        Style: {brand_voice.visual_style}
                        Duration: 8 seconds
                        Aspect ratio: 9:16 (Instagram Stories/Reels)
                        Mood: {brand_voice.mood}
                        Colors: Emphasize {brand_voice.colors}

                        Requirements:
                        - Eye-catching first frame
                        - Smooth camera movements
                        - Professional quality
                        - No text overlays (will add separately)""",
           "duration_seconds": 8,
           "aspect_ratio": "9:16",
           "enhance_prompt": True,  # Veo improves prompt
           "output_gcs_uri": f"gs://brandmind-videos/{campaign_id}/{day_plan.day}"
       })

       # Poll for completion (async)
       operation = await vertex_veo.wait_for_completion(
           video.operation_id,
           timeout=120
       )

       # Download from GCS and upload to S3
       gcs_url = operation.result.video_uri
       video_bytes = await gcs.download(gcs_url)
       s3_url = await s3.upload(
           video_bytes,
           bucket="brandmind-generated-assets",
           key=f"videos/{campaign_id}/{day_plan.day}.mp4"
       )

       # Cache in Redis
       await redis.set(
           f"video:{day_plan.day}:{timestamp}",
           s3_url,
           ex=86400
       )

       return s3_url
   ```

4. **Parallel Generation** (Optimize for speed)
   ```python
   async def generate_all_content(
       strategy: ContentStrategy
   ) -> List[ContentAsset]:
       # Generate all 7 days in parallel
       tasks = []
       for day_plan in strategy.days:
           tasks.append(generate_day_content(day_plan))

       results = await asyncio.gather(*tasks, return_exceptions=True)

       # Handle failures gracefully
       assets = []
       for i, result in enumerate(results):
           if isinstance(result, Exception):
               logger.error(f"Day {i+1} generation failed: {result}")
               # Create placeholder asset
               assets.append(create_fallback_asset(i+1))
           else:
               assets.append(result)

       return assets

   async def generate_day_content(day_plan: DayPlan) -> ContentAsset:
       # Generate caption, image, video concurrently
       caption_task = generate_captions(day_plan, brand_voice)
       image_task = generate_image(day_plan, product_images)

       # Only generate video if needed
       video_task = None
       if day_plan.content_type == "video":
           video_task = generate_video(day_plan, brand_voice)

       # Wait for all
       caption, image = await asyncio.gather(caption_task, image_task)
       video = await video_task if video_task else None

       return ContentAsset(
           day=day_plan.day,
           caption=caption,
           image=image,
           video=video,
           hashtags=day_plan.hashtags,
           optimal_post_time=day_plan.optimal_post_time
       )
   ```

5. **Cache Management** (Redis optimization)
   ```python
   async def check_cache_before_generation(
       prompt_hash: str
   ) -> Optional[str]:
       # Check if similar prompt was generated recently
       similar = await redis.vector_search(
           query_embedding=await claude.embed(prompt_hash),
           index="generated_assets",
           threshold=0.95  # 95% similarity
       )

       if similar:
           logger.info(f"Cache hit for {prompt_hash}")
           return similar[0].asset_url

       return None
   ```

#### Outputs
```python
@dataclass
class ContentAsset:
    day: int
    caption: Caption
    image: str  # S3 URL
    video: Optional[str]  # S3 URL if video day
    hashtags: List[str]
    optimal_post_time: str
    generated_at: datetime

@dataclass
class Caption:
    hook: str
    body: str
    cta: str
    full_caption: str
```

#### Error Handling
- **Imagen generation fails:** Retry with simplified prompt, or use stock images
- **Veo timeout:** Skip video, use image + caption only
- **Safety filter triggers:** Regenerate with adjusted prompt
- **Cache miss:** Always generate fresh content

#### Performance Targets
- Caption generation: 20-30s per day
- Image generation: 45-60s per day
- Video generation: 90-120s per day
- Total for 7 days: 8-12 minutes (parallel execution)
- Cache hit rate: >30% for returning users

---

### Agent 4: Content Orchestration & Publishing Agent

**Responsibility:** Publish content to CMS, schedule across platforms, track performance

#### Inputs
```python
@dataclass
class OrchestrationInputs:
    content_assets: List[ContentAsset]  # From Agent 3
    strategy: ContentStrategy  # From Agent 2
    business_url: str
    social_handles: SocialHandles
```

#### Processing Steps

1. **Publish to Sanity CMS** (Duration: 30-45s)
   ```python
   async def publish_to_sanity(
       campaign: Campaign,
       assets: List[ContentAsset]
   ) -> SanityPublishResult:
       # Initialize Sanity client
       sanity = SanityClient(
           project_id=os.getenv("SANITY_PROJECT_ID"),
           dataset="production",
           token=os.getenv("SANITY_TOKEN")
       )

       # Create campaign document
       campaign_doc = await sanity.create({
           "_type": "campaign",
           "business_url": campaign.business_url,
           "campaign_id": campaign.campaign_id,
           "created_at": campaign.created_at.isoformat(),
           "status": "scheduled"
       })

       # Create content documents for each day
       content_docs = []
       for asset in assets:
           # Upload images/videos to Sanity
           image_asset = await sanity.upload_image(asset.image)
           video_asset = None
           if asset.video:
               video_asset = await sanity.upload_video(asset.video)

           # Create content document
           doc = await sanity.create({
               "_type": "content",
               "campaign": {"_ref": campaign_doc._id},
               "day": asset.day,
               "caption": asset.caption.full_caption,
               "hashtags": asset.hashtags,
               "image": {
                   "_type": "image",
                   "asset": {"_ref": image_asset._id}
               },
               "video": {
                   "_type": "file",
                   "asset": {"_ref": video_asset._id}
               } if video_asset else None,
               "scheduled_time": asset.optimal_post_time,
               "status": "pending"
           })

           content_docs.append(doc)

       # Store Sanity IDs in Redis
       await redis.set(
           f"sanity_campaign:{campaign.campaign_id}",
           {
               "campaign_id": campaign_doc._id,
               "content_ids": [doc._id for doc in content_docs]
           }
       )

       return SanityPublishResult(
           campaign_id=campaign_doc._id,
           content_ids=[doc._id for doc in content_docs],
           cms_url=f"https://brandmind.sanity.studio/desk/campaign;{campaign_doc._id}"
       )
   ```

2. **Schedule Posts via Postman** (Duration: 45-60s)
   ```python
   async def schedule_posts(
       assets: List[ContentAsset],
       social_handles: SocialHandles
   ) -> ScheduleResult:
       # Use Postman Collections to orchestrate social media APIs
       postman = PostmanClient(api_key=os.getenv("POSTMAN_API_KEY"))

       scheduled_posts = []

       for asset in assets:
           # Calculate actual post time
           post_datetime = datetime.now() + timedelta(days=asset.day)
           post_time = datetime.combine(
               post_datetime.date(),
               datetime.strptime(asset.optimal_post_time, "%H:%M").time()
           )

           # Schedule on Instagram (via Meta Graph API)
           if social_handles.instagram:
               ig_result = await postman.run_collection(
                   collection="Instagram_Post_Scheduler",
                   variables={
                       "access_token": social_handles.instagram_token,
                       "image_url": asset.image,
                       "caption": f"{asset.caption.full_caption}\\n\\n{' '.join(asset.hashtags)}",
                       "scheduled_time": post_time.isoformat()
                   }
               )
               scheduled_posts.append({
                   "platform": "instagram",
                   "post_id": ig_result.post_id,
                   "scheduled_time": post_time
               })

           # Schedule on Facebook
           if social_handles.facebook:
               fb_result = await postman.run_collection(
                   collection="Facebook_Post_Scheduler",
                   variables={
                       "access_token": social_handles.facebook_token,
                       "image_url": asset.image,
                       "message": f"{asset.caption.full_caption}\\n\\n{' '.join(asset.hashtags)}",
                       "scheduled_publish_time": int(post_time.timestamp())
                   }
               )
               scheduled_posts.append({
                   "platform": "facebook",
                   "post_id": fb_result.post_id,
                   "scheduled_time": post_time
               })

           # Schedule on Twitter/X
           if social_handles.twitter:
               twitter_result = await postman.run_collection(
                   collection="Twitter_Post_Scheduler",
                   variables={
                       "bearer_token": social_handles.twitter_token,
                       "text": f"{asset.caption.full_caption} {' '.join(asset.hashtags[:3])}",  # Twitter hashtag limit
                       "media_url": asset.image
                   }
               )
               scheduled_posts.append({
                   "platform": "twitter",
                   "post_id": twitter_result.tweet_id,
                   "scheduled_time": post_time
               })

       # Store schedule in Redis
       await redis.set(
           f"schedule:{campaign.campaign_id}",
           scheduled_posts,
           ex=604800  # 7 days
       )

       return ScheduleResult(scheduled_posts=scheduled_posts)
   ```

3. **Track Performance** (Continuous)
   ```python
   async def track_performance(
       campaign_id: str
   ) -> PerformanceMetrics:
       # Get scheduled posts from Redis
       schedule = await redis.get(f"schedule:{campaign_id}")

       metrics = []
       for post in schedule:
           # Use Postman to query analytics
           if post["platform"] == "instagram":
               stats = await postman.run_collection(
                   collection="Instagram_Insights",
                   variables={
                       "post_id": post["post_id"],
                       "metrics": "engagement,impressions,reach,likes,comments,shares"
                   }
               )
           elif post["platform"] == "facebook":
               stats = await postman.run_collection(
                   collection="Facebook_Insights",
                   variables={
                       "post_id": post["post_id"],
                       "metrics": "post_impressions,post_engaged_users,post_reactions"
                   }
               )
           elif post["platform"] == "twitter":
               stats = await postman.run_collection(
                   collection="Twitter_Analytics",
                   variables={
                       "tweet_id": post["post_id"]
                   }
               )

           metrics.append({
               "post_id": post["post_id"],
               "platform": post["platform"],
               "stats": stats.data
           })

       # Store metrics in Redis for learning
       await redis.set(
           f"metrics:{campaign_id}",
           metrics,
           ex=2592000  # 30 days
       )

       # Update Sanity CMS with performance data
       await sanity.patch_multiple(
           [{"_id": post["sanity_id"], "metrics": post["stats"]}
            for post in metrics]
       )

       return PerformanceMetrics(campaign_id=campaign_id, posts=metrics)
   ```

4. **Learning Loop** (Continuous)
   ```python
   async def learn_from_performance(
       campaign_id: str
   ) -> LearningInsights:
       # Get all metrics
       metrics = await redis.get(f"metrics:{campaign_id}")

       # Use Claude to analyze patterns
       insights = await claude.analyze({
           "data": metrics,
           "task": """Analyze performance and extract learnings:
                   - Which content types performed best?
                   - Which themes had highest engagement?
                   - Which posting times were optimal?
                   - What caption styles resonated?
                   - What visual styles worked?"""
       })

       # Store learnings as embeddings in Redis
       await redis.store_with_embeddings(
           key=f"learnings:{campaign.business_url}:{timestamp}",
           data=insights,
           embeddings=await claude.embed(str(insights))
       )

       # These learnings will be retrieved by Agent 2 in future campaigns
       return insights
   ```

#### Outputs
```python
@dataclass
class OrchestrationResult:
    sanity_publish: SanityPublishResult
    schedule: ScheduleResult
    cms_dashboard_url: str

@dataclass
class PerformanceMetrics:
    campaign_id: str
    posts: List[PostMetrics]

@dataclass
class PostMetrics:
    post_id: str
    platform: str
    impressions: int
    engagement_rate: float
    likes: int
    comments: int
    shares: int
    collected_at: datetime
```

#### Error Handling
- **Sanity upload fails:** Retry 3x, fallback to S3 links
- **Social API auth fails:** Store locally, prompt user to re-auth
- **Postman collection fails:** Direct API fallback
- **Performance tracking fails:** Continue without metrics, log error

#### Performance Targets
- Sanity publish: 30-45s
- Schedule all platforms: 45-60s
- Total orchestration: 90-120s
- Performance tracking: Real-time (webhook-based)

---

## 4. Data Models

### Redis Data Structures

#### Vector Indexes
```python
# campaigns index
{
    "index_name": "campaigns",
    "vector_dimensions": 1536,  # Claude embeddings
    "distance_metric": "COSINE",
    "fields": [
        "campaign_id",
        "business_url",
        "industry",
        "content_summary",  # Vectorized
        "performance_score",
        "created_at"
    ]
}

# research index
{
    "index_name": "research",
    "vector_dimensions": 1536,
    "fields": [
        "business_url",
        "research_type",  # website|competitor|trends
        "content",  # Vectorized
        "extracted_at"
    ]
}

# generated_assets index
{
    "index_name": "generated_assets",
    "vector_dimensions": 1536,
    "fields": [
        "prompt_hash",  # Vectorized
        "asset_url",
        "asset_type",  # image|video|caption
        "generated_at"
    ]
}
```

#### Key-Value Patterns
```python
# Business context
"business:{url}" -> {
    "name": str,
    "industry": str,
    "products": List[str],
    "target_audience": str,
    "website_content": str
}

# Brand voice
"brand_voice:{url}" -> {
    "tone": str,
    "style": str,
    "colors": List[str],
    "dos": List[str],
    "donts": List[str]
}

# Product images
"product_images:{url}" -> List[str]  # S3 URLs

# Competitor insights
"competitor:{url}:{competitor_name}" -> {
    "social_handles": dict,
    "top_posts": List[dict],
    "content_themes": List[str],
    "visual_style": str
}

# Content strategy
"strategy:{url}:{timestamp}" -> ContentStrategy

# Generated assets
"caption:{day}:{timestamp}" -> Caption
"image:{day}:{timestamp}" -> str  # S3 URL
"video:{day}:{timestamp}" -> str  # S3 URL

# Schedule
"schedule:{campaign_id}" -> List[ScheduledPost]

# Performance metrics
"metrics:{campaign_id}" -> List[PostMetrics]

# Learnings
"learnings:{url}:{timestamp}" -> LearningInsights
```

### Sanity CMS Schema

```javascript
// campaign.js
export default {
  name: 'campaign',
  title: 'Campaign',
  type: 'document',
  fields: [
    {
      name: 'business_url',
      title: 'Business URL',
      type: 'url'
    },
    {
      name: 'campaign_id',
      title: 'Campaign ID',
      type: 'string'
    },
    {
      name: 'created_at',
      title: 'Created At',
      type: 'datetime'
    },
    {
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: ['scheduled', 'publishing', 'completed']
      }
    }
  ]
}

// content.js
export default {
  name: 'content',
  title: 'Content',
  type: 'document',
  fields: [
    {
      name: 'campaign',
      title: 'Campaign',
      type: 'reference',
      to: [{type: 'campaign'}]
    },
    {
      name: 'day',
      title: 'Day',
      type: 'number'
    },
    {
      name: 'caption',
      title: 'Caption',
      type: 'text'
    },
    {
      name: 'hashtags',
      title: 'Hashtags',
      type: 'array',
      of: [{type: 'string'}]
    },
    {
      name: 'image',
      title: 'Image',
      type: 'image'
    },
    {
      name: 'video',
      title: 'Video',
      type: 'file'
    },
    {
      name: 'scheduled_time',
      title: 'Scheduled Time',
      type: 'string'
    },
    {
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: ['pending', 'published', 'failed']
      }
    },
    {
      name: 'metrics',
      title: 'Performance Metrics',
      type: 'object',
      fields: [
        {name: 'impressions', type: 'number'},
        {name: 'engagement_rate', type: 'number'},
        {name: 'likes', type: 'number'},
        {name: 'comments', type: 'number'},
        {name: 'shares', type: 'number'}
      ]
    }
  ]
}
```

### PostgreSQL Schema (Optional - for user accounts)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    business_url VARCHAR(500) NOT NULL,
    business_name VARCHAR(255),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    campaign_id VARCHAR(100) UNIQUE NOT NULL,
    redis_keys JSONB,
    sanity_campaign_id VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    platform VARCHAR(50),  -- instagram, facebook, twitter
    handle VARCHAR(255),
    access_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. API Integrations

### Sponsor Tools

#### 1. Redis (RedisVL)
```python
# Setup
from redis import Redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

redis_client = Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# Create vector index
schema = (
    TextField("campaign_id"),
    TextField("business_url"),
    VectorField("embedding",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": 1536,
            "DISTANCE_METRIC": "COSINE"
        }
    )
)

redis_client.ft("campaigns").create_index(
    schema,
    definition=IndexDefinition(prefix=["campaign:"], index_type=IndexType.HASH)
)

# Vector search
from redis.commands.search.query import Query

query = Query("*=>[KNN 5 @embedding $vec AS score]")
results = redis_client.ft("campaigns").search(
    query,
    query_params={"vec": embedding_vector}
)
```

#### 2. Sanity CMS
```python
from sanity import Client

sanity = Client({
    "project_id": os.getenv("SANITY_PROJECT_ID"),
    "dataset": "production",
    "token": os.getenv("SANITY_TOKEN"),
    "api_version": "2025-01-01"
})

# Create document
doc = sanity.create({
    "_type": "campaign",
    "business_url": "https://example.com"
})

# Upload image
with open("image.jpg", "rb") as f:
    image_asset = sanity.upload_image(f)

# Query
campaigns = sanity.query('*[_type == "campaign"]')
```

#### 3. Postman
```python
import requests

POSTMAN_API_KEY = os.getenv("POSTMAN_API_KEY")

# Run collection
response = requests.post(
    "https://api.postman.com/collections/{collection_id}/runs",
    headers={"X-Api-Key": POSTMAN_API_KEY},
    json={
        "collection": collection_id,
        "environment": environment_id,
        "data": variables
    }
)

# Alternative: Use Postman Collections SDK
from postman import Collection

collection = Collection.from_url(
    "https://www.postman.com/collections/instagram-scheduler"
)
result = collection.run(variables={"access_token": token})
```

#### 4. Lightpanda
```python
from puppeteer import connect

browser = await connect({
    "browserWSEndpoint": f"wss://euwest.cloud.lightpanda.io/ws?token={LIGHTPANDA_TOKEN}"
})

page = await browser.newPage()
await page.goto("https://example.com")

# Extract images
images = await page.evaluate('''() => {
    return Array.from(document.querySelectorAll('img'))
        .map(img => img.src)
}''')

await browser.close()
```

#### 5. Anthropic Claude
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Generate content
response = client.messages.create(
    model="claude-sonnet-4.5-20250929",
    max_tokens=2048,
    temperature=0.7,
    system="You are a social media strategist.",
    messages=[{
        "role": "user",
        "content": "Create a 7-day content strategy..."
    }]
)

# Get embeddings (via extended API or use separate service)
embeddings = client.embeddings.create(
    input=["text to embed"],
    model="claude-embeddings-v1"
)
```

#### 6. AWS Services
```python
import boto3

# S3
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

s3.upload_file('image.jpg', 'brandmind-assets', 'path/to/image.jpg')

# ECS (for deployment)
ecs = boto3.client('ecs')
ecs.update_service(
    cluster='brandmind-cluster',
    service='brandmind-api',
    forceNewDeployment=True
)

# Lambda (for scheduled tasks)
lambda_client = boto3.client('lambda')
lambda_client.invoke(
    FunctionName='trackPerformance',
    InvocationType='Event',
    Payload=json.dumps({"campaign_id": campaign_id})
)
```

### Google Cloud Services

#### 1. Vertex AI Imagen 3
```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

aiplatform.init(project=GCP_PROJECT_ID, location="us-central1")

model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

images = model.generate_images(
    prompt="A coffee shop storefront with warm lighting",
    number_of_images=2,
    aspect_ratio="1:1",
    safety_filter_level="block_medium_and_above",
    add_watermark=False
)

# Save to GCS
for i, image in enumerate(images):
    image.save(f"gs://brandmind-images/output_{i}.jpg")
```

#### 2. Vertex AI Veo 2
```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import VideoGenerationModel

model = VideoGenerationModel.from_pretrained("veo-2.0-generate-001")

response = model.generate_videos(
    prompt="A barista making latte art in a cozy coffee shop",
    duration_seconds=8,
    aspect_ratio="9:16",
    output_gcs_uri="gs://brandmind-videos/output"
)

# Poll for completion
import time
while not response.done():
    time.sleep(10)
    response.refresh()

video_uri = response.result().videos[0].uri
```

#### 3. Vertex AI Search & Grounded Generation
```python
from google.cloud import discoveryengine_v1 as discoveryengine

# Search
client = discoveryengine.SearchServiceClient()

request = discoveryengine.SearchRequest(
    serving_config=f"projects/{project}/locations/global/collections/default_collection/dataStores/{datastore}/servingConfigs/default_config",
    query="coffee shop industry trends 2025"
)

response = client.search(request)

# Grounded Generation
from vertexai.preview.generative_models import GenerativeModel

model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content(
    "What are current trends in the coffee industry?",
    generation_config={
        "grounding_source": "google_search"
    }
)

print(response.text)
print(response.grounding_metadata)  # Citations
```

### Social Media APIs (via Postman)

#### Instagram Graph API
```python
# Schedule post
POST https://graph.facebook.com/v18.0/{ig_user_id}/media
{
    "image_url": "https://s3.../image.jpg",
    "caption": "Caption text #hashtags",
    "access_token": "{token}"
}

# Get insights
GET https://graph.facebook.com/v18.0/{media_id}/insights
?metric=engagement,impressions,reach
&access_token={token}
```

#### Facebook Graph API
```python
# Schedule post
POST https://graph.facebook.com/v18.0/{page_id}/photos
{
    "url": "https://s3.../image.jpg",
    "message": "Caption text",
    "published": false,
    "scheduled_publish_time": 1234567890,
    "access_token": "{token}"
}
```

#### Twitter/X API v2
```python
# Create tweet with media
POST https://api.twitter.com/2/tweets
Authorization: Bearer {token}
{
    "text": "Caption text #hashtags",
    "media": {
        "media_ids": ["{media_id}"]
    }
}

# Get analytics
GET https://api.twitter.com/2/tweets/{id}
?tweet.fields=public_metrics
```

---

## 6. Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **Async:** asyncio, aiohttp
- **Task Queue:** Celery + Redis (for long-running jobs)
- **Validation:** Pydantic v2

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5.3+
- **UI:** Tailwind CSS + shadcn/ui components
- **State:** React Context + TanStack Query
- **Forms:** React Hook Form + Zod

### Infrastructure
- **Hosting:** AWS ECS Fargate
- **Storage:** AWS S3 + Google Cloud Storage
- **Database:** Redis (primary) + PostgreSQL (user accounts)
- **CDN:** AWS CloudFront
- **Monitoring:** AWS CloudWatch + Sentry

### AI/ML Services
- **LLM:** Anthropic Claude Sonnet 4.5
- **Image Gen:** Google Vertex AI Imagen 3
- **Video Gen:** Google Vertex AI Veo 2
- **Search:** Vertex AI Search + Grounded Generation
- **Embeddings:** Claude embeddings API

### Sponsor Integrations
- **Redis:** Vector database, caching, session store
- **Sanity:** Content management system
- **Postman:** API orchestration and monitoring
- **Lightpanda:** Web scraping and automation
- **AWS:** Cloud infrastructure
- **Anthropic:** AI reasoning and content generation

### Development Tools
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Containerization:** Docker + Docker Compose
- **Testing:** pytest (backend), Jest (frontend)
- **Code Quality:** Black, Ruff, ESLint, Prettier

---

## 7. User Flows

### Flow 1: First-Time User - Generate Campaign

```
1. User lands on homepage
   └─> Clear value prop: "AI Marketing Agent - 7 days of content in 5 minutes"

2. User clicks "Get Started"
   └─> Input form appears

3. User enters:
   └─> Business URL (required)
   └─> Instagram handle (optional)
   └─> Facebook page (optional)
   └─> Twitter handle (optional)
   └─> [Optional] Competitor URLs

4. User clicks "Generate Content"
   └─> Loading screen with progress indicators
       ├─> "🔍 Researching your business..." (Agent 1)
       ├─> "🎯 Creating strategy..." (Agent 2)
       ├─> "🎨 Generating content..." (Agent 3)
       └─> "📅 Publishing to CMS..." (Agent 4)

5. Progress updates (real-time via WebSocket)
   └─> "Analyzed website"
   └─> "Found 12 product images"
   └─> "Identified 3 competitors"
   └─> "Generated 7-day strategy"
   └─> "Creating day 1 content..."
   └─> ...
   └─> "Publishing to Sanity CMS"

6. Results dashboard appears (3-4 minutes later)
   ├─> Campaign summary card
   │   └─> Industry, brand voice, key themes
   ├─> Content calendar (7 days)
   │   └─> Each day shows: image, video, caption, hashtags
   ├─> Competitive insights
   │   └─> What competitors are doing, opportunities
   └─> CTA: "View in Sanity CMS" | "Schedule Posts"

7. User clicks "View in Sanity CMS"
   └─> Opens Sanity Studio in new tab
   └─> User sees full content calendar with editing capabilities

8. User clicks "Schedule Posts"
   └─> OAuth flow for social media platforms
   └─> User authorizes Instagram, Facebook, Twitter
   └─> System schedules all 7 posts
   └─> Confirmation: "All posts scheduled! 🎉"
```

### Flow 2: Returning User - View Performance

```
1. User logs in
   └─> Dashboard shows past campaigns

2. User clicks on a campaign
   └─> Campaign detail page

3. Performance metrics displayed
   ├─> Total impressions
   ├─> Engagement rate
   ├─> Top performing post
   └─> Trend graph (7 days)

4. User sees "Learnings" section
   └─> "Your audience engages most with product close-ups"
   └─> "Posts at 10 AM get 40% more engagement"
   └─> "Educational content outperforms promotional"

5. User clicks "Generate Next Campaign"
   └─> System uses learnings from Redis
   └─> Strategy automatically incorporates insights
   └─> Better content generated based on past performance
```

### Flow 3: Edit Content in Sanity

```
1. User opens Sanity Studio from email/dashboard
   └─> Sees campaign with 7 content items

2. User clicks on Day 3 content
   └─> Editor opens

3. User can edit:
   ├─> Caption text
   ├─> Hashtags
   ├─> Image (replace or adjust)
   ├─> Scheduled time
   └─> Status (pending → approved)

4. User clicks "Publish"
   └─> Changes saved in Sanity
   └─> Backend syncs with Redis
   └─> Social media schedule updated via Postman

5. User can preview content
   └─> See how it looks on Instagram, Facebook, Twitter
```

---

## 8. Success Criteria

### Judging Criteria Alignment (20% each)

#### 1. Autonomy (20%)
**Target Score: 18/20**

✅ **Agent acts on real-time data without manual intervention:**
- Agent 1 autonomously discovers business context (scraping, research)
- No user input needed beyond initial URL
- System learns from performance data and adapts
- Competitors monitored automatically
- Industry trends fetched in real-time

**Demo Points:**
- Show Agent 1 discovering product images, brand voice, competitors
- Show Redis vector search retrieving past learnings
- Show performance tracking feeding back into strategy

---

#### 2. Idea (20%)
**Target Score: 19/20**

✅ **Solves meaningful problem:**
- $50B+ social media marketing industry
- 33M US small businesses struggle with consistent content
- Current solutions: $2-5K/month agencies OR 10-20 hrs/week manual work

✅ **Real-world value:**
- Save 10-20 hrs/week for business owners
- Reduce cost from $2-5K/month → $99-299/month
- Improve content quality with AI + competitive intelligence
- Learn and improve over time (not one-shot)

**Demo Points:**
- Show before/after: Manual process vs autonomous agent
- Show cost savings calculation
- Show learning loop improving content quality

---

#### 3. Technical Implementation (20%)
**Target Score: 19/20**

✅ **Production-grade code:**
- Full error handling and retries
- Async/parallel processing for speed
- Comprehensive data models
- Proper authentication and security
- Monitoring and logging

✅ **Architecture:**
- Clean 4-agent separation of concerns
- Event-driven communication
- Redis for state management
- Sanity for content persistence
- AWS for scalability

**Demo Points:**
- Show architecture diagram
- Show parallel agent execution
- Show Redis vector search in action
- Show Sanity CMS integration
- Show error handling (simulate failure)

---

#### 4. Tool Use (20%)
**Target Score: 20/20**

✅ **Uses 6 sponsor tools effectively:**

1. **Redis** (Deep integration)
   - Vector search for past campaigns
   - Semantic caching for AI generations
   - Session store for user state
   - Performance metrics storage
   - Learnings database

2. **Sanity CMS** (Deep integration)
   - Content calendar management
   - Real-time collaboration
   - Asset management (images, videos)
   - Performance tracking UI
   - Client deliverables

3. **Postman** (Deep integration)
   - Orchestrate 3+ social media APIs
   - Schedule posts across platforms
   - Monitor API health
   - Collect analytics data

4. **Lightpanda** (Deep integration)
   - Scrape business websites (faster than Chrome)
   - Scrape competitor social media
   - Extract product images
   - Monitor trends

5. **Anthropic Claude** (Deep integration)
   - All agent reasoning
   - Content generation
   - Strategy planning
   - Performance analysis
   - Embeddings for vector search

6. **AWS** (Moderate integration)
   - ECS for container hosting
   - S3 for asset storage
   - Lambda for scheduled tasks
   - CloudWatch for monitoring

**Demo Points:**
- Show Redis vector search query
- Show Sanity CMS content management
- Show Postman API orchestration logs
- Show Lightpanda scraping in real-time
- Show Claude generating strategy + content
- Show AWS deployment architecture

---

#### 5. Presentation (Demo) (20%)
**Target Score: 19/20**

**3-Minute Demo Script:**

**0:00-0:30 - Problem (Hook)**
> "Small businesses spend 10-20 hours every week creating social media content. Agencies charge $2-5K per month. Most businesses post inconsistently or not at all, missing out on customers."

**0:30-1:00 - Solution (Introduce BrandMind AI)**
> "BrandMind AI is an autonomous 4-agent system that creates a week of branded content in 5 minutes. Just give it your website URL."

**1:00-2:30 - Live Demo**
> - Enter business URL: "https://bluebottlecoffee.com"
> - Click "Generate Content"
> - Show Agent 1 discovering: products, brand voice, competitors (Starbucks, Peet's)
> - Show Agent 2 creating strategy: 7 themed days
> - Show Agent 3 generating: captions, images, videos (live)
> - Show Agent 4 publishing to Sanity CMS
> - Open Sanity Studio: see full content calendar
> - Click "Schedule Posts": posts scheduled across Instagram, Facebook, Twitter

**2:30-3:00 - Technical Highlights & Impact**
> "Behind the scenes: Redis stores agent memory, Lightpanda scrapes competitors 10x faster, Claude powers all reasoning, Sanity manages content, Postman orchestrates APIs. The system learns from performance and improves over time. No more $2-5K/month. No more 10-20 hours/week. Just 5 minutes."

**Recording:**
- Pre-record full 3-minute demo (backup)
- Prepare live demo (preferred)
- Have screenshots ready (fallback)

---

### Technical Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| End-to-end execution time | <5 minutes | 95th percentile |
| Agent 1 (Research) | <3 minutes | Average |
| Agent 2 (Strategy) | <90 seconds | Average |
| Agent 3 (Creative) | <10 minutes (parallel) | Average for 7 days |
| Agent 4 (Orchestration) | <2 minutes | Average |
| Redis vector search latency | <100ms | p99 |
| Image generation success rate | >95% | Per request |
| Video generation success rate | >90% | Per request |
| System uptime | >99.5% | During hackathon demo |

---

## 9. Implementation Phases

### Phase 1: Setup & Infrastructure (Hour 1-2)

**Time: 9:30 AM - 11:30 AM (Keynote + Setup)**

1. **Create GitHub Repository**
   ```bash
   git init brandmind-ai
   cd brandmind-ai
   # Add README, .gitignore, LICENSE
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Set up Project Structure**
   ```
   brandmind-ai/
   ├── backend/
   │   ├── agents/
   │   │   ├── __init__.py
   │   │   ├── research_agent.py
   │   │   ├── strategy_agent.py
   │   │   ├── creative_agent.py
   │   │   └── orchestration_agent.py
   │   ├── services/
   │   │   ├── redis_service.py
   │   │   ├── claude_service.py
   │   │   ├── lightpanda_service.py
   │   │   ├── sanity_service.py
   │   │   ├── postman_service.py
   │   │   ├── vertex_service.py
   │   │   └── aws_service.py
   │   ├── models.py
   │   ├── orchestrator.py
   │   ├── main.py
   │   ├── requirements.txt
   │   └── Dockerfile
   ├── frontend/
   │   ├── app/
   │   │   ├── page.tsx
   │   │   ├── dashboard/
   │   │   └── layout.tsx
   │   ├── components/
   │   ├── lib/
   │   ├── package.json
   │   └── Dockerfile
   ├── infrastructure/
   │   ├── terraform/
   │   └── docker-compose.yml
   └── README.md
   ```

3. **Set up Redis**
   - Sign up for Redis Cloud (free tier)
   - Create vector index for campaigns
   - Test connection

4. **Set up Sanity CMS**
   - Create Sanity project
   - Define schemas (campaign, content)
   - Deploy Sanity Studio

5. **Get API Keys**
   - Anthropic API key
   - Lightpanda token
   - Postman API key
   - AWS credentials
   - Google Cloud credentials

6. **Environment Variables**
   ```bash
   # backend/.env
   REDIS_HOST=...
   REDIS_PASSWORD=...
   ANTHROPIC_API_KEY=...
   LIGHTPANDA_TOKEN=...
   POSTMAN_API_KEY=...
   SANITY_PROJECT_ID=...
   SANITY_TOKEN=...
   AWS_ACCESS_KEY=...
   GCP_PROJECT_ID=...
   ```

**Deliverable:** All infrastructure set up, API keys working, git repo initialized

---

### Phase 2: Core Agent Implementation (Hour 3-7)

**Time: 11:30 AM - 3:30 PM (Core Coding)**

#### Hour 3: Agent 1 - Research Agent (11:30 AM - 12:30 PM)
- Implement Lightpanda web scraping
- Implement website analysis with Claude
- Implement product image collection
- Implement Redis storage with embeddings
- Test on 3 sample businesses

#### Hour 4: Agent 2 - Strategy Agent (12:30 PM - 1:30 PM)
- Implement Redis vector search
- Implement Claude strategy generation
- Implement 7-day content calendar
- Test with Agent 1 output

**Lunch Break: 1:30 PM - 2:00 PM**

#### Hour 5: Agent 3 - Creative Agent (2:00 PM - 3:00 PM)
- Implement caption generation with Claude
- Implement image generation with Imagen
- Implement video generation with Veo
- Implement parallel execution
- Test with Agent 2 output

#### Hour 6: Agent 4 - Orchestration Agent (3:00 PM - 4:00 PM)
- Implement Sanity CMS publishing
- Implement Postman API scheduling
- Implement performance tracking
- Test end-to-end flow

**Deliverable:** All 4 agents working end-to-end

---

### Phase 3: Frontend & Integration (Hour 8-9)

**Time: 3:30 PM - 4:30 PM (Deadline at 4:30 PM)**

#### Hour 8: Frontend (3:30 PM - 4:00 PM)
- Build input form
- Build loading screen with progress
- Build results dashboard
- Connect to backend API
- Test user flow

#### Hour 9: Polish & Testing (4:00 PM - 4:30 PM)
- End-to-end testing
- Error handling
- Performance optimization
- Demo preparation
- Commit and push all code

**Deliverable:** Working demo ready for submission

---

### Phase 4: Submission & Demo Prep (Hour 10)

**Time: 4:30 PM - 5:00 PM (Project Submission Deadline at 4:30 PM)**

1. **Submit Project**
   - GitHub URL
   - Live demo URL (if deployed)
   - Video demo (if required)

2. **Prepare Demo**
   - Practice 3-minute pitch
   - Test live demo
   - Prepare backup recording
   - Prepare architecture slides

**Deliverable:** Project submitted, demo prepared

---

## 10. Deployment Strategy

### Development (Local)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080

# Frontend
cd frontend
npm install
npm run dev
```

### Production (AWS ECS)

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### Docker Compose (Local Testing)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    env_file:
      - ./backend/.env
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080

  redis:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"
      - "8001:8001"
```

#### AWS ECS Deployment
```bash
# Build and push images
docker build -t brandmind-backend ./backend
docker tag brandmind-backend:latest {ECR_URL}/brandmind-backend:latest
docker push {ECR_URL}/brandmind-backend:latest

docker build -t brandmind-frontend ./frontend
docker tag brandmind-frontend:latest {ECR_URL}/brandmind-frontend:latest
docker push {ECR_URL}/brandmind-frontend:latest

# Deploy to ECS
aws ecs update-service \
  --cluster brandmind-cluster \
  --service brandmind-backend \
  --force-new-deployment

aws ecs update-service \
  --cluster brandmind-cluster \
  --service brandmind-frontend \
  --force-new-deployment
```

---

## Appendix A: Environment Variables

```bash
# Redis
REDIS_HOST=your-redis-host.redislabs.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Lightpanda
LIGHTPANDA_TOKEN=your-lightpanda-token

# Sanity
SANITY_PROJECT_ID=your-project-id
SANITY_DATASET=production
SANITY_TOKEN=your-token

# Postman
POSTMAN_API_KEY=PMAK-...

# Google Cloud
GCP_PROJECT_ID=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET=brandmind-assets

# Social Media (for demo)
INSTAGRAM_ACCESS_TOKEN=...
FACEBOOK_ACCESS_TOKEN=...
TWITTER_BEARER_TOKEN=...
```

---

## Appendix B: Hackathon Checklist

### Before Hackathon (Tonight)
- [ ] Read this spec thoroughly
- [ ] Set up all API keys and accounts
- [ ] Test Redis connection
- [ ] Test Claude API
- [ ] Test Lightpanda
- [ ] Prepare sample business URLs for testing
- [ ] Review Sanity CMS docs
- [ ] Review Postman Collections docs
- [ ] Sleep well!

### During Hackathon (Tomorrow)
- [ ] 9:30 AM: Arrive, set up workstation
- [ ] 10:00 AM: Attend keynote, network with sponsors
- [ ] 11:00 AM: Start coding - Phase 1 (Infrastructure)
- [ ] 11:30 AM: Phase 2 begins (Agent 1)
- [ ] 12:30 PM: Agent 2
- [ ] 1:30 PM: Lunch
- [ ] 2:00 PM: Agent 3
- [ ] 3:00 PM: Agent 4
- [ ] 3:30 PM: Frontend
- [ ] 4:00 PM: Polish & testing
- [ ] 4:30 PM: Submit project
- [ ] 5:00 PM: Finalists announced, prepare demo
- [ ] 6:00 PM: Demo presentation (3 minutes)
- [ ] 7:00 PM: Awards ceremony

### Post-Hackathon
- [ ] Get judge feedback
- [ ] Network with sponsors
- [ ] Deploy production version
- [ ] Write blog post about experience
- [ ] Add to portfolio

---

## Appendix C: Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits hit | Medium | High | Implement caching, use Redis aggressively |
| Video generation too slow | Medium | Medium | Generate videos asynchronously, show progress |
| Lightpanda scraping blocked | Low | Medium | Fallback to Grounded Generation API |
| Sanity setup complex | Low | Medium | Use pre-built templates, simplify schema |
| Network issues during demo | Medium | High | Pre-record backup demo video |
| Time runs out | Medium | High | Prioritize core flow, skip polish features |
| Redis connection issues | Low | High | Test thoroughly beforehand, have fallback in-memory cache |

---

**End of Technical Specification**

**Version:** 1.0
**Last Updated:** November 20, 2025
**Ready for:** Production Agents Hackathon (November 21, 2025)
