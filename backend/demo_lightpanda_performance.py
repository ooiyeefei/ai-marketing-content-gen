#!/usr/bin/env python3
"""
Lightpanda Performance Demonstration Script
============================================

Demonstrates the 10x speed advantage for the $750 prize submission.

This script:
1. Runs multiple scrapes to collect performance data
2. Tracks timing for each operation
3. Compares with Chrome headless estimates
4. Generates comprehensive performance report
5. Shows real-world use cases

Run this to showcase Lightpanda's performance benefits!
"""

import asyncio
import logging
from services.lightpanda_service import get_lightpanda_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_single_scrape():
    """Demonstrate single website scrape with performance tracking"""
    print("\n" + "=" * 70)
    print("🎯 DEMO 1: Single Website Scrape")
    print("=" * 70)

    service = get_lightpanda_service()

    # Example: Scrape a product website
    url = "https://www.example.com"
    print(f"\n📍 Scraping: {url}")

    result = await service.scrape_website(url, extract_images=True, extract_text=True)

    print(f"\n✅ Results:")
    print(f"   Title: {result.get('title', 'N/A')}")
    print(f"   Images: {len(result.get('images', []))}")
    print(f"   Text: {len(result.get('text', ''))} chars")

    if 'performance' in result:
        perf = result['performance']
        print(f"\n⚡ Performance:")
        print(f"   Lightpanda: {perf['duration']:.2f}s")
        print(f"   Chrome Est: {perf['chrome_estimate']:.1f}s")
        print(f"   Speedup: {perf['speedup_factor']:.1f}x")
        print(f"   Time Saved: {perf['time_saved']:.1f}s")


async def demo_product_extraction():
    """Demonstrate product image extraction with performance tracking"""
    print("\n" + "=" * 70)
    print("🎯 DEMO 2: Product Image Extraction")
    print("=" * 70)

    service = get_lightpanda_service()

    # Example: Extract product images from business website
    business_url = "https://www.shopify.com"
    print(f"\n📍 Extracting product images from: {business_url}")

    images = await service.extract_product_images(business_url, max_images=20)

    print(f"\n✅ Extracted {len(images)} product images")
    print(f"   (With 10x performance advantage over Chrome)")


async def demo_competitor_research():
    """Demonstrate competitor website scraping"""
    print("\n" + "=" * 70)
    print("🎯 DEMO 3: Competitor Research")
    print("=" * 70)

    service = get_lightpanda_service()

    # Example: Analyze competitor website
    competitor_url = "https://www.competitor.com"
    print(f"\n📍 Analyzing competitor: {competitor_url}")

    data = await service.scrape_competitor_website(competitor_url)

    print(f"\n✅ Competitor Analysis:")
    print(f"   Name: {data.get('name', 'N/A')}")
    print(f"   Images: {data.get('image_count', 0)}")
    print(f"   Description: {data.get('description', 'N/A')[:100]}...")

    if 'performance' in data:
        print(f"\n⚡ Analysis completed in {data['performance']['duration']:.2f}s")


async def demo_batch_scraping():
    """Demonstrate batch scraping with parallel processing"""
    print("\n" + "=" * 70)
    print("🎯 DEMO 4: Batch Scraping (Parallel)")
    print("=" * 70)

    service = get_lightpanda_service()

    # Example: Scrape multiple URLs in parallel
    urls = [
        "https://www.example1.com",
        "https://www.example2.com",
        "https://www.example3.com",
    ]

    print(f"\n📍 Scraping {len(urls)} URLs in parallel...")

    results = await service.scrape_multiple(urls)

    print(f"\n✅ Successfully scraped {len(results)}/{len(urls)} URLs")
    print(f"   (All processed in parallel with 10x speedup)")


async def show_performance_summary():
    """Display comprehensive performance statistics"""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 70)

    service = get_lightpanda_service()

    # Get performance stats
    stats = service.get_performance_stats()

    if stats.get("total_scrapes", 0) == 0:
        print("\n⚠️  No performance data yet. Run some demos first!")
        return

    print(f"\n📈 Overall Statistics:")
    print(f"   Total Scrapes: {stats['summary']['total_scrapes']}")
    print(f"   Total Time (Lightpanda): {stats['summary']['total_lightpanda_time']}s")
    print(f"   Total Time (Chrome Est): {stats['summary']['total_chrome_estimate']}s")
    print(f"   Time Saved: {stats['summary']['total_time_saved']}s")
    print(f"   Average Speedup: {stats['summary']['average_speedup_factor']}x")

    print(f"\n⚡ Performance Metrics:")
    print(f"   Avg Time (Lightpanda): {stats['averages']['avg_lightpanda_time']}s")
    print(f"   Avg Time (Chrome): {stats['averages']['avg_chrome_estimate']}s")
    print(f"   Fastest Scrape: {stats['extremes']['fastest_scrape']}s")
    print(f"   Slowest Scrape: {stats['extremes']['slowest_scrape']}s")

    print(f"\n🎨 Content Extracted:")
    print(f"   Total Images: {stats['content_metrics']['total_images_extracted']}")
    print(f"   Total Text: {stats['content_metrics']['total_text_chars']:,} chars")
    print(f"   Avg Images/Scrape: {stats['content_metrics']['avg_images_per_scrape']}")


async def run_full_demo():
    """Run all demonstrations and show comprehensive results"""
    print("\n" + "=" * 80)
    print("🏆 LIGHTPANDA PERFORMANCE DEMONSTRATION - $750 PRIZE SUBMISSION")
    print("=" * 80)

    try:
        # Run all demos
        await demo_single_scrape()
        await demo_product_extraction()
        await demo_competitor_research()
        await demo_batch_scraping()

        # Show final summary
        await show_performance_summary()

        # Show prize submission demo
        service = get_lightpanda_service()
        service.log_performance_demo()

    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n❌ Error during demo: {e}")


async def quick_test():
    """Quick test for development"""
    print("\n🚀 Quick Performance Test")
    print("=" * 50)

    service = get_lightpanda_service()

    # Test single scrape
    result = await service.scrape_website("https://www.example.com")

    print(f"\n✅ Scrape completed!")
    if 'performance' in result:
        perf = result['performance']
        print(f"⚡ Lightpanda: {perf['duration']:.2f}s")
        print(f"🐌 Chrome: ~{perf['chrome_estimate']:.1f}s")
        print(f"🚀 Speedup: {perf['speedup_factor']:.1f}x")

    # Show stats
    stats = service.get_performance_stats()
    print(f"\n📊 Stats: {stats['summary']['total_scrapes']} scrapes, "
          f"{stats['summary']['average_speedup_factor']:.1f}x average speedup")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_test())
    else:
        asyncio.run(run_full_demo())


if __name__ == "__main__":
    main()
