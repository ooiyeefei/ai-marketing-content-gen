import os
import httpx
from typing import Dict, List, Any, Optional
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class AGIService:
    """
    AGI API service for intelligent web research using sessions-based API.

    Capabilities:
    - Multi-step web navigation
    - Business context extraction
    - Intelligent competitor discovery
    - Deep competitor research
    - Market trend synthesis
    """

    def __init__(self):
        self.api_key = os.getenv("AGI_API_KEY")
        if not self.api_key:
            raise ValueError("AGI_API_KEY environment variable not set")

        self.base_url = "https://api.agi.tech/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("✓ AGI API initialized with sessions-based API")

    async def _create_session(self) -> str:
        """
        Create a new AGI session (isolated browser environment).

        Returns:
            session_id: Unique session identifier
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/sessions",
                    headers=self.headers,
                    json={}
                )
                response.raise_for_status()

                session_data = response.json()
                session_id = session_data.get("session_id")  # Correct field name per API docs
                logger.info(f"✓ AGI session created: {session_id}")
                return session_id

        except Exception as e:
            logger.error(f"✗ AGI session creation failed: {e}")
            raise

    async def _send_message(
        self,
        session_id: str,
        task: str,
        url: Optional[str] = None,
        max_wait: int = 180
    ) -> Dict[str, Any]:
        """
        Send a message to an AGI session and wait for completion.

        Args:
            session_id: Active session ID
            task: Task instruction for the agent
            url: Optional starting URL
            max_wait: Maximum wait time in seconds (default: 180 = 3 minutes)

        Returns:
            Agent's response data
        """
        try:
            # Send message
            async with httpx.AsyncClient(timeout=60.0) as client:
                message_payload = {"message": task}  # API uses "message" not "task"
                if url:
                    message_payload["start_url"] = url  # API uses "start_url" not "url"

                response = await client.post(
                    f"{self.base_url}/sessions/{session_id}/message",  # Singular: /message not /messages
                    headers=self.headers,
                    json=message_payload
                )
                response.raise_for_status()

                message_data = response.json()
                message_id = message_data.get("id")
                logger.info(f"✓ AGI message sent: {message_id}")

                # Poll for completion via messages endpoint
                result = await self._poll_messages(session_id, max_wait=max_wait)
                return result

        except Exception as e:
            logger.error(f"✗ AGI message failed: {e}")
            raise

    async def _poll_messages(
        self,
        session_id: str,
        max_wait: int = 180,  # Hard 3-minute maximum as requested by user
        idle_timeout: int = 90
    ) -> Dict[str, Any]:
        """
        Poll session messages until agent completes the task.
        Implements HARD 3-MINUTE TIMEOUT based on wall-clock time.
        Also implements idle detection: if no new messages for idle_timeout seconds,
        cancels session and attempts to extract results.

        Args:
            session_id: Active session ID
            max_wait: HARD maximum wall-clock time in seconds (default: 180 = 3 minutes)
            idle_timeout: Seconds without new messages before considering idle (default: 90)

        Returns:
            Final result from agent
        """
        import time

        # Track ACTUAL wall-clock time, not just sleep time
        start_time = time.time()

        after_id = 0
        all_messages = []
        retry_count = 0
        max_retries = 3
        last_message_time = None
        idle_check_start = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                # Check HARD timeout based on actual elapsed time
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_wait:
                    logger.warning(f"⚠ HARD TIMEOUT: Session {session_id} exceeded {max_wait}s wall-clock limit ({elapsed_time:.1f}s elapsed)")
                    logger.info(f"  → Force-canceling session and extracting results...")

                    # Try to extract results from messages before canceling
                    result = self._extract_result_from_messages(all_messages)

                    # Cancel the session
                    try:
                        await self._close_session(session_id)
                    except Exception as e:
                        logger.error(f"Failed to close timed-out session: {e}")

                    if result:
                        logger.info(f"✓ Extracted partial results from timed-out session")
                        return result
                    else:
                        # Return empty/minimal data instead of raising exception
                        logger.warning(f"⚠ No extractable results from timeout - returning minimal data")
                        return {
                            "partial": True,
                            "timeout": True,
                            "messages": all_messages,
                            "error": f"Session exceeded {max_wait}s timeout"
                        }

                try:
                    response = await client.get(
                        f"{self.base_url}/sessions/{session_id}/messages?after_id={after_id}",
                        headers=self.headers
                    )
                    response.raise_for_status()

                    # Reset retry count on successful request
                    retry_count = 0

                    data = response.json()
                    messages = data.get("messages", [])

                    # Process new messages
                    for msg in messages:
                        message_id = msg.get("id", 0)
                        message_type = msg.get("type", "")
                        content = msg.get("content", {})

                        all_messages.append(msg)
                        after_id = max(after_id, message_id)

                        logger.info(f"  AGI {message_type}: {str(content)[:100]}")

                        # Check for completion
                        if message_type == "DONE":
                            logger.info(f"✓ AGI task completed in session {session_id}")

                            # Handle different content formats from AGI
                            if isinstance(content, dict):
                                # Already a dict, perfect!
                                return content
                            elif isinstance(content, str):
                                # Try to parse as JSON
                                try:
                                    parsed = json.loads(content)
                                    if isinstance(parsed, dict):
                                        return parsed
                                except json.JSONDecodeError:
                                    pass

                                # Try to extract JSON from text (agent sometimes adds explanation + JSON)
                                import re
                                json_match = re.search(r'\{[\s\S]*\}', content)
                                if json_match:
                                    try:
                                        parsed = json.loads(json_match.group())
                                        if isinstance(parsed, dict):
                                            logger.warning(f"Extracted JSON from mixed content")
                                            return parsed
                                    except json.JSONDecodeError:
                                        pass

                                # Last resort: agent returned only descriptive text, not JSON
                                logger.error(f"AGI returned plain text instead of JSON: {content[:500]}")
                                raise Exception(
                                    f"AGI agent returned descriptive text instead of JSON data.\n"
                                    f"Content: {content[:300]}\n"
                                    f"Please refine the prompt to enforce JSON-only output."
                                )
                            else:
                                raise Exception(f"AGI returned unexpected type: {type(content)}")

                            # Return the content from DONE message
                            return content

                        elif message_type == "ERROR":
                            error = content.get("message", "Unknown error")
                            logger.error(f"✗ AGI task failed: {error}")
                            raise Exception(f"AGI task failed: {error}")

                        elif message_type == "QUESTION":
                            # Agent is asking a question - we need to respond
                            # For autonomous extraction, tell it to proceed without human input
                            logger.warning(f"⚠ AGI asked a question: {str(content)[:200]}")
                            logger.info("  → Telling agent to proceed autonomously")

                            # Send response telling agent to make assumptions and continue
                            response = await client.post(
                                f"{self.base_url}/sessions/{session_id}/message",
                                headers=self.headers,
                                json={
                                    "message": "Please proceed autonomously. Make reasonable assumptions based on available information. Do not ask for clarification."
                                }
                            )
                            response.raise_for_status()

                    # Idle detection: Check if we received new messages
                    current_time = time.time()

                    if messages:
                        # Reset idle timer - we got new messages
                        last_message_time = current_time
                        idle_check_start = None
                    else:
                        # No new messages - start or continue idle timer
                        if last_message_time is None:
                            # First poll, no messages yet - wait normally
                            last_message_time = current_time
                        elif idle_check_start is None:
                            # First time detecting no messages - start idle timer
                            idle_check_start = current_time
                        else:
                            # Check if idle timeout exceeded
                            idle_duration = current_time - idle_check_start
                            if idle_duration >= idle_timeout:
                                logger.warning(f"⚠ Session idle for {idle_duration:.0f}s (no new messages)")
                                logger.info(f"  → Canceling session {session_id} and extracting results...")

                                # Try to extract results from last messages before canceling
                                result = self._extract_result_from_messages(all_messages)

                                # Cancel the session
                                try:
                                    await self._close_session(session_id)
                                except Exception as e:
                                    logger.error(f"Failed to close idle session: {e}")

                                if result:
                                    logger.info(f"✓ Extracted results from idle session")
                                    return result
                                else:
                                    raise Exception(f"Session idle for {idle_duration:.0f}s with no extractable results")

                    # Still processing (poll every 2s per API docs recommendation)
                    await asyncio.sleep(2)

                except httpx.HTTPStatusError as e:
                    retry_count += 1

                    # Handle 502 Bad Gateway errors with retry
                    if e.response.status_code == 502:
                        if retry_count <= max_retries:
                            logger.warning(f"⚠ 502 Bad Gateway (attempt {retry_count}/{max_retries}), retrying in 5s...")
                            await asyncio.sleep(5)
                            continue
                        else:
                            logger.error(f"✗ 502 Bad Gateway after {max_retries} retries, giving up")
                            # Return partial results if we have any
                            if all_messages:
                                logger.info("  → Returning partial results from AGI")
                                return {
                                    "partial": True,
                                    "messages": all_messages,
                                    "error": "502 Bad Gateway after retries"
                                }
                            raise Exception(f"AGI API returned 502 Bad Gateway after {max_retries} retries")

                    # Handle 404 (session might not have messages yet)
                    elif e.response.status_code == 404:
                        await asyncio.sleep(2)

                    # Handle other HTTP errors
                    else:
                        logger.error(f"✗ HTTP {e.response.status_code}: {e}")
                        # Return partial results if we have any
                        if all_messages:
                            logger.info("  → Returning partial results from AGI")
                            return {
                                "partial": True,
                                "messages": all_messages,
                                "error": str(e)
                            }
                        raise

                except Exception as e:
                    # Handle other exceptions (network errors, etc.)
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.warning(f"⚠ Error: {e} (attempt {retry_count}/{max_retries}), retrying in 5s...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        # Return partial results if we have any
                        if all_messages:
                            logger.info("  → Returning partial results from AGI")
                            return {
                                "partial": True,
                                "messages": all_messages,
                                "error": str(e)
                            }
                        raise

    async def _capture_screenshot(self, session_id: str) -> bytes:
        """
        Capture a screenshot of the current browser state.

        Args:
            session_id: Active session ID

        Returns:
            Raw image bytes (JPEG format)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/sessions/{session_id}/screenshot",
                    headers=self.headers
                )
                response.raise_for_status()

                # Response is base64-encoded JPEG
                data = response.json()
                import base64

                # Fix base64 padding if needed
                screenshot_b64 = data["screenshot"]
                missing_padding = len(screenshot_b64) % 4
                if missing_padding:
                    screenshot_b64 += '=' * (4 - missing_padding)

                screenshot_bytes = base64.b64decode(screenshot_b64)
                logger.info(f"✓ Captured screenshot from session {session_id} ({len(screenshot_bytes)} bytes)")
                return screenshot_bytes

        except Exception as e:
            logger.error(f"✗ Screenshot capture failed: {e}")
            raise

    def _extract_result_from_messages(self, messages: list) -> Optional[Dict[str, Any]]:
        """
        Try to extract results from message history when session goes idle.
        Looks for JSON content in THOUGHT or QUESTION messages as fallback.

        Args:
            messages: All messages received from the session

        Returns:
            Extracted data dict or None if no valid data found
        """
        import re
        import json

        # Strategy 1: Look for the last THOUGHT message with JSON content
        for msg in reversed(messages):
            msg_type = msg.get("type", "")
            content = msg.get("content", {})

            if msg_type in ["THOUGHT", "QUESTION"] and isinstance(content, str):
                # Try to extract JSON from text
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            logger.info(f"Extracted JSON from {msg_type} message")
                            return parsed
                    except json.JSONDecodeError:
                        continue

        # Strategy 2: Look for any message with dict content
        for msg in reversed(messages):
            content = msg.get("content", {})
            if isinstance(content, dict) and len(content) > 0:
                logger.info(f"Using dict content from {msg.get('type', 'UNKNOWN')} message")
                return content

        logger.warning("No extractable JSON found in message history")
        return None

    async def _close_session(self, session_id: str):
        """
        Close an AGI session to free resources.

        Args:
            session_id: Session to close
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/sessions/{session_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                logger.info(f"✓ AGI session closed: {session_id}")
        except Exception as e:
            logger.warning(f"⚠ Failed to close session {session_id}: {e}")

    async def _extract_from_website(self, business_url: str) -> Dict[str, Any]:
        """
        Extract business data from official website in ONE session + capture screenshots.
        Returns: {business_name, industry, description, unique_selling_point, instagram_account, menu_info, location, screenshot_pages: []}
        """
        task_prompt = f"""
Visit {business_url} and extract business data in 3 minutes max.

**Extract from visible text only (visit homepage, about, menu, contact pages):**

Required fields:
- business_name: Company/restaurant name
- industry: Category (restaurant, retail, service, etc.)
- location: {{"street": "...", "city": "...", "state": "...", "zip": "...", "country": "..."}}
- description: 2-3 sentences about the business
- unique_selling_point: What makes this business special/different
- instagram_account: @username (search footer/contact/social links)
- menu_info: {{"categories": [...], "signature_items": [...]}} (key products/services)
- price_range: budget/moderate/premium (infer from context)
- brand_voice: elegant/casual/modern (infer from tone)

**Rules:**
- Return ONLY valid JSON (no explanations, no "Here is the data", just raw JSON)
- Proceed autonomously (no questions, make assumptions for unclear info)
- Skip unavailable fields rather than ask
- Visit 3-4 pages maximum
- Complete within 3 MINUTES

**JSON Example:**
{{
    "business_name": "Ozumo",
    "industry": "restaurant",
    "location": {{"street": "161 Stewart St", "city": "San Francisco", "state": "CA", "zip": "94105", "country": "USA"}},
    "description": "Contemporary Japanese restaurant featuring premium sushi and Kobe beef",
    "unique_selling_point": "Premium Kobe beef and fresh sushi in sophisticated atmosphere",
    "instagram_account": "@ozumosanfrancisco",
    "menu_info": {{"categories": ["sushi", "sashimi", "Kobe beef"], "signature_items": ["Omakase", "A5 Wagyu"]}},
    "price_range": "premium",
    "brand_voice": "elegant, sophisticated",
    "pages_visited": ["homepage", "about", "menu"]
}}

Finish when you have: business_name, industry, location (city+state min), description, instagram (if found).
Return JSON NOW within 3 MINUTES.
"""

        session_id = None
        screenshots = []
        try:
            session_id = await self._create_session()

            # Send extraction task
            result = await self._send_message(session_id, task_prompt, business_url)

            # Capture screenshot after extraction completes
            try:
                screenshot_bytes = await self._capture_screenshot(session_id)
                screenshots.append({
                    "page": "final_state",
                    "data": screenshot_bytes,
                    "size": len(screenshot_bytes)
                })
                logger.info(f"✓ Captured website screenshot ({len(screenshot_bytes)} bytes)")
            except Exception as e:
                logger.warning(f"⚠ Screenshot capture failed: {e}")

            return {
                "source": "website",
                "data": result,
                "screenshots": screenshots
            }
        finally:
            if session_id:
                await self._close_session(session_id)

    async def _extract_from_google_maps(self, business_name: str, city: str) -> Dict[str, Any]:
        """
        Extract Google Maps data + customer photos (3-5 photos max).
        Returns: {address, phone, rating, review_count, hours, customer_photos: [urls]}
        """
        task_prompt = f"""
Search Google Maps for "{business_name} {city}" and extract business data in 2 MINUTES MAX.

**Instructions:**
1. Search Google Maps for "{business_name} {city}"
2. Click on the business listing
3. Extract VISIBLE data ONLY from the listing page

**DO NOT click into Photos section or explore individual photos.**

**Extract these fields:**
- address: Full street address
- phone: Phone number
- google_rating: Star rating number
- review_count: Total review count number

**CRITICAL RULES:**
1. DO NOT browse photos or click Photos section
2. DO NOT explore beyond the main listing page
3. Extract data that is IMMEDIATELY visible only
4. Skip fields if not immediately visible (hours, photo descriptions)
5. Complete in 2 MINUTES MAXIMUM
6. Do NOT ask questions - return JSON immediately

**OUTPUT - JSON ONLY:**
Return ONLY this JSON format (no text before/after):
{{
    "address": "161 Stewart St, San Francisco, CA 94105",
    "phone": "(415) 882-1333",
    "google_rating": 4.4,
    "review_count": 1631
}}

**WHEN TO STOP:**
After extracting address, phone, rating, and review_count from listing page, IMMEDIATELY return JSON and STOP.
Do NOT explore photos. Do NOT scroll endlessly. Return JSON NOW.
"""

        session_id = None
        try:
            session_id = await self._create_session()
            result = await self._send_message(session_id, task_prompt)
            return {"source": "google_maps", "data": result}
        finally:
            if session_id:
                await self._close_session(session_id)

    async def _extract_from_instagram(self, instagram_handle: str) -> Dict[str, Any]:
        """
        Extract Instagram data from 3 recent posts (1-2 minutes max).
        User will handle CAPTCHA manually if needed.
        Returns: {follower_count, post_images: [descriptions], post_captions: [], engagement}
        """
        task_prompt = f"""
Navigate to instagram.com/{instagram_handle} and extract data in 1-2 minutes max.

**Extract from profile (3 most recent posts only):**

Required fields:
- follower_count: Follower number
- bio: Profile bio/description
- recent_posts: Array of 3 posts with:
  - image_description: What the image shows
  - caption: Caption text (first 50 chars)
  - likes: Like count
  - comments: Comment count
- captcha_encountered: true/false

**CAPTCHA Handling:**
If CAPTCHA appears, return: {{"captcha_encountered": true, "message": "CAPTCHA - user will handle"}}

**Rules:**
- Return ONLY valid JSON (no explanations, just raw JSON)
- Proceed autonomously (no questions)
- Look at 3 posts maximum
- Describe photos (don't extract URLs, we'll screenshot)
- Complete within 1-2 MINUTES

**JSON Examples:**

Success:
{{
    "follower_count": 6175,
    "bio": "Contemporary Japanese restaurant in San Francisco",
    "recent_posts": [
        {{"image_description": "sushi platter", "caption": "Fresh omakase...", "likes": 234, "comments": 12}},
        {{"image_description": "restaurant interior", "caption": "Happy hour 5-7pm", "likes": 189, "comments": 8}},
        {{"image_description": "wagyu beef", "caption": "A5 Wagyu Special", "likes": 312, "comments": 15}}
    ],
    "captcha_encountered": false
}}

CAPTCHA:
{{"captcha_encountered": true, "message": "CAPTCHA verification required - user will handle"}}

Finish when you have: follower_count, bio, 3 posts described, OR encountered CAPTCHA.
Return JSON NOW within 1-2 MINUTES.
"""

        session_id = None
        try:
            session_id = await self._create_session()
            result = await self._send_message(session_id, task_prompt)
            return {"source": "instagram", "data": result}
        except Exception as e:
            logger.error(f"✗ Instagram extraction failed: {e}")
            return {
                "source": "instagram",
                "data": {
                    "captcha_encountered": True,
                    "error": str(e),
                    "message": "Failed to extract Instagram data - user will handle manually"
                }
            }
        finally:
            if session_id:
                await self._close_session(session_id)

    async def extract_business_context(self, business_url: str) -> Dict[str, Any]:
        """
        SEQUENTIAL multi-source extraction - launches AGI sessions one at a time.

        To avoid AGI API rate limiting, we run sessions sequentially:
        Session 1: Website (data + screenshots)
        Session 2: Google Maps (data + customer photos) - uses business name from Session 1
        Session 3: Instagram (data + post images) - uses handle from Session 1

        Returns merged data from all sources including screenshot bytes.
        """
        logger.info("🔄 Launching SEQUENTIAL AGI sessions (one at a time to avoid rate limits)")

        # Quick pre-check: Extract business name and Instagram handle from URL/HTML
        business_name_hint = None
        instagram_handle = None
        try:
            import httpx
            import re
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(business_url)
                content = response.text

                # Extract business name from title tag
                title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
                if title_match:
                    business_name_hint = title_match.group(1).split('|')[0].split('-')[0].strip()
                    logger.info(f"💡 Pre-extracted business hint: {business_name_hint}")

                # Extract Instagram handle
                insta_match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', content)
                if insta_match:
                    instagram_handle = insta_match.group(1)
                    logger.info(f"📸 Found Instagram: @{instagram_handle}")
        except Exception as e:
            logger.warning(f"⚠ Pre-extraction failed: {e}")
            # Extract business name from URL domain as fallback
            import re
            domain_match = re.search(r'//(?:www\.)?([^/\.]+)', business_url)
            if domain_match:
                business_name_hint = domain_match.group(1).title()
                logger.info(f"💡 Using domain as hint: {business_name_hint}")

        # Run sessions SEQUENTIALLY (one at a time)
        results = []

        # Session 1: Website (try to extract, continue even if timeout/partial)
        logger.info("📄 Starting Session 1: Website extraction...")
        try:
            website_result = await self._extract_from_website(business_url)
            results.append(website_result)

            # Check if we got timeout/partial data
            if isinstance(website_result, dict) and website_result.get("timeout"):
                logger.warning(f"⚠ Session 1 timed out - continuing with partial data")
            else:
                logger.info("✓ Session 1 completed: Website")
        except Exception as e:
            logger.warning(f"⚠ Session 1 failed (continuing with defaults): {e}")
            # Add minimal result so campaign can continue
            results.append({"source": "website", "data": {}, "error": str(e)})

        # Session 2: Google Maps (OPTIONAL - failure is logged but extraction continues)
        if business_name_hint:
            logger.info("🗺️  Starting Session 2: Google Maps extraction...")
            try:
                maps_result = await self._extract_from_google_maps(business_name_hint, "")
                results.append(maps_result)
                logger.info("✓ Session 2 completed: Google Maps")
            except Exception as e:
                logger.warning(f"⚠ Session 2 failed (optional, continuing): {e}")
                results.append(e)

        # Session 3: Instagram (OPTIONAL - failure is logged but extraction continues)
        if instagram_handle:
            logger.info("📸 Starting Session 3: Instagram extraction...")
            try:
                insta_result = await self._extract_from_instagram(instagram_handle)
                results.append(insta_result)
                logger.info("✓ Session 3 completed: Instagram")
            except Exception as e:
                logger.warning(f"⚠ Session 3 failed (optional, continuing): {e}")
                results.append(e)

        logger.info(f"✓ All {len(results)} sequential sessions completed")

        # Extract data from each parallel result
        website_data = {}
        website_screenshots = []
        maps_data = {}
        insta_data = {}

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"⚠ One session failed: {result}")
                continue

            if isinstance(result, dict):
                source = result.get("source", "")
                if source == "website":
                    website_data = result.get("data", {})
                    website_screenshots = result.get("screenshots", [])
                    logger.info(f"✓ Website data: {website_data.get('business_name', 'N/A')}")
                elif source == "google_maps":
                    maps_data = result.get("data", {})
                    logger.info(f"✓ Maps data: {maps_data.get('google_rating', 'N/A')} rating")
                elif source == "instagram":
                    insta_data = result.get("data", {})
                    logger.info(f"✓ Instagram data: {insta_data.get('follower_count', 'N/A')} followers")

        # Merge all data sources
        merged_data = {
            "business_name": website_data.get("business_name", business_name_hint or "Unknown"),
            "industry": website_data.get("industry", "Unknown"),
            "location": website_data.get("location", {}),
            "description": website_data.get("description", ""),
            "price_range": website_data.get("price_range"),
            "specialties": website_data.get("specialties", []),
            "brand_voice": website_data.get("brand_voice"),
            "target_audience": website_data.get("target_audience"),
            "images": {
                "website": website_data.get("images", []),
                "google_maps": maps_data.get("customer_photos", []),
                "social_media": insta_data.get("post_images", [])
            },
            "screenshots": website_screenshots,
            "contact": {
                "address": maps_data.get("address", ""),
                "phone": maps_data.get("phone", ""),
                "google_rating": maps_data.get("google_rating", 0),
                "review_count": maps_data.get("review_count", 0)
            },
            "follower_count": insta_data.get("follower_count", 0)
        }

        screenshot_count = len(website_screenshots)
        website_images = len(merged_data['images'].get('website', []))
        maps_photos = len(merged_data['images'].get('google_maps', []))
        insta_images = len(merged_data['images'].get('social_media', []))
        logger.info(f"✅ TRUE PARALLEL extraction complete: {screenshot_count} screenshots, {website_images} website images, {maps_photos} Maps photos, {insta_images} Instagram images")

        return merged_data

    async def discover_competitors(
        self,
        business_context: Dict[str, Any],
        num_competitors: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Intelligently discover competitors based on business context.

        Returns:
        [
            {
                "name": "Akiko's Restaurant",
                "website": "https://akikos.com",
                "location": "San Francisco, CA",
                "google_rating": 4.5,
                "review_count": 1234,
                "social_handles": {"instagram": "@akikossf"},
                "similarity_score": 0.9
            }
        ]
        """
        business_name = business_context.get("business_name")
        industry = business_context.get("industry")
        location = business_context.get("location", {})
        city = location.get("city")

        # Build search query based on industry
        if industry == "restaurant":
            specialties = business_context.get("specialties", [])
            cuisine = specialties[0] if specialties else "cuisine"
            search_query = f"{cuisine} {industry} in {city}"
        else:
            search_query = f"{industry} in {city}"

        task_prompt = f"""
Search Google Maps for "{search_query}" and extract top {num_competitors} competitors in 2 MINUTES MAX.

**DO NOT visit individual websites. Extract data ONLY from Google Maps search results.**

For each competitor in search results, extract VISIBLE data ONLY:
- name: Business name
- location: City, State
- google_rating: Rating number
- review_count: Number of reviews

**CRITICAL RULES:**
1. DO NOT click on individual business listings
2. DO NOT visit competitor websites
3. Extract data ONLY from search results page
4. Complete in 2 MINUTES MAXIMUM

**OUTPUT - JSON ONLY:**
Return ONLY this JSON format (no text before/after):
{{
    "competitors": [
        {{"name": "Business Name", "location": "City, State", "google_rating": 4.5, "review_count": 1234}}
    ]
}}

**WHEN TO STOP:**
After seeing Google Maps search results with {num_competitors} competitors, IMMEDIATELY return JSON and STOP.
Do NOT explore further. Return JSON NOW.
"""

        session_id = None
        try:
            session_id = await self._create_session()
            result = await self._send_message(session_id, task_prompt)
            return result.get("competitors", [])

        except Exception as e:
            logger.error(f"✗ AGI competitor discovery failed: {e}")
            return []

        finally:
            if session_id:
                await self._close_session(session_id)

    async def research_competitor(
        self,
        competitor_url: str,
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Deep research on a single competitor.

        Returns:
        {
            "competitor_name": "Akiko's Restaurant",
            "menu": [{"item": "Omakase", "price": "$150"}],
            "pricing_strategy": "premium",
            "brand_voice": "elegant, traditional",
            "top_content_themes": ["behind-the-scenes", "seasonal ingredients"],
            "differentiators": ["20+ years experience"],
            "hero_images": ["https://..."]
        }
        """
        task_prompt = f"""
        Deep research on competitor: {competitor_name} ({competitor_url})

        Extract:
        1. Menu items with prices (or product catalog)
        2. Special promotions or offers
        3. Brand messaging and tone
        4. Key differentiators mentioned on website
        5. If social media linked:
           - Navigate to Instagram/Facebook profile
           - Identify 5 most recent post themes
        6. Screenshot/save hero images or key visuals

        **IMPORTANT RULES:**
        - Do NOT ask questions - proceed autonomously
        - Make reasonable assumptions if information is unclear
        - Skip unavailable data instead of asking for clarification

        **OUTPUT FORMAT - CRITICAL:**
        You MUST return ONLY raw JSON with NO additional text, explanations, or commentary.
        Do NOT write "Here is the research" or "I found" or any other text.
        Your ENTIRE response must be valid JSON starting with {{ and ending with }}.

        Example of CORRECT format:
        {{
            "competitor_name": "Akiko's Restaurant",
            "menu": [{{"item": "Omakase", "price": "$150"}}],
            "pricing_strategy": "premium",
            "brand_voice": "elegant, traditional",
            "top_content_themes": ["behind-the-scenes", "seasonal ingredients"],
            "differentiators": ["20+ years experience"],
            "hero_images": ["https://example.com/image.jpg"]
        }}

        Example of INCORRECT format (DO NOT DO THIS):
        I have completed the research on Akiko's Restaurant. Here is what I found: {{...}}

        **WHEN TO FINISH - CRITICAL:**
        Once you have extracted:
        - Basic menu/product information
        - Pricing strategy
        - Brand voice and key differentiators
        - A few hero images

        IMMEDIATELY return the JSON above and STOP.
        Do NOT exhaustively explore all pages or social media.
        Return the JSON NOW and complete the task.
        """

        session_id = None
        try:
            session_id = await self._create_session()
            result = await self._send_message(session_id, task_prompt, competitor_url)
            return result

        except Exception as e:
            logger.error(f"✗ AGI competitor research failed: {e}")
            return {}

        finally:
            if session_id:
                await self._close_session(session_id)

    async def scrape_online_reviews(
        self,
        business_name: str,
        location: Dict[str, str],
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape online reviews when GMB API unavailable (business not claimed).

        Fallback strategy for businesses without claimed Google My Business profile.

        Returns:
        {
            "reviews": [
                {"rating": 5, "text": "...", "date": "2025-01-15", "source": "Google Maps", "reviewer_name": "John D."}
            ],
            "customer_photos": ["https://maps.google.com/..."],
            "overall_rating": 4.5,
            "total_reviews": 234,
            "sources": ["Google Maps", "Yelp", "TripAdvisor"]
        }
        """
        city = location.get("city", "")
        state = location.get("state", "")

        task_prompt = f"""
        Search Google Maps for "{business_name} {city}" and extract reviews in 90 SECONDS MAX.

        **DO NOT visit Yelp, TripAdvisor, or other review sites. Extract data ONLY from Google Maps.**

        **Instructions:**
        1. Search Google Maps for "{business_name} {city}"
        2. Click on the business listing
        3. Extract overall_rating and total_reviews from the TOP of listing (no scrolling yet)
        4. Scroll down ONCE to see first 3-5 reviews
        5. Extract ONLY the first 3-5 visible reviews - DO NOT scroll further

        **CRITICAL RULES:**
        1. Extract MAXIMUM 5 reviews - DO NOT read more than 5
        2. DO NOT scroll through all reviews - get first 5 and STOP
        3. DO NOT visit Yelp or TripAdvisor
        4. DO NOT attempt to solve CAPTCHAs
        5. Complete in 90 SECONDS MAXIMUM
        6. Do NOT ask questions - return JSON immediately

        **OUTPUT - JSON ONLY:**
        Return ONLY this JSON format (no text before/after):
        {{
            "reviews": [
                {{"rating": 5, "text": "Great food", "reviewer_name": "John D."}},
                {{"rating": 4, "text": "Nice place", "reviewer_name": "Jane S."}}
            ],
            "customer_photos": [],
            "overall_rating": 4.5,
            "total_reviews": 234,
            "sources": ["Google Maps"]
        }}

        **WHEN TO STOP:**
        After extracting rating, review count, and FIRST 5 reviews, IMMEDIATELY return JSON and STOP.
        Do NOT scroll through all reviews. Do NOT read more than 5 reviews. Return JSON NOW.
        """

        session_id = None
        try:
            session_id = await self._create_session()
            # Hard 3-minute timeout for review scraping (agent tends to scroll through ALL reviews)
            result = await self._send_message(session_id, task_prompt, max_wait=180)

            # Ensure required keys exist
            return {
                "reviews": result.get("reviews", []),
                "customer_photos": result.get("customer_photos", []),
                "overall_rating": result.get("overall_rating", 0.0),
                "total_reviews": result.get("total_reviews", 0),
                "sources": result.get("sources", ["AGI Scraped"])
            }

        except Exception as e:
            logger.error(f"✗ AGI review scraping failed: {e}")
            return {
                "reviews": [],
                "customer_photos": [],
                "overall_rating": 0.0,
                "total_reviews": 0,
                "sources": []
            }

        finally:
            if session_id:
                await self._close_session(session_id)

    async def analyze_market_trends(
        self,
        business_context: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize market insights from competitors.

        Returns:
        {
            "trending_topics": ["sustainable seafood", "omakase experiences"],
            "market_gaps": ["late-night fusion", "vegetarian options"],
            "positioning_opportunities": ["Emphasize sustainability"]
        }
        """
        business_name = business_context.get("business_name")
        industry = business_context.get("industry")
        location = business_context.get("location", {})
        city = location.get("city")

        competitor_summary = "\n".join([
            f"- {c.get('name')}: {c.get('description', 'N/A')}"
            for c in competitors[:5]
        ])

        task_prompt = f"""
        Analyze the competitive landscape for {business_name} in {city}.

        Business: {business_name}
        Industry: {industry}
        Competitors:
        {competitor_summary}

        Research and synthesize:
        1. What's trending in {industry} in {city}?
        2. What are top competitors doing well?
        3. What gaps exist that no competitor is filling?
        4. What unique positioning opportunities exist for {business_name}?

        Use web search to supplement competitor data if needed.

        **IMPORTANT RULES:**
        - Do NOT ask questions - proceed autonomously
        - Make reasonable assumptions if information is unclear
        - Skip unavailable data instead of asking for clarification

        **OUTPUT FORMAT - CRITICAL:**
        You MUST return ONLY raw JSON with NO additional text, explanations, or commentary.
        Do NOT write "Here is my analysis" or "Based on my research" or any other text.
        Your ENTIRE response must be valid JSON starting with {{ and ending with }}.

        Example of CORRECT format:
        {{
            "trending_topics": ["sustainable seafood", "omakase experiences"],
            "market_gaps": ["late-night fusion", "vegetarian options"],
            "positioning_opportunities": ["Emphasize sustainability"]
        }}

        Example of INCORRECT format (DO NOT DO THIS):
        Based on my analysis of the competitive landscape, here are the insights: {{...}}

        **WHEN TO FINISH - CRITICAL:**
        Once you have identified:
        - 3-5 trending topics in the industry
        - 2-3 market gaps
        - 2-3 positioning opportunities

        IMMEDIATELY return the JSON above and STOP.
        Do NOT conduct exhaustive market research.
        Do NOT search for every possible trend.
        Return the JSON NOW and complete the task.
        """

        session_id = None
        try:
            session_id = await self._create_session()
            result = await self._send_message(session_id, task_prompt)
            return result

        except Exception as e:
            logger.error(f"✗ AGI market trends failed: {e}")
            return {
                "trending_topics": [],
                "market_gaps": [],
                "positioning_opportunities": []
            }

        finally:
            if session_id:
                await self._close_session(session_id)
