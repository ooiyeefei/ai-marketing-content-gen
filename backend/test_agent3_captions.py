import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.creative_producer import CreativeProducerAgent


async def test_captions():
    """Test caption generation for Creative Producer Agent"""
    agent = CreativeProducerAgent()

    # Mock post plan from Content Strategist
    post_plan = {
        'day': 1,
        'platform': 'instagram',
        'concept': 'Signature laksa preparation',
        'caption_theme': 'heritage recipe',
        'cta': 'Visit us today',
        'video_prompts': [
            'Chef preparing laksa broth',
            'Adding fresh noodles and garnish',
            'Steaming bowl ready to serve'
        ]
    }

    business_profile = {
        'business_name': 'The Hawker',
        'brand_voice': 'casual'
    }

    print("=" * 60)
    print("Testing Creative Producer Agent - Caption Generation")
    print("=" * 60)
    print(f"\nBusiness: {business_profile['business_name']}")
    print(f"Brand Voice: {business_profile['brand_voice']}")
    print(f"\nPost Concept: {post_plan['concept']}")
    print(f"Theme: {post_plan['caption_theme']}")
    print(f"Platform: {post_plan['platform']}")
    print("\n" + "-" * 60)
    print("Generating caption...")
    print("-" * 60)

    caption = await agent._generate_caption(post_plan, business_profile)

    print("\nGenerated Caption:")
    print("=" * 60)
    print(caption)
    print("=" * 60)

    hashtags = agent._extract_hashtags(caption)
    print(f"\nExtracted Hashtags ({len(hashtags)}):")
    print(", ".join(hashtags))

    print("\n" + "=" * 60)
    print("Caption test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_captions())
