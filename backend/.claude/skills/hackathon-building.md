---
name: hackathon-building
description: Use when building hackathon projects - comprehensive workflow from initial idea to submission, covering requirement gathering, technical implementation, winning strategies, submission materials, and project cleanup
---

# Hackathon Building - End-to-End Project Workflow

## When to Use This Skill

Use this skill when:
- Starting a new hackathon project from scratch
- User mentions hackathon deadlines, prizes, or submission requirements
- Building a proof-of-concept demo within time constraints
- Need to maximize winning chances with strategic feature selection
- Creating submission materials (writeup, demo video, architecture diagrams)

## Phase 1: Initial Requirement Gathering & Hackathon Analysis

### Step 1.1: Understand the Hackathon Context

Ask the user:
1. **Hackathon Details**
   - What's the hackathon name and theme?
   - What are the judging criteria? (innovation, technical complexity, business impact, design, etc.)
   - What's the timeline? (hours/days remaining)
   - What are the prizes or categories?
   - Are there specific technologies or APIs that must be used?

2. **Team & Resources**
   - Who's on the team and what are their skills?
   - What tech stack are you most comfortable with?
   - Do you have access to premium APIs or cloud credits?

3. **Initial Idea**
   - What problem are you trying to solve?
   - Who is the target user?
   - What's your elevator pitch?

### Step 1.2: Analyze Winning Potential

Assess the idea against these criteria:
- **Impact**: Does it solve a real problem people care about?
- **Innovation**: Is it novel or a unique combination of technologies?
- **Feasibility**: Can it be built within the time constraints?
- **Demo-ability**: Will it look impressive in a 3-minute demo?
- **Completeness**: Can you ship a working end-to-end experience?

**Red Flags to Avoid**:
- Ideas requiring complex data pipelines that take days to build
- Features depending on unavailable APIs or data
- Solutions looking for problems
- Overly broad scope that can't be completed

**Green Flags to Pursue**:
- Clear value proposition within 30 seconds
- Leverages cutting-edge AI/ML capabilities (Gemini, Veo, multimodal)
- End-to-end user experience (not just backend logic)
- Visual/interactive elements that demo well
- Solves judge's own pain points

## Phase 2: Strategic Feature Selection & User Preferences

### Step 2.1: MVP Feature Definition

With the user, identify:
1. **Core Features** (must-have for demo)
   - What's the absolute minimum to demonstrate value?
   - What will judges interact with?

2. **Nice-to-Have Features** (if time permits)
   - What would make it more polished?
   - What edge cases can we handle?

3. **Cut Features** (out of scope)
   - What can wait until after the hackathon?
   - What's too complex for the timeline?

### Step 2.2: Gather Technical Preferences

Throughout development, continuously ask:
- **UI/UX Preferences**: Dark mode or light mode? Color scheme?
- **Data Sources**: What real business/user data can we use for the demo?
- **Generation Settings**: Do we enable expensive API calls (video/image generation) or use placeholders during testing?
- **Deployment**: Where will this be hosted for judges to access?

**Example from our journey**:
- User wanted light mode instead of dark mode
- User wanted real business photos scraped from Facebook/Instagram for authentic image generation
- User wanted actual video generation enabled (not placeholders)
- User wanted enhanced loading UI with progress indicators

## Phase 3: Technical Implementation Patterns

### Step 3.1: Agent-Based Architecture (for AI projects)

For multi-step AI workflows, use an agent pattern:

**Example: 3-Agent Social Media Content Generator**
1. **Agent 1: Business Analyst** - Gathers context (website, Google Maps, trends, photos)
2. **Agent 2: Content Strategist** - Creates 7-day content calendar with themes
3. **Agent 3: Creative Producer** - Generates captions, images, and videos

**Benefits**:
- Clear separation of concerns
- Easy to parallelize data gathering
- Each agent can use different models/tools
- Modular for judges to understand

### Step 3.2: Multimodal AI Integration

Leverage multiple AI modalities for richer experiences:
- **Text**: Gemini for analysis, captions, themes
- **Images**: Gemini native image generation with style references
- **Video**: Veo 2.0 for short-form video generation
- **Grounding**: Google Search Grounding for web scraping

**Critical Implementation Details**:
```python
# Image generation with style references (multimodal prompts)
contents = [style_prompt]
for ref_img in reference_images:
    contents.append({
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": ref_img  # base64 encoded
        }
    })

response = genai_client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents=contents,
    config=genai_types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        mediaResolution="MEDIA_RESOLUTION_MEDIUM"
    )
)
```

```python
# Video generation with Veo 2.0 (following official docs)
config = genai_types.GenerateVideosConfig(
    number_of_videos=1,
    duration_seconds=5,
    aspect_ratio="9:16",
    output_gcs_uri=output_gcs_uri,
    enhance_prompt=True
)

operation = genai_client.models.generate_videos(
    model='veo-2.0-generate-001',
    prompt=full_prompt,
    config=config
)

# Poll until complete
while not operation.done and polls < max_polls:
    await asyncio.sleep(15)
    operation = genai_client.operations.get(operation=operation)

# Extract GCS URI
video_gcs_uri = operation.result.generated_videos[0].video.uri
```

### Step 3.3: User Experience Polish

**Frontend Best Practices**:
- Show loading states with progress indicators (not just spinners)
- Use real-time status updates ("Analyzing website...", "Generating videos...")
- Display results progressively (show images while videos generate)
- Handle errors gracefully with retry options
- Mobile-responsive design

**Example: Enhanced Loading Screen**
```typescript
const steps = [
  { icon: '🔍', label: 'Analyzing your website', color: '#4285F4' },
  { icon: '📍', label: 'Discovering your business', color: '#34A853' },
  { icon: '📊', label: 'Understanding local trends', color: '#FBBC04' },
  { icon: '🤖', label: 'Agents creating content', color: '#EA4335' },
  { icon: '🎬', label: 'Generating videos', color: '#9C27B0' },
]

// Show circular progress, step-by-step animations, color-coded indicators
```

### Step 3.4: Configuration & Feature Flags

Use environment variables for easy demo control:
```python
# config.py
enable_video_generation: bool = False  # Toggle for testing
enable_image_generation: bool = True
video_duration_seconds: int = 5
max_images_per_post: int = 3
storage_bucket: str = "your-demo-bucket"
```

This allows you to:
- Test quickly without expensive API calls
- Enable full features for final demo
- Adjust based on remaining cloud credits

## Phase 4: Submission Materials

### Step 4.1: Project Writeup Template

**Title**: [Catchy project name]

**Tagline**: [One sentence describing the value]

**Problem**:
- What problem does this solve?
- Who experiences this problem?
- Why is it important?

**Solution**:
- What does your project do?
- How does it work (high-level)?
- What makes it unique?

**Tech Stack**:
- Frontend: [e.g., Next.js 14, React, Material-UI, Tailwind CSS]
- Backend: [e.g., FastAPI, Python 3.12]
- AI/ML: [e.g., Gemini 2.0-flash-001, Veo 2.0, Gemini 2.5-flash-image]
- Cloud: [e.g., Google Cloud Storage, Vertex AI]
- APIs: [e.g., Google Maps, Google Search Grounding]

**Architecture**:
[Include architecture diagram - see section 4.3]

**Key Features**:
1. [Feature 1 with screenshot]
2. [Feature 2 with screenshot]
3. [Feature 3 with screenshot]

**Demo**: [Link to live demo]

**Challenges & Learnings**:
- What technical challenges did you overcome?
- What did you learn about the technologies used?

**Future Enhancements**:
- What would you build next?
- How would you scale this?

**Example from our project**:
> **Veo-licious Gems**: AI-powered social media agency that generates 7 days of branded content (captions, images, videos) in minutes. Simply provide your business URL and address - our 3-agent system analyzes your brand, scrapes real photos for style-matching, and produces authentic short-form videos using Veo 2.0.

### Step 4.2: Demo Video Script Template

**Duration**: 2-3 minutes max

**Structure**:
1. **Hook (0:00-0:15)**: Show the problem
   - "Small businesses spend hours creating social media content every week..."

2. **Solution (0:15-0:30)**: Introduce your project
   - "Meet [Project Name] - an AI agent that generates a week's worth of branded content in minutes"

3. **Demo (0:30-2:00)**: Show it working
   - Input: Show entering business URL and address
   - Processing: Show enhanced loading UI with progress
   - Output: Show generated content (captions, images, videos)
   - Interaction: Show user selecting different images, viewing videos

4. **Tech Highlight (2:00-2:30)**: Show what makes it impressive
   - "Behind the scenes, we use 3 specialized AI agents..."
   - "Photos are scraped from real business pages for authentic style-matching..."
   - "Veo 2.0 generates short-form videos with seamless multi-segment extension..."

5. **Call to Action (2:30-3:00)**: Wrap up
   - "Try it yourself at [demo-url]"
   - "Built in 48 hours for [Hackathon Name]"

**Recording Tips**:
- Use Loom or OBS for screen recording
- Show real data (not dummy/test data)
- Keep cursor movements smooth
- Zoom in on important UI elements
- Add background music (low volume)
- Include voiceover explaining what's happening

### Step 4.3: Architecture Diagram

Create a visual system diagram showing:

**Components to Include**:
1. **User Interface** (Frontend)
   - Technology used (Next.js, React)
   - Key pages/components

2. **API Layer** (Backend)
   - Framework (FastAPI)
   - Key endpoints

3. **Agent System** (if applicable)
   - Agent 1: [Name and purpose]
   - Agent 2: [Name and purpose]
   - Agent 3: [Name and purpose]

4. **External Services**
   - AI Models (Gemini, Veo, Imagen)
   - APIs (Google Maps, Search)
   - Storage (GCS, database)

5. **Data Flow**
   - Show arrows indicating data movement
   - Label with data types (text, images, videos)

**Example Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Input Form   │  │ Loading UI   │  │ Results View │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────┐
│                     Backend API (FastAPI)                   │
│                    /api/generate (POST)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Agent 1    │    │   Agent 2    │    │   Agent 3    │
│   Business   │───▶│   Content    │───▶│   Creative   │
│   Analyst    │    │   Strategist │    │   Producer   │
└──────┬───────┘    └──────────────┘    └──────┬───────┘
       │                                        │
       ▼                                        ▼
┌─────────────────────────────┐    ┌─────────────────────────┐
│   External Data Sources     │    │    AI Generation        │
│  • Google Search Grounding  │    │  • Gemini (captions)    │
│  • Google Maps API          │    │  • Veo 2.0 (videos)     │
│  • Photo Scraper            │    │  • Gemini Image (imgs)  │
└─────────────────────────────┘    └──────────┬──────────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │  Google Cloud       │
                                   │  Storage (GCS)      │
                                   │  • Videos           │
                                   │  • Images           │
                                   └─────────────────────┘
```

**Tools to Create Diagrams**:
- Excalidraw (free, easy, hand-drawn style)
- draw.io / diagrams.net (professional)
- Mermaid (code-based diagrams in markdown)
- ASCII art (for quick text-based diagrams)

## Phase 5: Pre-Submission Cleanup & Analysis

### Step 5.1: Code Quality Scan

Run these checks before submitting:

**1. Remove Debug Code**
```bash
# Search for console.logs, print statements
grep -r "console.log" frontend/
grep -r "print(" backend/
```

**2. Remove Commented Code**
```bash
# Find large blocks of commented code
grep -r "^#.*" backend/ | wc -l
```

**3. Check for Secrets**
```bash
# Make sure no API keys are committed
grep -r "API_KEY" . --exclude-dir={node_modules,venv,.git}
grep -r "SECRET" . --exclude-dir={node_modules,venv,.git}
```

**4. Verify Environment Variables**
```bash
# Check .env.example exists
ls -la .env.example

# Verify all required vars are documented
cat .env.example
```

### Step 5.2: Documentation Cleanup

**README.md Must Include**:
- Project title and tagline
- Problem and solution
- Quick start instructions (how to run locally)
- Demo link
- Tech stack
- Architecture diagram (or link to it)
- Team members
- License

**Example README structure**:
```markdown
# Veo-licious Gems - AI Social Media Agency

> Generate 7 days of branded social media content in minutes

## Problem
Small businesses struggle to create consistent, branded social media content...

## Solution
Veo-licious Gems uses 3 specialized AI agents to...

## Demo
🔗 [Live Demo](https://demo-url.com)

## Quick Start
1. Clone the repo
2. Set up environment variables (see .env.example)
3. Run backend: `cd backend && uvicorn main:app --reload`
4. Run frontend: `cd frontend && npm run dev`

## Tech Stack
- **Frontend**: Next.js 14, React, Material-UI
- **Backend**: FastAPI, Python 3.12
- **AI**: Gemini 2.0, Veo 2.0, Gemini 2.5-flash-image
- **Cloud**: Google Cloud Storage, Vertex AI

## Architecture
[Insert diagram]

## Team
- [Name] - Frontend
- [Name] - Backend
- [Name] - AI/ML

## License
MIT
```

### Step 5.3: Performance & Error Handling

**Before Demo Day**:
1. **Test Error Cases**
   - What happens if user enters invalid URL?
   - What if photo scraping fails?
   - What if video generation times out?
   - What if API quota is exceeded?

2. **Add Loading States**
   - All async operations should show progress
   - Use realistic loading messages
   - Show estimated time remaining

3. **Add Fallbacks**
   - If video generation fails → show placeholder or retry
   - If photos can't be scraped → generate without style references
   - If API fails → show clear error message with next steps

4. **Test on Demo Hardware**
   - Will you demo on laptop, tablet, or phone?
   - Test on the actual device judges will see
   - Ensure responsive design works

### Step 5.4: Final Checklist

**Before Submission**:
- [ ] README.md is complete and clear
- [ ] Demo video is uploaded (YouTube/Vimeo)
- [ ] Live demo is deployed and accessible
- [ ] All secrets are in .env (not committed)
- [ ] Code is pushed to GitHub with clear commit messages
- [ ] Architecture diagram is included
- [ ] Project writeup is submitted on hackathon platform
- [ ] Team members are listed
- [ ] Judges can run the project locally (test with fresh clone)

**Before Demo Presentation**:
- [ ] Demo video is queued and ready
- [ ] Live demo is loaded in browser
- [ ] Backup demo video in case internet fails
- [ ] Test data is prepared (use real business examples)
- [ ] Pitch is practiced and under time limit
- [ ] Team knows who presents each section
- [ ] Questions are anticipated and answers prepared

## Phase 6: Demo Day Execution

### Step 6.1: Presentation Structure (3 minutes)

**0:00-0:30 - Problem Statement**
- Start with relatable pain point
- Use real statistics if possible
- Make judges nod in agreement

**0:30-1:00 - Solution Overview**
- Show your project name and tagline
- Explain high-level approach
- Highlight what's innovative

**1:00-2:30 - Live Demo**
- Use real business data (not fake/test data)
- Show input → processing → output
- Highlight AI-generated results
- Interact with the UI (don't just play video)

**2:30-3:00 - Technical Highlights & Wrap-up**
- Mention key technologies (Veo, Gemini, etc.)
- Show architecture diagram briefly
- End with impact statement
- "Try it at [demo-url]"

### Step 6.2: Handling Judge Questions

**Common Questions to Prepare**:
1. "How did you build this in 48 hours?"
   - Focus on strategic API choices and reusable patterns

2. "What was the hardest technical challenge?"
   - Share a specific bug you solved (shows depth)

3. "How would you scale this?"
   - Talk about caching, batch processing, user accounts

4. "What's your business model?"
   - Subscription for small businesses, API for agencies

5. "What would you add next?"
   - 2-3 concrete features, show you're thinking ahead

### Step 6.3: Post-Demo Follow-Up

**After presenting**:
1. Share demo link in hackathon chat/Discord
2. Tweet about your project (tag hackathon, sponsors)
3. Stay available for judges to test your demo
4. Network with other participants and sponsors
5. Get feedback and note improvements

**Win or lose**:
- Get judge feedback (what worked, what didn't)
- Ship improvements after the hackathon
- Write a blog post about your journey
- Add to your portfolio
- Open source if possible

## Key Lessons from Our Journey

### What Worked Well

1. **Multi-Agent Architecture**: Clear separation made development parallelizable and system understandable

2. **Real Business Data**: Scraping actual photos from Facebook/Instagram made generated content look authentic, not generic AI

3. **Multimodal AI**: Combining text, image, and video generation created a richer, more impressive demo

4. **Enhanced UX**: Progress indicators and loading animations made the wait time feel shorter and more engaging

5. **Feature Flags**: Environment variables for enabling/disabling expensive APIs allowed fast iteration during testing

6. **Following Official Docs**: Using Veo 2.0 and Gemini APIs exactly as documented (not guessing) prevented errors

### What to Avoid

1. **Stubbed Implementations**: Don't submit placeholders - judges will test your demo

2. **Dark Mode by Default**: Light mode is more accessible and professional for demos

3. **Generic AI Outputs**: Always use reference images/style matching for brand-authentic generation

4. **Silent Loading States**: Show what's happening with progress indicators and status messages

5. **Hardcoded Values**: Use environment variables for all API keys, buckets, and configuration

6. **Skipping Error Handling**: Gracefully handle API failures, timeouts, and invalid inputs

### Technical Patterns That Saved Time

**1. Async Concurrent Data Fetching**:
```python
# Agent 1 fetches multiple data sources in parallel
website_data = google_services.analyze_website()  # Run concurrently
maps_data = google_services.get_place_details()
photos = photo_scraper.scrape_photos()
```

**2. Multimodal Prompts with Style References**:
```python
# Pass business photos as style references
contents = [prompt] + [{"inline_data": {"data": img}} for img in reference_images]
response = genai_client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents=contents
)
```

**3. Video Extension Pattern**:
```python
# Each segment extends the previous for seamless video
previous_gcs_uri = None
for prompt in video_prompts:
    result = generate_video(prompt, previous_video=previous_gcs_uri)
    previous_gcs_uri = result['gcs_uri']
```

**4. Progressive Result Display**:
```typescript
// Show results as they become available
const [posts, setPosts] = useState([])
const [loading, setLoading] = useState(true)

// Poll backend for partial results
const interval = setInterval(async () => {
    const status = await fetchJobStatus(jobId)
    if (status.partial_results) {
        setPosts(status.partial_results)  // Show what's ready
    }
    if (status.complete) {
        clearInterval(interval)
        setLoading(false)
    }
}, 2000)
```

## Summary: Hackathon Success Formula

1. **Choose a demo-able problem** with visual outputs
2. **Leverage cutting-edge AI** (multimodal, video generation)
3. **Use real data** for authenticity
4. **Polish the UX** with loading states and animations
5. **Document everything** (README, architecture, demo video)
6. **Test the full flow** on real data before demo day
7. **Practice your pitch** until it's under time limit
8. **Have fun** and learn new technologies!

## When to Skip This Skill

Skip this comprehensive workflow if:
- You're building a production app (not a hackathon demo)
- You have unlimited time (not 24-48 hours)
- The project doesn't have a submission deadline

For non-hackathon projects, use more thorough planning, testing, and development practices.
