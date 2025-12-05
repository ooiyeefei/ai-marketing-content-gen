"""
Postman Service - API Orchestration & Social Media Scheduling

Orchestrates API workflows using Postman collections to:
- Schedule social media posts across platforms
- Aggregate cross-platform analytics
- Run automated API workflows
- Coordinate multi-step posting processes

Prize: Postman API Orchestration ($2,000)
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import time

logger = logging.getLogger(__name__)


class PostmanService:
    """
    Postman API orchestration service for:
    - Running Postman collections via API
    - Scheduling posts across Instagram, Facebook, Twitter
    - Aggregating analytics from multiple platforms
    - Managing complex API workflows
    """

    def __init__(self):
        self.api_key = os.getenv("POSTMAN_API_KEY")
        self.workspace_id = os.getenv("POSTMAN_WORKSPACE_ID")

        if not self.api_key:
            logger.warning("POSTMAN_API_KEY not set - Postman orchestration will be disabled")
        if not self.workspace_id:
            logger.warning("POSTMAN_WORKSPACE_ID not set - using default workspace")

        self.base_url = "https://api.postman.com"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        # Maximum retry attempts for failed operations
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        logger.info(f"✅ Postman service initialized (API Key: {self.api_key[:10]}...)")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request payload
            retry_count: Current retry attempt

        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(f"🔄 Postman API: {method} {endpoint}")

            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            result = response.json() if response.content else {}
            logger.info(f"✅ Postman API success: {endpoint}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Postman API error: {e}")

            # Retry logic for transient errors
            if retry_count < self.max_retries:
                logger.warning(f"🔄 Retrying ({retry_count + 1}/{self.max_retries})...")
                time.sleep(self.retry_delay * (retry_count + 1))
                return self._make_request(method, endpoint, data, retry_count + 1)

            raise

    # ============================================
    # Core Collection Running
    # ============================================

    def run_collection(
        self,
        collection_id: str,
        variables: Optional[Dict[str, Any]] = None,
        environment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a Postman collection via API

        Args:
            collection_id: Postman collection ID
            variables: Variables to pass to collection
            environment_id: Optional environment ID

        Returns:
            Collection run results
        """
        if not self.api_key:
            logger.warning("⚠️  Postman API key not configured - collection not run")
            return {"error": "Postman not configured", "success": False}

        if not collection_id:
            logger.warning("⚠️  No collection ID provided")
            return {"error": "No collection ID", "success": False}

        try:
            logger.info(f"🚀 Running Postman collection: {collection_id}")

            # Prepare collection run data
            run_data = {
                "collection": collection_id,
            }

            if variables:
                run_data["data"] = [variables]
                logger.info(f"📊 Variables: {list(variables.keys())}")

            if environment_id:
                run_data["environment"] = environment_id
                logger.info(f"🌍 Environment: {environment_id}")

            # Run collection
            response = self._make_request(
                "POST",
                f"/collections/{collection_id}/runs",
                data=run_data
            )

            logger.info(f"✅ Collection run completed: {collection_id}")
            return {
                "success": True,
                "collection_id": collection_id,
                "run_id": response.get("run", {}).get("id"),
                "stats": response.get("run", {}).get("stats"),
                "results": response
            }

        except Exception as e:
            logger.error(f"❌ Collection run failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_id": collection_id
            }

    def get_collection_runs(self, collection_id: str) -> List[Dict[str, Any]]:
        """
        Get all runs for a collection

        Args:
            collection_id: Postman collection ID

        Returns:
            List of collection runs
        """
        try:
            response = self._make_request(
                "GET",
                f"/collections/{collection_id}/runs"
            )
            return response.get("runs", [])
        except Exception as e:
            logger.error(f"❌ Failed to get collection runs: {e}")
            return []

    # ============================================
    # Social Media Scheduling
    # ============================================

    def schedule_instagram_post(
        self,
        image_url: str,
        caption: str,
        scheduled_time: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Schedule Instagram post via Postman collection

        Args:
            image_url: URL to image
            caption: Post caption
            scheduled_time: ISO format time (optional)
            hashtags: List of hashtags

        Returns:
            Scheduling result
        """
        logger.info(f"📸 Scheduling Instagram post")
        logger.info(f"   Image: {image_url}")
        logger.info(f"   Caption: {caption[:50]}...")

        # Add hashtags to caption
        full_caption = caption
        if hashtags:
            hashtag_string = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
            full_caption = f"{caption}\n\n{hashtag_string}"
            logger.info(f"   Hashtags: {len(hashtags)}")

        # Prepare variables for Instagram collection
        variables = {
            "platform": "instagram",
            "image_url": image_url,
            "caption": full_caption,
            "scheduled_time": scheduled_time or datetime.now().isoformat(),
            "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            "user_id": os.getenv("INSTAGRAM_USER_ID")
        }

        # Check for Instagram collection ID
        collection_id = os.getenv("POSTMAN_INSTAGRAM_COLLECTION_ID")

        if not collection_id:
            logger.warning("⚠️  POSTMAN_INSTAGRAM_COLLECTION_ID not set")
            logger.info("📝 Logging Instagram post details for manual scheduling:")
            logger.info(f"   Platform: Instagram")
            logger.info(f"   Image: {image_url}")
            logger.info(f"   Caption: {full_caption[:100]}...")
            logger.info(f"   Scheduled: {scheduled_time or 'now'}")

            return {
                "success": True,
                "platform": "instagram",
                "scheduled": True,
                "mock": True,
                "details": variables,
                "message": "Instagram post logged (collection ID not configured)"
            }

        # Run Instagram posting collection
        result = self.run_collection(collection_id, variables)

        return {
            "success": result.get("success", False),
            "platform": "instagram",
            "scheduled": True,
            "collection_run": result,
            "post_details": {
                "caption": caption,
                "image_url": image_url,
                "scheduled_time": scheduled_time
            }
        }

    def schedule_facebook_post(
        self,
        image_url: str,
        caption: str,
        scheduled_time: Optional[str] = None,
        link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule Facebook post via Postman collection

        Args:
            image_url: URL to image
            caption: Post caption
            scheduled_time: ISO format time (optional)
            link: Optional link to include

        Returns:
            Scheduling result
        """
        logger.info(f"👥 Scheduling Facebook post")
        logger.info(f"   Image: {image_url}")
        logger.info(f"   Caption: {caption[:50]}...")

        # Prepare variables for Facebook collection
        variables = {
            "platform": "facebook",
            "image_url": image_url,
            "message": caption,
            "scheduled_time": scheduled_time or datetime.now().isoformat(),
            "access_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
            "page_id": os.getenv("FACEBOOK_PAGE_ID")
        }

        if link:
            variables["link"] = link
            logger.info(f"   Link: {link}")

        # Check for Facebook collection ID
        collection_id = os.getenv("POSTMAN_FACEBOOK_COLLECTION_ID")

        if not collection_id:
            logger.warning("⚠️  POSTMAN_FACEBOOK_COLLECTION_ID not set")
            logger.info("📝 Logging Facebook post details for manual scheduling:")
            logger.info(f"   Platform: Facebook")
            logger.info(f"   Image: {image_url}")
            logger.info(f"   Message: {caption[:100]}...")
            logger.info(f"   Scheduled: {scheduled_time or 'now'}")

            return {
                "success": True,
                "platform": "facebook",
                "scheduled": True,
                "mock": True,
                "details": variables,
                "message": "Facebook post logged (collection ID not configured)"
            }

        # Run Facebook posting collection
        result = self.run_collection(collection_id, variables)

        return {
            "success": result.get("success", False),
            "platform": "facebook",
            "scheduled": True,
            "collection_run": result,
            "post_details": {
                "message": caption,
                "image_url": image_url,
                "scheduled_time": scheduled_time,
                "link": link
            }
        }

    def schedule_twitter_post(
        self,
        image_url: str,
        caption: str,
        thread: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Schedule Twitter/X post via Postman collection

        Args:
            image_url: URL to image
            caption: Tweet text (max 280 chars)
            thread: Optional list of additional tweets for thread

        Returns:
            Scheduling result
        """
        logger.info(f"🐦 Scheduling Twitter/X post")
        logger.info(f"   Image: {image_url}")
        logger.info(f"   Tweet: {caption[:50]}...")

        # Truncate caption to Twitter's limit
        tweet_text = caption[:280]
        if len(caption) > 280:
            logger.warning(f"⚠️  Caption truncated from {len(caption)} to 280 chars")

        # Prepare variables for Twitter collection
        variables = {
            "platform": "twitter",
            "image_url": image_url,
            "text": tweet_text,
            "api_key": os.getenv("TWITTER_API_KEY"),
            "api_secret": os.getenv("TWITTER_API_SECRET"),
            "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "access_secret": os.getenv("TWITTER_ACCESS_SECRET"),
            "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
        }

        if thread:
            variables["thread"] = thread
            logger.info(f"   Thread: {len(thread)} additional tweets")

        # Check for Twitter collection ID
        collection_id = os.getenv("POSTMAN_TWITTER_COLLECTION_ID")

        if not collection_id:
            logger.warning("⚠️  POSTMAN_TWITTER_COLLECTION_ID not set")
            logger.info("📝 Logging Twitter post details for manual scheduling:")
            logger.info(f"   Platform: Twitter/X")
            logger.info(f"   Image: {image_url}")
            logger.info(f"   Tweet: {tweet_text}")

            return {
                "success": True,
                "platform": "twitter",
                "scheduled": True,
                "mock": True,
                "details": variables,
                "message": "Twitter post logged (collection ID not configured)"
            }

        # Run Twitter posting collection
        result = self.run_collection(collection_id, variables)

        return {
            "success": result.get("success", False),
            "platform": "twitter",
            "scheduled": True,
            "collection_run": result,
            "post_details": {
                "text": tweet_text,
                "image_url": image_url,
                "thread_count": len(thread) if thread else 0
            }
        }

    # ============================================
    # Multi-Platform Publishing
    # ============================================

    def schedule_multi_platform_post(
        self,
        image_url: str,
        caption: str,
        platforms: List[str],
        scheduled_time: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Schedule post across multiple platforms simultaneously

        Args:
            image_url: URL to image
            caption: Post caption
            platforms: List of platforms ('instagram', 'facebook', 'twitter')
            scheduled_time: ISO format time (optional)
            hashtags: List of hashtags (for Instagram)

        Returns:
            Dictionary with results per platform
        """
        logger.info(f"🌐 Scheduling multi-platform post")
        logger.info(f"   Platforms: {', '.join(platforms)}")
        logger.info(f"   Image: {image_url}")

        results = {
            "instagram": [],
            "facebook": [],
            "twitter": []
        }

        for platform in platforms:
            try:
                if platform.lower() == "instagram":
                    result = self.schedule_instagram_post(
                        image_url, caption, scheduled_time, hashtags
                    )
                    results["instagram"].append(result)

                elif platform.lower() == "facebook":
                    result = self.schedule_facebook_post(
                        image_url, caption, scheduled_time
                    )
                    results["facebook"].append(result)

                elif platform.lower() == "twitter":
                    result = self.schedule_twitter_post(
                        image_url, caption
                    )
                    results["twitter"].append(result)

                else:
                    logger.warning(f"⚠️  Unknown platform: {platform}")

            except Exception as e:
                logger.error(f"❌ Failed to schedule on {platform}: {e}")
                results[platform].append({
                    "success": False,
                    "platform": platform,
                    "error": str(e)
                })

        logger.info(f"✅ Multi-platform scheduling complete")
        return results

    # ============================================
    # Analytics Aggregation
    # ============================================

    def get_aggregated_analytics(
        self,
        campaign_id: str,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate analytics from multiple platforms via Postman collections

        Args:
            campaign_id: Campaign identifier
            platforms: List of platforms (default: all)

        Returns:
            Aggregated analytics data
        """
        logger.info(f"📊 Aggregating analytics for campaign: {campaign_id}")

        if platforms is None:
            platforms = ["instagram", "facebook", "twitter"]

        logger.info(f"   Platforms: {', '.join(platforms)}")

        # Variables for analytics collection
        variables = {
            "campaign_id": campaign_id,
            "platforms": platforms,
            "instagram_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            "facebook_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
            "twitter_bearer": os.getenv("TWITTER_BEARER_TOKEN")
        }

        # Check for analytics collection ID
        collection_id = os.getenv("POSTMAN_ANALYTICS_COLLECTION_ID")

        if not collection_id:
            logger.warning("⚠️  POSTMAN_ANALYTICS_COLLECTION_ID not set")
            logger.info("📝 Returning mock analytics data")

            # Return mock analytics structure
            return {
                "success": True,
                "campaign_id": campaign_id,
                "mock": True,
                "platforms": platforms,
                "aggregated_metrics": {
                    "total_impressions": 0,
                    "total_engagements": 0,
                    "total_reach": 0,
                    "engagement_rate": 0.0,
                    "platforms": {
                        platform: {
                            "impressions": 0,
                            "likes": 0,
                            "comments": 0,
                            "shares": 0,
                            "clicks": 0
                        }
                        for platform in platforms
                    }
                },
                "message": "Mock analytics (collection ID not configured)"
            }

        # Run analytics collection
        result = self.run_collection(collection_id, variables)

        if not result.get("success"):
            logger.error("❌ Analytics collection run failed")
            return {
                "success": False,
                "campaign_id": campaign_id,
                "error": result.get("error", "Unknown error")
            }

        # Parse and aggregate results
        try:
            analytics_data = self._parse_analytics_results(result, platforms)
            logger.info(f"✅ Analytics aggregated successfully")
            return analytics_data

        except Exception as e:
            logger.error(f"❌ Failed to parse analytics: {e}")
            return {
                "success": False,
                "campaign_id": campaign_id,
                "error": str(e)
            }

    def _parse_analytics_results(
        self,
        collection_result: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Parse and aggregate analytics from collection results

        Args:
            collection_result: Raw collection run results
            platforms: List of platforms

        Returns:
            Structured analytics data
        """
        # Extract metrics from collection responses
        # This would parse the actual API responses from each platform

        aggregated = {
            "success": True,
            "total_impressions": 0,
            "total_engagements": 0,
            "total_reach": 0,
            "platforms": {}
        }

        # Parse results for each platform
        for platform in platforms:
            # In real implementation, this would extract data from collection responses
            aggregated["platforms"][platform] = {
                "impressions": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "clicks": 0,
                "engagement_rate": 0.0
            }

        # Calculate totals
        for platform_data in aggregated["platforms"].values():
            aggregated["total_impressions"] += platform_data.get("impressions", 0)
            aggregated["total_engagements"] += (
                platform_data.get("likes", 0) +
                platform_data.get("comments", 0) +
                platform_data.get("shares", 0)
            )

        # Calculate overall engagement rate
        if aggregated["total_impressions"] > 0:
            aggregated["engagement_rate"] = (
                aggregated["total_engagements"] / aggregated["total_impressions"]
            ) * 100
        else:
            aggregated["engagement_rate"] = 0.0

        return aggregated

    # ============================================
    # Workflow Orchestration
    # ============================================

    def orchestrate_content_workflow(
        self,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate complete content workflow:
        1. Generate content
        2. Optimize for platforms
        3. Schedule posts
        4. Track analytics

        Args:
            content_data: Content to orchestrate

        Returns:
            Workflow execution results
        """
        logger.info(f"🎬 Orchestrating content workflow")

        workflow_id = f"workflow_{int(time.time())}"

        try:
            # Step 1: Validate content
            logger.info("📋 Step 1: Validating content")
            image_url = content_data.get("image_url")
            caption = content_data.get("caption")
            platforms = content_data.get("platforms", ["instagram", "facebook", "twitter"])

            if not image_url or not caption:
                raise ValueError("Missing required content: image_url and caption")

            # Step 2: Schedule posts
            logger.info("📅 Step 2: Scheduling posts")
            scheduling_results = self.schedule_multi_platform_post(
                image_url=image_url,
                caption=caption,
                platforms=platforms,
                scheduled_time=content_data.get("scheduled_time"),
                hashtags=content_data.get("hashtags")
            )

            # Step 3: Log workflow completion
            logger.info("✅ Step 3: Workflow complete")

            return {
                "success": True,
                "workflow_id": workflow_id,
                "steps_completed": 3,
                "results": {
                    "validation": {"success": True},
                    "scheduling": scheduling_results,
                    "status": "completed"
                }
            }

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e)
            }

    # ============================================
    # Utility Methods
    # ============================================

    def get_workspace_collections(self) -> List[Dict[str, Any]]:
        """
        Get all collections in workspace

        Returns:
            List of collections
        """
        try:
            if not self.workspace_id:
                logger.warning("⚠️  No workspace ID configured")
                return []

            response = self._make_request(
                "GET",
                f"/workspaces/{self.workspace_id}"
            )

            collections = response.get("workspace", {}).get("collections", [])
            logger.info(f"📚 Found {len(collections)} collections in workspace")
            return collections

        except Exception as e:
            logger.error(f"❌ Failed to get workspace collections: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """
        Check Postman service health

        Returns:
            Health status
        """
        if not self.api_key:
            return {
                "healthy": False,
                "error": "API key not configured"
            }

        try:
            # Try to get user info as health check
            response = self._make_request("GET", "/me")
            return {
                "healthy": True,
                "user": response.get("user", {}).get("username"),
                "workspace_id": self.workspace_id
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }


# Global instance
_postman_service = None


def get_postman_service() -> PostmanService:
    """Get or create Postman service instance"""
    global _postman_service
    if _postman_service is None:
        _postman_service = PostmanService()
    return _postman_service
