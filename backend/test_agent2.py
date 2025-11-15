import asyncio
from agents.content_strategist import ContentStrategistAgent

async def test_agent():
    agent = ContentStrategistAgent()

    # Mock business profile
    business_profile = {
        'business_name': 'The Hawker',
        'brand_voice': 'casual',
        'content_themes': [
            'heritage recipes',
            'fresh ingredients',
            'customer favorites'
        ],
        'from_maps': {
            'review_themes': ['authentic taste', 'generous portions']
        },
        'local_trends': {
            'trending_topics': ['food delivery', 'hawker food']
        }
    }

    calendar = await agent.create_calendar(business_profile)

    print(f"\n{'='*60}")
    print(f"Generated {len(calendar)} posts:")
    print(f"{'='*60}\n")

    for post in calendar:
        print(f"Day {post['day']}: {post['concept']}")
        print(f"  Platform: {post['platform']}")
        print(f"  Caption Theme: {post.get('caption_theme', 'N/A')}")
        print(f"  CTA: {post.get('cta', 'N/A')}")
        print(f"  Video Prompts ({len(post['video_prompts'])} segments):")
        for i, prompt in enumerate(post['video_prompts'], 1):
            print(f"    Segment {i}: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print()

    print(f"{'='*60}")
    print(f"Quality Gate Check:")
    print(f"  ✓ Total posts: {len(calendar)}")
    print(f"  ✓ All posts have video_prompts: {all('video_prompts' in p and len(p['video_prompts']) > 0 for p in calendar)}")
    print(f"  ✓ Video prompts range (1-3): {all(1 <= len(p['video_prompts']) <= 3 for p in calendar)}")
    print(f"  ✓ All posts have required fields: {all(all(k in p for k in ['day', 'platform', 'concept', 'video_prompts', 'caption_theme', 'cta']) for p in calendar)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(test_agent())
