"""
Parallel.ai Search Service - AI-powered web research using LangChain
Extracts relevant information optimized for LLMs
"""

import os
import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class ParallelSearchService:
    """
    Parallel.ai Search service using LangChain for:
    - Business research
    - Competitor analysis
    - Industry information
    - Market trends

    Returns structured, LLM-optimized excerpts
    """

    def __init__(self):
        self.api_key = os.getenv("PARALLEL_API_KEY")
        self.search_tool = None

        if not self.api_key:
            logger.warning("⚠️  PARALLEL_API_KEY not set - search will be limited")
        else:
            try:
                from langchain_parallel import ParallelWebSearchTool

                # Initialize LangChain tool
                os.environ["PARALLEL_API_KEY"] = self.api_key
                self.search_tool = ParallelWebSearchTool()

                logger.info("✅ Parallel.ai Search service initialized (LangChain)")
            except ImportError as e:
                logger.error(f"❌ Failed to import langchain_parallel: {e}")
                logger.warning("   Install with: pip install langchain-parallel")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Parallel.ai: {e}")

    async def search(
        self,
        objective: str,
        max_results: int = 10,
        max_characters: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        AI-powered search optimized for LLMs using LangChain

        Args:
            objective: Natural language search query
            max_results: Maximum number of results
            max_characters: Max characters per result excerpt

        Returns:
            List of search results with URLs, titles, excerpts
        """
        if not self.search_tool:
            logger.warning("No Parallel search tool - skipping search")
            return []

        try:
            logger.info(f"🔍 Parallel.ai search: {objective[:100]}...")

            # Use LangChain tool's ainvoke for async
            result = await asyncio.to_thread(
                self.search_tool.invoke,
                {
                    "objective": objective,
                    "max_results": max_results
                }
            )

            # Parse results - LangChain tool returns dict with 'results' array
            if isinstance(result, dict) and 'results' in result:
                # Extract results array
                search_results = result.get('results', [])

                results = []
                for item in search_results[:max_results]:
                    # Each result has: url, excerpts, publish_date, title
                    excerpts = item.get('excerpts', [])
                    excerpt_text = ' '.join(excerpts)[:max_characters] if excerpts else ""

                    results.append({
                        "title": item.get('title', ''),
                        "url": item.get('url', ''),
                        "excerpt": excerpt_text,
                        "publish_date": item.get('publish_date', ''),
                        "content": excerpt_text
                    })

                logger.info(f"✅ Found {len(results)} results from Parallel.ai")
            elif isinstance(result, list):
                results = result[:max_results]
            else:
                logger.warning(f"⚠️ Unexpected result format: {type(result)}")
                results = []

            logger.info(f"✅ Found {len(results)} results from Parallel.ai")
            return results

        except Exception as e:
            logger.error(f"Parallel.ai search error: {e}")
            return []

    async def research_business(self, business_name: str, business_url: str) -> Dict[str, Any]:
        """
        Research a business using AI-powered search

        Args:
            business_name: Name of the business
            business_url: Business website URL

        Returns:
            Structured business research data
        """
        logger.info(f"🔬 Researching business: {business_name}")

        # Multiple targeted searches
        searches = [
            f"What does {business_name} do? What products or services do they offer?",
            f"Who is the target audience for {business_name}?",
            f"What industry is {business_name} in? What are the latest trends?",
            f"Who are the main competitors of {business_name}?"
        ]

        all_results = []
        for query in searches:
            results = await self.search(query, max_results=5, max_characters=500)
            all_results.extend(results)

        # Consolidate findings
        business_info = {
            "business_name": business_name,
            "business_url": business_url,
            "research_results": all_results,
            "insights": self._extract_insights(all_results)
        }

        logger.info(f"✅ Research complete: {len(all_results)} sources analyzed")
        return business_info

    def _extract_insights(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key insights from search results"""
        insights = {
            "total_sources": len(results),
            "urls": [r.get("url") for r in results if r.get("url")],
            "key_excerpts": [r.get("excerpt", r.get("content", ""))[:200] for r in results[:5]]
        }
        return insights

    async def research_competitors(self, industry: str, business_name: str) -> List[Dict[str, Any]]:
        """
        Find and research competitors in the industry

        Args:
            industry: Industry name
            business_name: Business to compare against

        Returns:
            List of competitor information
        """
        query = f"Who are the top companies in the {industry} industry similar to {business_name}?"

        results = await self.search(query, max_results=10, max_characters=500)

        competitors = []
        for result in results:
            competitors.append({
                "source": result.get("title", ""),
                "url": result.get("url", ""),
                "info": result.get("excerpt", result.get("content", "")),
                "publish_date": result.get("publish_date", "")
            })

        logger.info(f"✅ Found {len(competitors)} competitor references")
        return competitors

    async def research_industry_trends(self, industry: str) -> List[Dict[str, Any]]:
        """
        Research current trends in an industry

        Args:
            industry: Industry name

        Returns:
            List of trend information
        """
        query = f"What are the latest trends and developments in the {industry} industry in 2025?"

        results = await self.search(query, max_results=8, max_characters=600)

        trends = []
        for result in results:
            trends.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "trend": result.get("excerpt", result.get("content", "")),
                "date": result.get("publish_date", "")
            })

        logger.info(f"✅ Found {len(trends)} industry trends")
        return trends


# Global instance
_parallel_service = None


def get_parallel_service() -> ParallelSearchService:
    """Get or create Parallel.ai service instance"""
    global _parallel_service
    if _parallel_service is None:
        _parallel_service = ParallelSearchService()
    return _parallel_service
