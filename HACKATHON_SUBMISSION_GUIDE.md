# GDG Stanford Hackathon Submission Guide

## 📝 Submission Requirements

### ✅ 1. Live Demo URLs (COMPLETED)
- **Frontend**: https://veo-licious-gems-frontend-t5666p4y5q-uc.a.run.app
- **Backend**: https://veo-licious-gems-backend-t5666p4y5q-uc.a.run.app
- **Status**: ✅ Deployed and working with images + videos

---

## 🔗 2. Google AI Studio Code Sharing (TO DO)

### Quick Method (5 minutes):

1. **Go to**: https://aistudio.google.com/
2. **Click**: "New Prompt"
3. **Create 3 prompts showcasing your agents**:

#### Prompt 1: Business Analyst Agent
```
Model: Gemini 2.0 Flash

System Instructions:
You are a Business Analyst Agent analyzing small businesses for social media marketing.
Analyze the provided business information and return insights about:
- Business name, industry, and brand personality
- Key products/services
- Unique selling points
- Customer reviews sentiment
- Local trends and opportunities

User Input:
[Business website URL, address, reviews]

Expected Output:
JSON with business_name, industry, brand_voice, key_products, review_themes, local_trends
```

#### Prompt 2: Content Strategist Agent
```
Model: Gemini 2.5 Flash

System Instructions:
You are a Content Strategist creating 7-day social media calendars.
Generate a content calendar with:
- 7 daily posts (Instagram/TikTok focus)
- Engaging captions with hashtags
- Video concepts (1-3 segments each, 8-24 seconds total)
- Mix of product features, customer testimonials, and trending topics

User Input:
{business_profile from Agent 1}

Expected Output:
JSON array with 7 posts, each containing platform, caption_prompt, video_concept, hashtags
```

#### Prompt 3: Creative Producer Agent
```
Models: Gemini 2.5 Flash Image + Veo 2.0

System Instructions:
You generate final social media content:
- Captions: Use Gemini 2.0 Flash
- Images (3 per post): Use Gemini 2.5 Flash Image with style-matching
- Videos: Use Veo 2.0 for 5-8 second segments

Style-Matching Process:
1. Download business photos from website/social media
2. Use them as reference images in image generation
3. Generate new images that match the brand's visual style

User Input:
{content_calendar from Agent 2, business_photos}

Expected Output:
Final posts with captions, image_urls, video_urls
```

4. **Share each prompt**: Click "Get Link" → Copy shareable link
5. **Add to SUBMISSION.md**: Update line 158 with your AI Studio project link

---

## 📹 3. Demo Video (TO DO)

### Script (3 minutes):

**[0:00-0:30] The Problem**
- "Small businesses struggle with social media"
- "Agencies cost $2-5K/month, DIY takes 10 hours/week"
- "Generic AI tools produce obvious 'AI slop'"

**[0:30-1:30] The Demo**
- Open: https://veo-licious-gems-frontend-t5666p4y5q-uc.a.run.app
- Input: Magpie Burgertory URL + address
- Show: "GENERATING CONTENT..." loading
- Result: 2 posts with 3 images + 1 video each
- Highlight: "Notice how images match the brand's rustic burger aesthetic"

**[1:30-2:15] The Technology**
- "3-Agent System powered by Google Gemini"
- "Agent 1: Analyzes business with Gemini 2.0"
- "Agent 2: Creates strategy with Gemini 2.5"
- "Agent 3: Generates content with Gemini Image + Veo 2.0"
- "All deployed on Google Cloud Run"

**[2:15-3:00] The Opportunity**
- "$59B market - 33M US small businesses"
- "$99-299/month self-serve pricing"
- "Try it now at [your-url]"

### Recording Tools:
- **Loom**: https://www.loom.com/ (easiest, auto-uploads)
- **OBS Studio**: Free, more control
- **Zoom**: Record yourself + screen share

### Upload:
1. Upload to YouTube (Unlisted or Public)
2. Add link to SUBMISSION.md line 159

---

## 📄 4. Complete SUBMISSION.md (TO DO)

Update these lines in SUBMISSION.md:

**Line 150**: Add your relevant experience
```markdown
✅ **Founder-Market Fit**: [Your name] - [Brief relevant experience, e.g., "Built 2 SaaS products, ex-Meta engineer"]
```

**Line 158**: Add Google AI Studio link
```markdown
- **Code Repository**: https://aistudio.google.com/app/prompts/[your-prompt-id]
```

**Line 159**: Add demo video link
```markdown
- **3-Minute Demo Video**: https://www.youtube.com/watch?v=[your-video-id]
```

**Lines 165-168**: Add your contact info
```markdown
**Email**: your-email@gmail.com
**LinkedIn**: linkedin.com/in/yourprofile
**Twitter**: @yourhandle
```

---

## 🚀 5. Submit to Hackathon

### Submission Form:
Go to the hackathon submission page and provide:
1. **Project Name**: Veo-licious Gems
2. **One-Pager**: Copy entire SUBMISSION.md content OR upload the file
3. **Live Demo URL**: https://veo-licious-gems-frontend-t5666p4y5q-uc.a.run.app
4. **Code Repository**: Your Google AI Studio link
5. **Demo Video**: Your YouTube link
6. **Team Members**: [Your name(s)]

---

## ⏰ Time Estimate

- Google AI Studio prompts: **5 minutes**
- Record demo video: **15 minutes**
- Upload video: **5 minutes**
- Update SUBMISSION.md: **5 minutes**
- Submit form: **5 minutes**

**Total: 35 minutes** ⏱️

---

## 💡 Quick Wins for Judging

Make sure to emphasize:
1. **Technical Innovation**: "First to combine Gemini + Veo + style-matching"
2. **Real Photos**: "Uses actual business photos, not generic AI stock"
3. **Working Demo**: "Fully deployed on Cloud Run, test it now"
4. **Market Size**: "$59B TAM, $99/month SMB pricing"
5. **All Google**: "100% Google Gemini stack - AI Studio, Cloud Run, Veo 2.0"

---

## 🎯 Submission Deadline

**2:30 PM** - Don't forget to submit before the deadline! 🚨

Good luck! 🚀
