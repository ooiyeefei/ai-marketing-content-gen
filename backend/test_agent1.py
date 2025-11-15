import asyncio
import json
from agents.business_analyst import BusinessAnalystAgent
from models import BusinessInput


async def test_agent():
    """Test Business Analyst Agent with mock business input"""
    agent = BusinessAnalystAgent()

    # Mock business input (using a well-known business for testing)
    business_input = BusinessInput(
        website_url="https://www.example.com",
        business_address="1600 Amphitheatre Parkway, Mountain View, CA",
        brand_voice="professional"
    )

    print("=" * 60)
    print("Testing Business Analyst Agent")
    print("=" * 60)
    print(f"\nInput:")
    print(f"  Website: {business_input.website_url}")
    print(f"  Address: {business_input.business_address}")
    print(f"  Brand Voice: {business_input.brand_voice}")
    print("\n" + "=" * 60)
    print("Starting Analysis...")
    print("=" * 60 + "\n")

    try:
        result = await agent.analyze(business_input)

        print("=" * 60)
        print("Business Profile Generated Successfully!")
        print("=" * 60)
        print("\nBusiness Profile JSON:")
        print(json.dumps(result, indent=2))

        # Validate required fields
        print("\n" + "=" * 60)
        print("Validation:")
        print("=" * 60)

        checks = [
            ("Business Name", result.get('business_name')),
            ("Brand Voice", result.get('brand_voice')),
            ("Website Data", result.get('from_website')),
            ("Maps Data", result.get('from_maps')),
            ("Local Trends", result.get('local_trends')),
            ("Content Themes", result.get('content_themes'))
        ]

        for label, value in checks:
            status = "✓ PASS" if value else "✗ FAIL"
            print(f"  {status}: {label}")

        print("\n" + "=" * 60)
        print("Test Complete")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())
