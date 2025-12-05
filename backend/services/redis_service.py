"""
Redis Service - Vector database, caching, and state management
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis
from redis.commands.search.field import VectorField, TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

logger = logging.getLogger(__name__)


class RedisService:
    """
    Redis service for:
    - Vector storage and semantic search
    - Caching AI generations
    - Campaign state storage
    """

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        if not self.redis_url:
            raise ValueError("REDIS_URL environment variable not set")

        # Initialize Redis client
        self.client = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test connection
        try:
            self.client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

        # Initialize vector indexes
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create vector indexes if they don't exist"""
        try:
            # Campaigns index for semantic search
            self._create_campaigns_index()

            # Research index for business context
            self._create_research_index()

            # Assets index for caching generated content
            self._create_assets_index()

            logger.info("✅ Redis vector indexes ready")

        except Exception as e:
            logger.warning(f"Index creation skipped (may already exist): {e}")

    def _create_campaigns_index(self):
        """Create index for campaign semantic search"""
        schema = (
            TextField("campaign_id"),
            TextField("business_url"),
            TextField("industry"),
            NumericField("performance_score"),
            VectorField(
                "embedding",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,  # Claude embeddings dimension
                    "DISTANCE_METRIC": "COSINE"
                }
            )
        )

        definition = IndexDefinition(
            prefix=["campaign:"],
            index_type=IndexType.HASH
        )

        try:
            self.client.ft("campaigns").create_index(
                schema,
                definition=definition
            )
        except Exception as e:
            if "Index already exists" not in str(e):
                raise

    def _create_research_index(self):
        """Create index for research data"""
        schema = (
            TextField("business_url"),
            TextField("research_type"),  # website, competitor, trends
            TextField("industry"),
            VectorField(
                "embedding",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,
                    "DISTANCE_METRIC": "COSINE"
                }
            )
        )

        definition = IndexDefinition(
            prefix=["research:"],
            index_type=IndexType.HASH
        )

        try:
            self.client.ft("research").create_index(
                schema,
                definition=definition
            )
        except Exception as e:
            if "Index already exists" not in str(e):
                raise

    def _create_assets_index(self):
        """Create index for generated assets caching"""
        schema = (
            TextField("asset_type"),  # caption, image, video
            TextField("campaign_id"),
            VectorField(
                "prompt_embedding",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,
                    "DISTANCE_METRIC": "COSINE"
                }
            )
        )

        definition = IndexDefinition(
            prefix=["asset:"],
            index_type=IndexType.HASH
        )

        try:
            self.client.ft("assets").create_index(
                schema,
                definition=definition
            )
        except Exception as e:
            if "Index already exists" not in str(e):
                raise

    # ============================================
    # Basic Storage Operations
    # ============================================

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Store data with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                # Use custom JSON encoder to handle datetime objects
                value = json.dumps(value, default=str)
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data"""
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis GET error for {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete data"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for {key}: {e}")
            return False

    # ============================================
    # Vector Operations
    # ============================================

    def store_with_embedding(
        self,
        key: str,
        data: Dict[str, Any],
        embedding: List[float],
        ex: Optional[int] = None
    ) -> bool:
        """
        Store data with vector embedding for semantic search

        Args:
            key: Redis key
            data: Dictionary of data to store
            embedding: Vector embedding (1536 dimensions for Claude)
            ex: Optional expiration in seconds
        """
        try:
            # Store embedding as bytes
            data["embedding"] = self._serialize_vector(embedding)

            # Flatten dict for Redis hash
            flat_data = {}
            for k, v in data.items():
                if isinstance(v, (dict, list)) and k != "embedding":
                    flat_data[k] = json.dumps(v)
                else:
                    flat_data[k] = v

            # Store in Redis hash
            self.client.hset(key, mapping=flat_data)

            if ex:
                self.client.expire(key, ex)

            return True

        except Exception as e:
            logger.error(f"Error storing with embedding for {key}: {e}")
            return False

    def vector_search(
        self,
        index_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search

        Args:
            index_name: Name of the index (campaigns, research, assets)
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional filters (e.g., {"industry": "coffee"})

        Returns:
            List of matching documents with scores
        """
        try:
            # Check if index exists
            try:
                self.client.ft(index_name).info()
            except Exception as e:
                logger.warning(f"Index {index_name} not found or empty: {e}")
                return []

            # Serialize query vector
            query_vector = self._serialize_vector(query_embedding)

            # Build query - use simpler syntax
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    filter_parts.append(f"@{key}:{value}")
                base_query = f"({' '.join(filter_parts)})"
            else:
                base_query = "*"

            # Create KNN query
            query = (
                Query(f"{base_query}=>[KNN {top_k} @embedding $vec AS score]")
                .return_fields("score")
                .sort_by("score")
                .paging(0, top_k)
                .dialect(2)  # Use dialect 2 for vector search
            )

            # Execute search
            results = self.client.ft(index_name).search(
                query,
                query_params={"vec": query_vector}
            )

            # Parse results
            docs = []
            for doc in results.docs:
                doc_dict = {
                    "id": doc.id,
                    "score": float(doc.score),
                }
                # Add all fields
                for key, value in doc.__dict__.items():
                    if key not in ["id", "score", "payload"]:
                        try:
                            doc_dict[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            doc_dict[key] = value
                docs.append(doc_dict)

            return docs

        except Exception as e:
            logger.error(f"Vector search error on {index_name}: {e}")
            return []

    def _serialize_vector(self, vector: List[float]) -> bytes:
        """Convert vector to bytes for Redis storage"""
        import struct
        import numpy as np
        return np.array(vector, dtype=np.float32).tobytes()

    # ============================================
    # Campaign Operations
    # ============================================

    def store_campaign(
        self,
        campaign_id: str,
        business_url: str,
        industry: str,
        embedding: List[float],
        data: Dict[str, Any]
    ) -> bool:
        """Store campaign with embedding for future similarity search"""
        key = f"campaign:{campaign_id}"
        campaign_data = {
            "campaign_id": campaign_id,
            "business_url": business_url,
            "industry": industry,
            "performance_score": 0.0,  # Will be updated later
            **data
        }
        return self.store_with_embedding(key, campaign_data, embedding, ex=2592000)  # 30 days

    def get_similar_campaigns(
        self,
        query_embedding: List[float],
        industry: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar past campaigns for strategy insights"""
        filters = {"industry": industry} if industry else None
        return self.vector_search("campaigns", query_embedding, top_k, filters)

    # ============================================
    # Research Operations
    # ============================================

    def store_research(
        self,
        business_url: str,
        research_type: str,
        industry: str,
        embedding: List[float],
        data: Dict[str, Any]
    ) -> bool:
        """Store research data with embedding"""
        key = f"research:{business_url}:{research_type}"
        research_data = {
            "business_url": business_url,
            "research_type": research_type,
            "industry": industry,
            **data
        }
        return self.store_with_embedding(key, research_data, embedding, ex=86400)  # 24 hours

    # ============================================
    # Caching Operations
    # ============================================

    def cache_generation(
        self,
        cache_key: str,
        result: Any,
        ttl: int = 3600
    ) -> bool:
        """Cache AI generation result"""
        return self.set(f"cache:{cache_key}", result, ex=ttl)

    def get_cached_generation(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached generation"""
        return self.get(f"cache:{cache_key}")

    def check_similar_asset(
        self,
        prompt_embedding: List[float],
        asset_type: str,
        threshold: float = 0.95
    ) -> Optional[str]:
        """
        Check if similar asset was generated recently

        Args:
            prompt_embedding: Embedding of the prompt
            asset_type: Type of asset (caption, image, video)
            threshold: Similarity threshold (0.95 = 95% similar)

        Returns:
            Asset URL if found, None otherwise
        """
        results = self.vector_search(
            "assets",
            prompt_embedding,
            top_k=1,
            filters={"asset_type": asset_type}
        )

        if results and results[0]["score"] >= threshold:
            return results[0].get("asset_url")

        return None

    # ============================================
    # Performance Tracking
    # ============================================

    def store_performance_metrics(
        self,
        campaign_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Store campaign performance metrics"""
        key = f"metrics:{campaign_id}"
        return self.set(key, metrics, ex=2592000)  # 30 days

    def get_performance_metrics(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve campaign performance metrics"""
        return self.get(f"metrics:{campaign_id}")

    # ============================================
    # Batch Operations
    # ============================================

    def get_all(self, pattern: str) -> Dict[str, Any]:
        """Get all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            result = {}
            for key in keys:
                result[key] = self.get(key)
            return result
        except Exception as e:
            logger.error(f"Error getting keys for pattern {pattern}: {e}")
            return {}

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")
            return 0

    # ============================================
    # Learning Operations (Self-Evolving System)
    # ============================================

    def store_learning(
        self,
        campaign_id: str,
        industry: str,
        learning_text: str,
        embedding: List[float],
        performance_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store learning from completed campaign for future retrieval

        Args:
            campaign_id: Campaign ID
            industry: Business industry
            learning_text: What was learned (e.g., "Video posts get 3x engagement in coffee industry")
            embedding: Vector embedding of learning text
            performance_score: Campaign performance (0-1)
            metadata: Additional metadata (e.g., content types used, themes, etc.)

        Returns:
            True if stored successfully
        """
        try:
            key = f"learning:{campaign_id}"
            learning_data = {
                "campaign_id": campaign_id,
                "industry": industry,
                "learning_text": learning_text,
                "performance_score": performance_score,
                "created_at": str(datetime.now()),
                "metadata": metadata or {}
            }

            # Store with embedding for semantic retrieval
            success = self.store_with_embedding(
                key,
                learning_data,
                embedding,
                ex=7776000  # 90 days
            )

            if success:
                logger.info(f"✅ Stored learning for campaign {campaign_id}: {learning_text[:50]}...")

            return success

        except Exception as e:
            logger.error(f"Failed to store learning for {campaign_id}: {e}")
            return False

    def retrieve_learnings(
        self,
        query_embedding: List[float],
        industry: Optional[str] = None,
        min_performance: float = 0.5,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant learnings from past campaigns

        Args:
            query_embedding: Embedding of current context (e.g., business description)
            industry: Filter by industry
            min_performance: Minimum performance score to consider
            top_k: Number of learnings to retrieve

        Returns:
            List of relevant learnings with scores
        """
        try:
            # Build filters
            filters = {}
            if industry:
                filters["industry"] = industry

            # Perform vector search on learnings
            # Note: We'll search in campaigns index for now
            # TODO: Create dedicated learnings index
            results = self.get_similar_campaigns(
                query_embedding,
                industry=industry,
                top_k=top_k
            )

            # Filter by performance
            filtered_results = [
                r for r in results
                if r.get("performance_score", 0) >= min_performance
            ]

            logger.info(f"📚 Retrieved {len(filtered_results)} learnings (min_perf={min_performance})")

            return filtered_results

        except Exception as e:
            logger.error(f"Failed to retrieve learnings: {e}")
            return []

    def store_campaign_analysis(
        self,
        campaign_id: str,
        analysis: Dict[str, Any],
        embedding: List[float]
    ) -> bool:
        """
        Store post-campaign analysis with insights

        Args:
            campaign_id: Campaign ID
            analysis: Analysis results (what worked, what didn't, insights)
            embedding: Embedding of analysis text

        Returns:
            True if stored successfully
        """
        try:
            key = f"analysis:{campaign_id}"
            analysis_data = {
                "campaign_id": campaign_id,
                "created_at": str(datetime.now()),
                **analysis
            }

            success = self.store_with_embedding(
                key,
                analysis_data,
                embedding,
                ex=7776000  # 90 days
            )

            if success:
                logger.info(f"✅ Stored analysis for campaign {campaign_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to store analysis for {campaign_id}: {e}")
            return False


# Global instance
_redis_service = None


def get_redis_service() -> RedisService:
    """Get or create Redis service instance"""
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service
