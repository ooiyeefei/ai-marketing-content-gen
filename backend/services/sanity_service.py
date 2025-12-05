"""
Sanity CMS Service - Content management and publishing
Advanced GROQ queries, batch operations, and analytics for deep Sanity integration
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Advanced GROQ query templates for deep Sanity integration
GROQ_QUERIES = {
    "top_performing": """
        *[_type == "content" && defined(metrics.engagement_rate)]
        | order(metrics.engagement_rate desc)
        [0...$limit] {
            _id,
            _createdAt,
            day,
            caption,
            hashtags,
            image_url,
            video_url,
            scheduled_time,
            status,
            metrics {
                views,
                likes,
                comments,
                shares,
                engagement_rate,
                click_through_rate
            },
            "campaign": campaign->{
                _id,
                campaign_id,
                business_url,
                status,
                created_at
            },
            "performance_score": metrics.engagement_rate * metrics.views
        }
    """,

    "campaign_calendar": """
        *[_type == "campaign" && business_url == $business_url]
        | order(created_at desc)
        [0...20] {
            _id,
            campaign_id,
            business_url,
            created_at,
            status,
            "content": *[_type == "content" && references(^._id)]
            | order(day asc) {
                _id,
                day,
                caption[0..100],
                content_type,
                scheduled_time,
                status,
                image_url,
                video_url,
                hashtags[0..5],
                metrics
            },
            "total_posts": count(*[_type == "content" && references(^._id)]),
            "published_posts": count(*[_type == "content" && references(^._id) && status == "published"]),
            "avg_engagement": avg(*[_type == "content" && references(^._id)].metrics.engagement_rate)
        }
    """,

    "campaign_metrics": """
        *[_type == "campaign" && campaign_id == $campaign_id][0] {
            _id,
            campaign_id,
            business_url,
            created_at,
            status,
            "content": *[_type == "content" && references(^._id)] {
                _id,
                day,
                caption,
                content_type,
                scheduled_time,
                status,
                metrics {
                    views,
                    likes,
                    comments,
                    shares,
                    engagement_rate,
                    click_through_rate,
                    reach,
                    impressions
                }
            },
            "analytics": {
                "total_posts": count(*[_type == "content" && references(^._id)]),
                "published_posts": count(*[_type == "content" && references(^._id) && status == "published"]),
                "pending_posts": count(*[_type == "content" && references(^._id) && status == "pending"]),
                "total_views": sum(*[_type == "content" && references(^._id)].metrics.views),
                "total_likes": sum(*[_type == "content" && references(^._id)].metrics.likes),
                "total_comments": sum(*[_type == "content" && references(^._id)].metrics.comments),
                "total_shares": sum(*[_type == "content" && references(^._id)].metrics.shares),
                "avg_engagement_rate": avg(*[_type == "content" && references(^._id)].metrics.engagement_rate),
                "top_performing_day": *[_type == "content" && references(^._id)]
                    | order(metrics.engagement_rate desc)[0].day,
                "best_hashtags": *[_type == "content" && references(^._id)]
                    | order(metrics.engagement_rate desc)[0].hashtags
            }
        }
    """,

    "content_by_performance": """
        *[_type == "content" && defined(metrics)]
        | order(metrics.engagement_rate desc, metrics.views desc)
        {
            _id,
            day,
            caption,
            content_type,
            status,
            scheduled_time,
            image_url,
            video_url,
            hashtags,
            metrics,
            "campaign": campaign->{campaign_id, business_url},
            "performance_tier": select(
                metrics.engagement_rate > 10.0 => "excellent",
                metrics.engagement_rate > 5.0 => "good",
                metrics.engagement_rate > 2.0 => "average",
                "poor"
            )
        }
    """,

    "trending_content": """
        *[_type == "content" &&
          _createdAt > $since &&
          defined(metrics.engagement_rate) &&
          metrics.engagement_rate > $min_engagement]
        | order(metrics.engagement_rate desc)
        [0...$limit] {
            _id,
            _createdAt,
            caption,
            hashtags,
            content_type,
            image_url,
            video_url,
            metrics,
            "campaign": campaign->{business_url, campaign_id},
            "trend_score": metrics.engagement_rate * (metrics.views / 100)
        }
    """,

    "hashtag_performance": """
        *[_type == "content" && defined(metrics) && count(hashtags) > 0] {
            "hashtag": hashtags[],
            "engagement": metrics.engagement_rate,
            "views": metrics.views
        } | {
            "hashtag": hashtag,
            "avg_engagement": avg(engagement),
            "total_views": sum(views),
            "usage_count": count(^)
        } | order(avg_engagement desc)
    """
}

logger = logging.getLogger(__name__)


class SanityService:
    """
    Sanity CMS service for:
    - Campaign publishing
    - Content calendar management
    - Asset organization
    """

    def __init__(self):
        self.project_id = os.getenv("SANITY_PROJECT_ID")
        self.dataset = os.getenv("SANITY_DATASET", "production")
        self.token = os.getenv("SANITY_TOKEN")
        self.api_version = os.getenv("SANITY_API_VERSION", "2025-01-01")

        if not self.project_id or not self.token:
            logger.warning("⚠️  Sanity credentials not set - publishing will be mocked")
        else:
            logger.info(f"✅ Sanity service initialized (project: {self.project_id})")

        self.base_url = f"https://{self.project_id}.api.sanity.io/{self.api_version}/data"
        self.studio_url = f"https://{self.project_id}.sanity.studio"

    def create_campaign(
        self,
        campaign_id: str,
        business_url: str,
        created_at: datetime
    ) -> Dict[str, Any]:
        """
        Create campaign document in Sanity

        Args:
            campaign_id: Campaign ID
            business_url: Business URL
            created_at: Creation timestamp

        Returns:
            Created campaign document
        """
        try:
            if not self.token:
                return self._mock_campaign(campaign_id, business_url)

            import requests

            doc = {
                "_type": "campaign",
                "campaign_id": campaign_id,
                "business_url": business_url,
                "created_at": created_at.isoformat(),
                "status": "scheduled"
            }

            response = requests.post(
                f"{self.base_url}/mutate/{self.dataset}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "mutations": [
                        {"create": doc}
                    ]
                }
            )

            if response.status_code == 200:
                result = response.json()
                created_id = result["results"][0]["id"]
                logger.info(f"✅ Created Sanity campaign: {created_id}")
                return {"_id": created_id, **doc}
            else:
                logger.error(f"Sanity create error: {response.text}")
                return self._mock_campaign(campaign_id, business_url)

        except Exception as e:
            logger.error(f"Error creating Sanity campaign: {e}")
            return self._mock_campaign(campaign_id, business_url)

    def create_content(
        self,
        campaign_id: str,
        day: int,
        caption: str,
        hashtags: List[str],
        image_url: str,
        video_url: Optional[str],
        scheduled_time: str
    ) -> Dict[str, Any]:
        """
        Create content document in Sanity

        Args:
            campaign_id: Parent campaign ID
            day: Day number (1-7)
            caption: Post caption
            hashtags: List of hashtags
            image_url: Image URL
            video_url: Optional video URL
            scheduled_time: Scheduled posting time

        Returns:
            Created content document
        """
        try:
            if not self.token:
                return self._mock_content(campaign_id, day, caption)

            import requests

            doc = {
                "_type": "content",
                "campaign": {
                    "_type": "reference",
                    "_ref": campaign_id
                },
                "day": day,
                "caption": caption,
                "hashtags": hashtags,
                "image_url": image_url,
                "video_url": video_url,
                "scheduled_time": scheduled_time,
                "status": "pending"
            }

            response = requests.post(
                f"{self.base_url}/mutate/{self.dataset}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "mutations": [
                        {"create": doc}
                    ]
                }
            )

            if response.status_code == 200:
                result = response.json()
                created_id = result["results"][0]["id"]
                logger.info(f"✅ Created Sanity content for day {day}")
                return {"_id": created_id, **doc}
            else:
                logger.error(f"Sanity create error: {response.text}")
                return self._mock_content(campaign_id, day, caption)

        except Exception as e:
            logger.error(f"Error creating Sanity content: {e}")
            return self._mock_content(campaign_id, day, caption)

    def upload_image(self, image_data: str) -> Dict[str, Any]:
        """
        Upload image as Sanity asset

        Args:
            image_data: Image URL or base64 data

        Returns:
            Sanity image asset reference
        """
        try:
            if not self.token:
                return {"_type": "image", "url": image_data}

            # For hackathon, just store URL
            # In production, upload binary to Sanity
            return {
                "_type": "image",
                "url": image_data
            }

        except Exception as e:
            logger.error(f"Error uploading image to Sanity: {e}")
            return {"_type": "image", "url": image_data}

    def get_studio_url(self, campaign_id: str) -> str:
        """Get Sanity Studio URL for campaign"""
        return f"{self.studio_url}/desk/campaign;{campaign_id}"

    # =====================================================
    # ADVANCED GROQ QUERY METHODS - Deep Sanity Integration
    # =====================================================

    def _execute_groq_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a GROQ query against Sanity dataset

        Args:
            query: GROQ query string
            params: Query parameters

        Returns:
            Query results or None on error
        """
        try:
            if not self.token:
                logger.warning("Sanity token not configured - returning mock data")
                return None

            import requests

            # Log the query for demonstration
            logger.info(f"📊 Executing GROQ query with params: {params}")
            logger.debug(f"GROQ Query:\n{query[:200]}...")

            # Build query URL with parameters
            query_url = f"https://{self.project_id}.api.sanity.io/{self.api_version}/data/query/{self.dataset}"

            response = requests.get(
                query_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                params={
                    "query": query,
                    **(params or {})
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ GROQ query executed successfully - returned {len(result.get('result', []))} results")
                return result.get("result")
            else:
                logger.error(f"GROQ query failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error executing GROQ query: {e}")
            return None

    def query_top_performing_content(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query top-performing content with engagement metrics using GROQ

        Features:
        - Sorts by engagement rate
        - Includes full metrics
        - Resolves campaign references
        - Calculates performance scores

        Args:
            limit: Maximum number of results

        Returns:
            List of top-performing content with full metrics
        """
        try:
            logger.info(f"🔍 Querying top {limit} performing content pieces")

            query = GROQ_QUERIES["top_performing"]
            params = {"limit": limit}

            result = self._execute_groq_query(query, params)

            if result:
                logger.info(f"✅ Retrieved {len(result)} top-performing content items")
                return result

            # Mock data for demo
            return self._mock_top_performing(limit)

        except Exception as e:
            logger.error(f"Error querying top performing content: {e}")
            return []

    def get_campaign_calendar(
        self,
        business_url: str
    ) -> List[Dict[str, Any]]:
        """
        Get structured content calendar for a business using GROQ

        Features:
        - Retrieves all campaigns for business
        - Includes nested content with references
        - Aggregates metrics per campaign
        - Orders by date

        Args:
            business_url: Business URL to filter campaigns

        Returns:
            List of campaigns with full content calendar
        """
        try:
            logger.info(f"📅 Getting content calendar for: {business_url}")

            query = GROQ_QUERIES["campaign_calendar"]
            params = {"business_url": business_url}

            result = self._execute_groq_query(query, params)

            if result:
                logger.info(f"✅ Retrieved calendar with {len(result)} campaigns")
                return result

            # Mock data for demo
            return self._mock_campaign_calendar(business_url)

        except Exception as e:
            logger.error(f"Error getting campaign calendar: {e}")
            return []

    def aggregate_campaign_metrics(
        self,
        campaign_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Aggregate comprehensive analytics for a campaign using GROQ

        Features:
        - Calculates total views, likes, comments, shares
        - Computes average engagement rates
        - Identifies top-performing content
        - Extracts best-performing hashtags
        - Tracks post status distribution

        Args:
            campaign_id: Campaign ID to analyze

        Returns:
            Dictionary with comprehensive campaign analytics
        """
        try:
            logger.info(f"📈 Aggregating metrics for campaign: {campaign_id}")

            query = GROQ_QUERIES["campaign_metrics"]
            params = {"campaign_id": campaign_id}

            result = self._execute_groq_query(query, params)

            if result:
                logger.info(f"✅ Retrieved metrics for {result.get('analytics', {}).get('total_posts', 0)} posts")
                return result

            # Mock data for demo
            return self._mock_campaign_metrics(campaign_id)

        except Exception as e:
            logger.error(f"Error aggregating campaign metrics: {e}")
            return None

    def get_trending_content(
        self,
        days_back: int = 7,
        min_engagement: float = 3.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending content from recent period using GROQ

        Features:
        - Filters by time period
        - Minimum engagement threshold
        - Calculates trend scores
        - Resolves campaign references

        Args:
            days_back: Days to look back
            min_engagement: Minimum engagement rate
            limit: Maximum results

        Returns:
            List of trending content with scores
        """
        try:
            since = (datetime.now() - timedelta(days=days_back)).isoformat()

            logger.info(f"📊 Getting trending content (last {days_back} days, min engagement: {min_engagement}%)")

            query = GROQ_QUERIES["trending_content"]
            params = {
                "since": since,
                "min_engagement": min_engagement,
                "limit": limit
            }

            result = self._execute_groq_query(query, params)

            if result:
                logger.info(f"✅ Found {len(result)} trending content items")
                return result

            return []

        except Exception as e:
            logger.error(f"Error getting trending content: {e}")
            return []

    def analyze_hashtag_performance(self) -> List[Dict[str, Any]]:
        """
        Analyze hashtag performance across all content using GROQ

        Features:
        - Aggregates metrics per hashtag
        - Calculates average engagement
        - Counts usage frequency
        - Sums total views

        Returns:
            List of hashtags with performance metrics
        """
        try:
            logger.info("🏷️  Analyzing hashtag performance")

            query = GROQ_QUERIES["hashtag_performance"]

            result = self._execute_groq_query(query)

            if result:
                logger.info(f"✅ Analyzed {len(result)} hashtags")
                return result

            return []

        except Exception as e:
            logger.error(f"Error analyzing hashtag performance: {e}")
            return []

    def bulk_update_content(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch update multiple content documents

        Features:
        - Single API call for multiple updates
        - Transactional updates
        - Supports partial updates
        - Returns updated document IDs

        Args:
            updates: List of update operations, each with:
                - content_id: Document ID
                - fields: Fields to update

        Returns:
            Dictionary with success status and updated IDs
        """
        try:
            if not self.token:
                logger.warning("Sanity token not set - mocking bulk update")
                return self._mock_bulk_update(updates)

            import requests

            logger.info(f"📝 Bulk updating {len(updates)} content documents")

            # Build mutations for batch update
            mutations = []
            for update in updates:
                content_id = update.get("content_id")
                fields = update.get("fields", {})

                mutations.append({
                    "patch": {
                        "id": content_id,
                        "set": fields
                    }
                })

            response = requests.post(
                f"{self.base_url}/mutate/{self.dataset}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={"mutations": mutations},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                updated_ids = [r.get("id") for r in result.get("results", [])]
                logger.info(f"✅ Successfully updated {len(updated_ids)} documents")

                return {
                    "success": True,
                    "updated_count": len(updated_ids),
                    "updated_ids": updated_ids
                }
            else:
                logger.error(f"Bulk update failed: {response.text}")
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            return {"success": False, "error": str(e)}

    def update_content_metrics(
        self,
        content_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Update metrics for a single content document

        Args:
            content_id: Content document ID
            metrics: Metrics to update (views, likes, comments, etc.)

        Returns:
            Success status
        """
        try:
            if not self.token:
                logger.info(f"Mocking metrics update for {content_id}")
                return True

            import requests

            logger.info(f"📊 Updating metrics for content: {content_id}")

            response = requests.post(
                f"{self.base_url}/mutate/{self.dataset}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "mutations": [{
                        "patch": {
                            "id": content_id,
                            "set": {"metrics": metrics}
                        }
                    }]
                },
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"✅ Updated metrics for {content_id}")
                return True
            else:
                logger.error(f"Failed to update metrics: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return False

    def query_content_by_performance_tier(
        self,
        tier: str = "excellent"
    ) -> List[Dict[str, Any]]:
        """
        Query content filtered by performance tier using GROQ

        Tiers:
        - excellent: engagement_rate > 10%
        - good: engagement_rate > 5%
        - average: engagement_rate > 2%
        - poor: engagement_rate <= 2%

        Args:
            tier: Performance tier to filter

        Returns:
            List of content in specified tier
        """
        try:
            logger.info(f"🎯 Querying content in '{tier}' performance tier")

            query = GROQ_QUERIES["content_by_performance"]
            result = self._execute_groq_query(query)

            if result:
                filtered = [c for c in result if c.get("performance_tier") == tier]
                logger.info(f"✅ Found {len(filtered)} content items in '{tier}' tier")
                return filtered

            return []

        except Exception as e:
            logger.error(f"Error querying by performance tier: {e}")
            return []

    # =====================================================
    # MOCK DATA METHODS FOR DEMO/TESTING
    # =====================================================

    def _mock_top_performing(self, limit: int) -> List[Dict[str, Any]]:
        """Mock top-performing content for testing"""
        return [{
            "_id": f"mock_content_{i}",
            "day": i + 1,
            "caption": f"Mock high-performing content day {i+1}",
            "metrics": {
                "views": 10000 - i * 500,
                "likes": 800 - i * 50,
                "engagement_rate": 8.5 - i * 0.3
            },
            "performance_score": (8.5 - i * 0.3) * (10000 - i * 500),
            "campaign": {
                "campaign_id": "mock_campaign",
                "business_url": "https://example.com"
            }
        } for i in range(min(limit, 5))]

    def _mock_campaign_calendar(self, business_url: str) -> List[Dict[str, Any]]:
        """Mock campaign calendar for testing"""
        return [{
            "_id": "mock_campaign_1",
            "campaign_id": "mock_campaign_2025",
            "business_url": business_url,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "content": [
                {
                    "_id": f"mock_content_{i}",
                    "day": i,
                    "caption": f"Mock content for day {i}",
                    "scheduled_time": f"{9+i}:00",
                    "status": "pending"
                }
                for i in range(1, 8)
            ],
            "total_posts": 7,
            "published_posts": 0,
            "avg_engagement": 5.2
        }]

    def _mock_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Mock campaign metrics for testing"""
        return {
            "_id": "mock_campaign_id",
            "campaign_id": campaign_id,
            "business_url": "https://example.com",
            "analytics": {
                "total_posts": 7,
                "published_posts": 5,
                "pending_posts": 2,
                "total_views": 45000,
                "total_likes": 3500,
                "total_comments": 450,
                "total_shares": 280,
                "avg_engagement_rate": 6.8,
                "top_performing_day": 3,
                "best_hashtags": ["#business", "#marketing", "#growth"]
            }
        }

    def _mock_bulk_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock bulk update for testing"""
        return {
            "success": True,
            "updated_count": len(updates),
            "updated_ids": [u.get("content_id") for u in updates]
        }

    def _mock_campaign(self, campaign_id: str, business_url: str) -> Dict[str, Any]:
        """Mock campaign document for testing"""
        return {
            "_id": f"mock_{campaign_id}",
            "_type": "campaign",
            "campaign_id": campaign_id,
            "business_url": business_url,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }

    def _mock_content(self, campaign_id: str, day: int, caption: str) -> Dict[str, Any]:
        """Mock content document for testing"""
        return {
            "_id": f"mock_{campaign_id}_day{day}",
            "_type": "content",
            "campaign": {"_ref": campaign_id},
            "day": day,
            "caption": caption,
            "status": "pending"
        }


# Global instance
_sanity_service = None


def get_sanity_service() -> SanityService:
    """Get or create Sanity service instance"""
    global _sanity_service
    if _sanity_service is None:
        _sanity_service = SanityService()
    return _sanity_service
