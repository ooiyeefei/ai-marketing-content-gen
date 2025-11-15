# Configuration Guide - OBI-RUN-KENOBI Backend

## Table of Contents
1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Configuration Files](#configuration-files)
4. [Cost Control](#cost-control)
5. [Content Limits](#content-limits)
6. [Cost Estimates](#cost-estimates)
7. [Development vs Production](#development-vs-production)
8. [Authentication Setup](#authentication-setup)

---

## Overview

This guide covers all configuration options for the OBI-RUN-KENOBI backend, including cost control, content limits, and environment-specific settings.

**Key Features:**
- Configurable video and image generation (enable/disable via environment variables)
- Fixed content limits to control costs (3 videos, 3 images per post)
- Optimized video duration (5 seconds per segment, reduced from 8 seconds)
- Placeholder mode for free development and testing

---

## Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | `my-project-123` | Yes |
| `GCP_REGION` | GCP Region for Vertex AI | `us-central1` | Yes |
| `STORAGE_BUCKET` | Cloud Storage bucket name | `my-media-bucket` | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | `AIza...` | Yes |

### Cost Control Variables

| Variable | Description | Default | Values |
|----------|-------------|---------|--------|
| `ENABLE_VIDEOS` | Enable Veo 2.0 video generation | `false` | `true` or `false` |
| `ENABLE_IMAGES` | Enable Imagen 3 image generation | `false` | `true` or `false` |

**Important:** These flags control whether actual API calls are made. When set to `false`, the system uses placeholder URIs instead, allowing for fast, free development and testing.

---

## Configuration Files

### 1. `.env.example`
Template file with all configuration options and documentation. Copy this to create your own `.env` file:
```bash
cp .env.example .env
```

### 2. `.env.development`
Pre-configured development environment with safe defaults:
- `ENABLE_VIDEOS=false`
- `ENABLE_IMAGES=false`

**Usage:**
```bash
# Automatically loaded by config.py
# Use for local development to avoid costs
```

### 3. `config.py`
Central configuration module that loads environment variables and defines content limits.

**Key Settings:**
```python
# Content Limits (hardcoded for consistency)
max_videos_per_post: int = 3       # Max video segments per post
max_images_per_post: int = 3       # Max image generations per post

# Video Settings (optimized for demo)
video_duration_seconds: int = 5    # Reduced from 8 seconds
video_resolution: str = "720p"     # Required for Veo extension

# Cost Control Flags (from environment variables)
enable_video_generation: bool      # From ENABLE_VIDEOS
enable_image_generation: bool      # From ENABLE_IMAGES
```

---

## Cost Control

### How It Works

The system supports two modes:

#### 1. Placeholder Mode (Cost: $0)
- **When:** `ENABLE_VIDEOS=false` and `ENABLE_IMAGES=false`
- **Behavior:** Returns placeholder URIs instead of generating actual media
- **Speed:** Instant (no API calls)
- **Use Case:** Development, testing, CI/CD

**Example Output:**
```json
{
  "video_segments": [
    {
      "segment_number": 1,
      "uri": "placeholder://video-segment-1",
      "duration_seconds": 5,
      "prompt_used": "Close-up of signature dish..."
    }
  ]
}
```

#### 2. Generation Mode (Cost: See below)
- **When:** `ENABLE_VIDEOS=true` or `ENABLE_IMAGES=true`
- **Behavior:** Makes actual API calls to Veo 2.0 and Imagen 3
- **Speed:** 2-5 minutes per video, 30-60 seconds per image
- **Use Case:** Demo, production, final content

---

## Content Limits

### Per-Post Limits (Enforced in Code)

| Content Type | Limit | Duration/Size | Configuration |
|--------------|-------|---------------|---------------|
| Video Segments | 3 | 5 seconds each | `max_videos_per_post = 3` |
| Images | 3 | 1:1 aspect ratio | `max_images_per_post = 3` |
| Video Resolution | 720p | Required for extension | `video_resolution = "720p"` |

### Enforcement Points

1. **Agent 2 (Content Strategist)**
   - Generates exactly 3 video prompts per post
   - Generates exactly 3 image prompts per post
   - Validates prompt counts in `_generate_calendar()`
   - Fallback calendar also enforces limits

2. **Agent 3 (Creative Producer)**
   - Limits video generation to `max_videos_per_post`
   - Limits image generation to `max_images_per_post`
   - Uses `video_duration_seconds` for all videos
   - Respects `enable_video_generation` and `enable_image_generation` flags

### Why These Limits?

- **Cost Control:** Fixed limits prevent runaway API costs
- **Demo Optimization:** 5-second videos are sufficient for Instagram Reels
- **Instagram Format:** 3 segments create a 15-second reel (Instagram optimal length)
- **Quality over Quantity:** Focus on high-quality, targeted content

---

## Cost Estimates

### Video Generation (Veo 2.0)

| Operation | Duration | Cost (Est.) | Notes |
|-----------|----------|-------------|-------|
| Initial Generation | 5 seconds | ~$0.20 | First video segment |
| Extension | 5 seconds | ~$0.10 | Segments 2 & 3 |
| **Per Post (3 segments)** | **15 seconds** | **~$0.40-0.50** | Total per post |

**Full Calendar (7 days, 21 videos):** ~$2.80-3.50

### Image Generation (Imagen 3)

| Operation | Format | Cost (Est.) | Notes |
|-----------|--------|-------------|-------|
| Single Image | 1:1 (1024x1024) | ~$0.03 | Per image |
| **Per Post (3 images)** | **3 images** | **~$0.09** | Total per post |

**Full Calendar (7 days, 21 images):** ~$$0.63

### Combined Cost

| Scenario | Videos | Images | Total Cost |
|----------|--------|--------|------------|
| **Full Calendar (Current)** | Enabled | Enabled | **~$3.40-4.15** |
| Videos Only | Enabled | Disabled | ~$2.80-3.50 |
| Images Only | Disabled | Enabled | ~$0.63 |
| **Development Mode** | Disabled | Disabled | **$0.00** |

### Cost Savings: 8s → 5s Video Reduction

| Configuration | Duration per Video | Cost per Video | Cost per Calendar (21 videos) | Savings |
|---------------|-------------------|----------------|-------------------------------|---------|
| **Old (8 seconds)** | 8s | ~$0.32 | ~$6.72 | - |
| **New (5 seconds)** | 5s | ~$0.20 | ~$4.20 | **~$2.52 (37.5%)** |

**Key Insight:** Reducing video duration from 8s to 5s saves approximately **37.5%** on video generation costs while maintaining content quality for Instagram Reels.

---

## Development vs Production

### Development Setup

**Recommended Configuration:**
```bash
# .env.development (default)
ENABLE_VIDEOS=false
ENABLE_IMAGES=false
```

**Benefits:**
- Instant testing (no API wait times)
- Zero cost
- Rapid iteration
- Safe for CI/CD

**Use Case:**
- Local development
- Unit tests
- Integration tests
- Feature development

### Demo Setup

**Configuration:**
```bash
# .env
ENABLE_VIDEOS=true
ENABLE_IMAGES=true
GCP_PROJECT_ID=demo-project-123
GCP_REGION=us-central1
STORAGE_BUCKET=demo-media-bucket
GOOGLE_MAPS_API_KEY=AIza...
```

**Costs:**
- Full 7-day calendar: ~$3.40-4.15
- Single post test: ~$0.50-0.60

**Use Case:**
- Product demos
- Client presentations
- Testing end-to-end flow
- Content quality validation

### Production Setup

**Configuration:**
```bash
# .env (not committed to git)
ENABLE_VIDEOS=true
ENABLE_IMAGES=true
GCP_PROJECT_ID=prod-project-456
GCP_REGION=us-central1
STORAGE_BUCKET=prod-media-bucket

# Use Secret Manager for API keys (recommended)
# GOOGLE_MAPS_API_KEY loaded from Secret Manager
```

**Additional Requirements:**
- Service account with minimal required permissions
- Secret Manager for API keys
- Cloud Storage bucket with proper IAM roles
- Monitoring and cost alerts
- Rate limiting and quotas

---

## Authentication Setup

### Option 1: Application Default Credentials (Development)

**Best for:** Local development

```bash
# Authenticate with your user account
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Option 2: Service Account Key (Production)

**Best for:** Production deployments

```bash
# Create service account
gcloud iam service-accounts create obi-run-kenobi \
  --display-name="OBI-RUN-KENOBI Backend"

# Grant required roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:obi-run-kenobi@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=obi-run-kenobi@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Option 3: Cloud Run (Automatic)

**Best for:** GCP-hosted deployments

When running on Cloud Run, Cloud Functions, or GKE, credentials are automatically provided via the service's service account. No additional authentication required.

**Required IAM Roles:**
- `roles/aiplatform.user` (Vertex AI access)
- `roles/storage.objectAdmin` (Cloud Storage)
- `roles/secretmanager.secretAccessor` (Secret Manager)

---

## Configuration Validation

### Verify Your Setup

```python
# Test configuration loading
from config import settings

print(f"Project ID: {settings.project_id}")
print(f"Region: {settings.region}")
print(f"Videos Enabled: {settings.enable_video_generation}")
print(f"Images Enabled: {settings.enable_image_generation}")
print(f"Max Videos per Post: {settings.max_videos_per_post}")
print(f"Max Images per Post: {settings.max_images_per_post}")
print(f"Video Duration: {settings.video_duration_seconds}s")
```

### Expected Output (Development):
```
Project ID: your-project-id
Region: us-central1
Videos Enabled: False
Images Enabled: False
Max Videos per Post: 3
Max Images per Post: 3
Video Duration: 5s
```

---

## Troubleshooting

### Issue: Videos/Images not generating

**Check:**
1. `ENABLE_VIDEOS` or `ENABLE_IMAGES` is set to `true`
2. GCP credentials are configured correctly
3. Project ID has Vertex AI API enabled
4. Service account has required permissions

### Issue: Unexpected costs

**Check:**
1. `.env` file has correct flags (not accidentally using demo config)
2. Monitor Cloud Console for API usage
3. Set up billing alerts
4. Review logs for unexpected regenerations

### Issue: Configuration not loading

**Check:**
1. `.env` file exists in `/backend` directory
2. Environment variables are set correctly
3. No syntax errors in `.env` file
4. Using correct variable names (e.g., `ENABLE_VIDEOS` not `VIDEOS_ENABLED`)

---

## Best Practices

1. **Always use `.env.development` for local development** - Prevents accidental costs
2. **Test with placeholders first** - Validate logic before generating real media
3. **Enable media generation only when needed** - For demos, final content
4. **Monitor costs regularly** - Set up billing alerts in GCP Console
5. **Use Secret Manager in production** - Don't commit API keys to git
6. **Version control configuration changes** - Document any limit adjustments

---

## Related Files

- `/backend/.env.example` - Configuration template
- `/backend/.env.development` - Development defaults
- `/backend/config.py` - Configuration loader
- `/backend/agents/content_strategist.py` - Prompt generation with limits
- `/backend/agents/creative_producer.py` - Media generation with cost controls

---

**Last Updated:** November 10, 2024
**Version:** 1.0.0
**Configuration Format:** Environment Variables + Python Settings
