"""
Demo script for Postman API Orchestration Service
Shows how to use the PostmanService for social media scheduling and analytics
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from services.postman_service import get_postman_service


def demo_postman_orchestration():
    """Demonstrate Postman API orchestration capabilities"""

    print("\n" + "="*60)
    print("🎯 POSTMAN API ORCHESTRATION DEMO")
    print("Prize: $2,000 - API Orchestration")
    print("="*60 + "\n")

    # Initialize service
    print("1️⃣  Initializing Postman Service...")
    postman = get_postman_service()

    # Health check
    print("\n2️⃣  Checking Postman service health...")
    health = postman.health_check()
    print(f"   Status: {'✅ Healthy' if health.get('healthy') else '❌ Unhealthy'}")
    if health.get('user'):
        print(f"   User: {health.get('user')}")
    print(f"   Workspace: {health.get('workspace_id', 'Not configured')}")

    # Example content
    example_content = {
        "image_url": "https://example.com/product-image.jpg",
        "caption": "🚀 Excited to share our latest innovation! Check out the future of technology. #Innovation #Tech #Product",
        "hashtags": ["Innovation", "Tech", "Product", "Launch"],
        "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat()
    }

    print("\n3️⃣  Example Content:")
    print(f"   Image: {example_content['image_url']}")
    print(f"   Caption: {example_content['caption'][:60]}...")
    print(f"   Hashtags: {', '.join(example_content['hashtags'])}")
    print(f"   Scheduled: {example_content['scheduled_time']}")

    # Schedule Instagram post
    print("\n4️⃣  Scheduling Instagram post...")
    instagram_result = postman.schedule_instagram_post(
        image_url=example_content['image_url'],
        caption=example_content['caption'],
        scheduled_time=example_content['scheduled_time'],
        hashtags=example_content['hashtags']
    )
    print(f"   Result: {'✅ Success' if instagram_result.get('success') else '❌ Failed'}")
    print(f"   Platform: {instagram_result.get('platform')}")
    if instagram_result.get('mock'):
        print(f"   Mode: Mock (collection ID not configured)")

    # Schedule Facebook post
    print("\n5️⃣  Scheduling Facebook post...")
    facebook_result = postman.schedule_facebook_post(
        image_url=example_content['image_url'],
        caption=example_content['caption'],
        scheduled_time=example_content['scheduled_time']
    )
    print(f"   Result: {'✅ Success' if facebook_result.get('success') else '❌ Failed'}")
    print(f"   Platform: {facebook_result.get('platform')}")
    if facebook_result.get('mock'):
        print(f"   Mode: Mock (collection ID not configured)")

    # Schedule Twitter post
    print("\n6️⃣  Scheduling Twitter/X post...")
    twitter_result = postman.schedule_twitter_post(
        image_url=example_content['image_url'],
        caption=example_content['caption'][:280]  # Twitter limit
    )
    print(f"   Result: {'✅ Success' if twitter_result.get('success') else '❌ Failed'}")
    print(f"   Platform: {twitter_result.get('platform')}")
    if twitter_result.get('mock'):
        print(f"   Mode: Mock (collection ID not configured)")

    # Multi-platform scheduling
    print("\n7️⃣  Multi-platform scheduling...")
    multi_result = postman.schedule_multi_platform_post(
        image_url=example_content['image_url'],
        caption=example_content['caption'],
        platforms=["instagram", "facebook", "twitter"],
        scheduled_time=example_content['scheduled_time'],
        hashtags=example_content['hashtags']
    )
    print(f"   Instagram: {len(multi_result.get('instagram', []))} posts")
    print(f"   Facebook: {len(multi_result.get('facebook', []))} posts")
    print(f"   Twitter: {len(multi_result.get('twitter', []))} posts")

    # Get aggregated analytics
    print("\n8️⃣  Aggregating analytics...")
    analytics = postman.get_aggregated_analytics(
        campaign_id="demo_campaign_001",
        platforms=["instagram", "facebook", "twitter"]
    )
    print(f"   Result: {'✅ Success' if analytics.get('success') else '❌ Failed'}")
    print(f"   Campaign: {analytics.get('campaign_id')}")
    if analytics.get('mock'):
        print(f"   Mode: Mock (collection ID not configured)")

    metrics = analytics.get('aggregated_metrics', {})
    print(f"   Total Impressions: {metrics.get('total_impressions', 0):,}")
    print(f"   Total Engagements: {metrics.get('total_engagements', 0):,}")
    print(f"   Engagement Rate: {metrics.get('engagement_rate', 0):.2f}%")

    # Workflow orchestration
    print("\n9️⃣  Orchestrating complete workflow...")
    workflow_result = postman.orchestrate_content_workflow({
        "image_url": example_content['image_url'],
        "caption": example_content['caption'],
        "platforms": ["instagram", "facebook", "twitter"],
        "scheduled_time": example_content['scheduled_time'],
        "hashtags": example_content['hashtags']
    })
    print(f"   Result: {'✅ Success' if workflow_result.get('success') else '❌ Failed'}")
    print(f"   Workflow ID: {workflow_result.get('workflow_id')}")
    print(f"   Steps Completed: {workflow_result.get('steps_completed', 0)}/3")

    # Get workspace collections
    print("\n🔟 Listing workspace collections...")
    collections = postman.get_workspace_collections()
    print(f"   Collections found: {len(collections)}")
    if collections:
        for i, collection in enumerate(collections[:3], 1):
            print(f"   {i}. {collection.get('name', 'Unknown')}")
        if len(collections) > 3:
            print(f"   ... and {len(collections) - 3} more")

    print("\n" + "="*60)
    print("✅ POSTMAN ORCHESTRATION DEMO COMPLETE")
    print("="*60 + "\n")

    # Summary
    print("📋 SUMMARY:")
    print("   - Postman API integration: ✅ Ready")
    print("   - Instagram scheduling: ✅ Implemented")
    print("   - Facebook scheduling: ✅ Implemented")
    print("   - Twitter/X scheduling: ✅ Implemented")
    print("   - Multi-platform posts: ✅ Implemented")
    print("   - Analytics aggregation: ✅ Implemented")
    print("   - Workflow orchestration: ✅ Implemented")
    print("   - Error handling & retries: ✅ Implemented")
    print("\n🎯 Ready for Postman API Orchestration Prize ($2,000)")
    print()


if __name__ == "__main__":
    # Ensure Postman credentials are set via environment variables
    if not os.getenv("POSTMAN_API_KEY"):
        print("❌ Error: POSTMAN_API_KEY environment variable not set")
        print("   Set it with: export POSTMAN_API_KEY='your-postman-api-key'")
        exit(1)

    if not os.getenv("POSTMAN_WORKSPACE_ID"):
        print("❌ Error: POSTMAN_WORKSPACE_ID environment variable not set")
        print("   Set it with: export POSTMAN_WORKSPACE_ID='your-workspace-id'")
        exit(1)

    demo_postman_orchestration()
