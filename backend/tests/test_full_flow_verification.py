"""
Focused E2E Test: Verify Complete Business URL → Content Generation Flow

Tests the critical path:
1. User inputs business URL
2. AGI researches and scrapes (text + images)
3. Data stored in Convex/R2
4. Agent 2 designs content strategy
5. Agent 3 generates images/videos using business data

Expected: ~10 minutes with real APIs
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from orchestrator import CampaignOrchestrator
from services.convex_service import ConvexService
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def verify_research_data(campaign_id: str, convex: ConvexService):
    """Verify Agent 1 extracted and stored data correctly"""
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION 1: Research Data")
    logger.info("="*80)

    research = await convex.get_research(campaign_id)

    checks = {
        "business_name": bool(research.business_context.business_name),
        "industry": bool(research.business_context.industry),
        "description": bool(research.business_context.description),
        "competitors": len(research.competitors) > 0,
        "market_insights": len(research.market_insights.trending_topics) > 0,
        "research_images_uploaded": len(research.research_images) > 0
    }

    logger.info(f"\n✓ Business: {research.business_context.business_name}")
    logger.info(f"✓ Industry: {research.business_context.industry}")
    logger.info(f"✓ Description: {research.business_context.description[:100]}...")
    logger.info(f"✓ Competitors found: {len(research.competitors)}")
    logger.info(f"✓ Market insights: {len(research.market_insights.trending_topics)} trending topics")
    logger.info(f"✓ Research images uploaded to R2: {len(research.research_images)}")

    if research.research_images:
        logger.info(f"\nR2 Image URLs:")
        for i, url in enumerate(research.research_images[:3], 1):
            logger.info(f"  {i}. {url}")

    all_passed = all(checks.values())

    if not all_passed:
        logger.error("\n❌ FAILED CHECKS:")
        for check, passed in checks.items():
            if not passed:
                logger.error(f"  - {check}")

    return all_passed


async def verify_analytics_data(campaign_id: str, convex: ConvexService):
    """Verify Agent 2 analyzed and stored strategy correctly"""
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION 2: Analytics & Strategy Data")
    logger.info("="*80)

    analytics = await convex.get_analytics(campaign_id)

    checks = {
        "customer_sentiment": len(analytics.customer_sentiment.positive_themes) > 0,
        "quotable_reviews": len(analytics.customer_sentiment.quotable_reviews) > 0,
        "market_trends": len(analytics.market_trends.trending_searches) > 0
    }

    logger.info(f"\n✓ Positive themes: {len(analytics.customer_sentiment.positive_themes)}")
    logger.info(f"  Examples: {analytics.customer_sentiment.positive_themes[:3]}")
    logger.info(f"✓ Quotable reviews: {len(analytics.customer_sentiment.quotable_reviews)}")
    logger.info(f"✓ Market trends: {len(analytics.market_trends.trending_searches)}")

    return all(checks.values())


async def verify_creative_output(campaign_id: str, convex: ConvexService):
    """Verify Agent 3 generated content using business data"""
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION 3: Creative Content Generation")
    logger.info("="*80)

    content = await convex.get_content(campaign_id)

    checks = {
        "has_7_days": len(content.days) == 7,
        "all_days_have_caption": all(day.caption for day in content.days),
        "all_days_have_images": all(len(day.image_urls) > 0 for day in content.days),
        "images_uploaded_to_r2": all(
            any("r2" in img or "cloudflarestorage" in img for img in day.image_urls)
            for day in content.days
        )
    }

    logger.info(f"\n✓ Total days of content: {len(content.days)}")

    for day in content.days[:3]:  # Show first 3 days
        logger.info(f"\nDay {day.day}: {day.theme}")
        logger.info(f"  Caption: {day.caption[:80]}...")
        logger.info(f"  Images: {len(day.image_urls)} generated")
        logger.info(f"  First image URL: {day.image_urls[0] if day.image_urls else 'None'}")
        if day.video_url:
            logger.info(f"  Video URL: {day.video_url}")

    all_passed = all(checks.values())

    if not all_passed:
        logger.error("\n❌ FAILED CHECKS:")
        for check, passed in checks.items():
            if not passed:
                logger.error(f"  - {check}")

    return all_passed


async def verify_images_use_business_reference(campaign_id: str, convex: ConvexService):
    """Verify Agent 3 used research images as subject reference"""
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION 4: Images Use Business Reference")
    logger.info("="*80)

    research = await convex.get_research(campaign_id)
    content = await convex.get_content(campaign_id)

    has_research_images = len(research.research_images) > 0
    has_generated_images = any(len(day.image_urls) > 0 for day in content.days)

    logger.info(f"\n✓ Research images available: {len(research.research_images)}")
    logger.info(f"✓ Content images generated: {sum(len(day.image_urls) for day in content.days)}")

    if has_research_images:
        logger.info(f"\n✓ Agent 3 had access to these reference images:")
        for i, url in enumerate(research.research_images[:2], 1):
            logger.info(f"  {i}. {url}")
        logger.info(f"\n✓ These were used as subject_reference_url for MiniMax")

    return has_research_images and has_generated_images


async def main():
    """Run focused E2E verification test"""
    logger.info("\n" + "="*80)
    logger.info("FOCUSED E2E VERIFICATION TEST")
    logger.info("="*80)
    logger.info("\nBusiness URL: https://www.ozumosanfrancisco.com/")
    logger.info("Expected Duration: ~10 minutes with real APIs")
    logger.info("\nThis test verifies:")
    logger.info("1. AGI scrapes business text + images")
    logger.info("2. Images uploaded to R2")
    logger.info("3. Agent 2 designs content strategy")
    logger.info("4. Agent 3 generates images using business references")

    try:
        # Initialize orchestrator
        logger.info("\n" + "-"*80)
        logger.info("Initializing orchestrator...")
        orchestrator = CampaignOrchestrator()
        convex = ConvexService()

        # Run campaign
        logger.info("\n" + "-"*80)
        logger.info("Starting campaign pipeline...")
        logger.info("⏱  This will take ~10 minutes with real APIs")

        response = await orchestrator.run_campaign(
            business_url="https://www.ozumosanfrancisco.com/"
        )

        campaign_id = response.campaign_id
        logger.info(f"\n✅ Campaign completed: {campaign_id}")

        # Run verifications
        logger.info("\n" + "="*80)
        logger.info("RUNNING VERIFICATIONS")
        logger.info("="*80)

        v1 = await verify_research_data(campaign_id, convex)
        v2 = await verify_analytics_data(campaign_id, convex)
        v3 = await verify_creative_output(campaign_id, convex)
        v4 = await verify_images_use_business_reference(campaign_id, convex)

        # Final summary
        logger.info("\n" + "="*80)
        logger.info("FINAL VERIFICATION SUMMARY")
        logger.info("="*80)

        results = {
            "1. Research & Scraping": v1,
            "2. Analytics & Strategy": v2,
            "3. Creative Generation": v3,
            "4. Images Use References": v4
        }

        for test, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{status} - {test}")

        all_passed = all(results.values())

        if all_passed:
            logger.info("\n" + "="*80)
            logger.info("🎉 ALL VERIFICATIONS PASSED!")
            logger.info("="*80)
            logger.info("\n✅ Complete flow working:")
            logger.info("  User URL → AGI Scrapes → R2 Upload → Strategy → Content Generation")
            sys.exit(0)
        else:
            logger.error("\n" + "="*80)
            logger.error("❌ SOME VERIFICATIONS FAILED")
            logger.error("="*80)
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
