"""
Smart Content Analyzer using Claude Sonnet 4
Analyzes captured content and extracts structured metadata in a SINGLE API call
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse
from .llm_client import get_llm_client

# Platform-specific patterns for accurate categorization
PLATFORM_PATTERNS = {
    # Video platforms
    'youtube.com': 'video',
    'youtu.be': 'video',
    'vimeo.com': 'video',
    'twitch.tv': 'video',
    'tiktok.com': 'video',

    # Code & developer
    'github.com': 'code',
    'gitlab.com': 'code',
    'bitbucket.org': 'code',
    'stackoverflow.com': 'forum',
    'stackexchange.com': 'forum',

    # E-commerce
    'amazon.com': 'product',
    'ebay.com': 'product',
    'etsy.com': 'product',
    'shopify.com': 'product',
    'aliexpress.com': 'product',

    # Social media
    'twitter.com': 'social',
    'x.com': 'social',
    'facebook.com': 'social',
    'instagram.com': 'social',
    'linkedin.com': 'social',
    'reddit.com': 'forum',

    # Research & academic
    'arxiv.org': 'research',
    'scholar.google.com': 'research',
    'researchgate.net': 'research',
    'nature.com': 'research',
    'sciencedirect.com': 'research',

    # News
    'nytimes.com': 'news',
    'cnn.com': 'news',
    'bbc.com': 'news',
    'reuters.com': 'news',
    'theguardian.com': 'news',

    # Blogs & articles
    'medium.com': 'article',
    'substack.com': 'article',
    'dev.to': 'article',
    'hashnode.dev': 'article',

    # Documentation
    'docs.python.org': 'documentation',
    'developer.mozilla.org': 'documentation',
    'docs.microsoft.com': 'documentation',
    'docs.npmjs.com': 'documentation',
    'kubernetes.io': 'documentation',

    # Reference / Wiki
    'wikipedia.org': 'article',
    'wikimedia.org': 'article',
    'wiki.archlinux.org': 'documentation',
}

class ContentAnalyzer:
    """
    Analyzes web content and extracts:
    - Content type (product, video, article, code, recipe, etc.)
    - Metadata (price, author, duration, ingredients, etc.)
    - Summary
    - Tags/categories
    - Cleaned content for embedding
    - Screenshot analysis (visual context)
    """

    def __init__(self):
        self.llm_client = get_llm_client()

    def _detect_platform_hint(self, url: str) -> Optional[str]:
        """
        Detect platform/content type from URL
        Returns content type hint or None
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]

            # Check exact match
            if domain in PLATFORM_PATTERNS:
                return PLATFORM_PATTERNS[domain]

            # Check if any pattern is in the domain
            for pattern, content_type in PLATFORM_PATTERNS.items():
                if pattern in domain:
                    return content_type

            return None
        except Exception as e:
            print(f"[Analyzer] Platform detection error: {e}")
            return None

    async def analyze(
        self,
        url: str,
        title: str,
        html_content: str,
        screenshot_data: bytes = None
    ) -> Dict[str, Any]:
        """
        Single LLM call to extract all metadata and structure

        Returns:
        {
            "content_type": "product" | "video" | "article" | "code" | "recipe" | "documentation" | "social" | "other",
            "metadata": {
                # Product
                "price": "29.99",
                "currency": "USD",
                "brand": "Apple",
                "rating": "4.5",

                # Video
                "duration": "12:34",
                "channel": "3Blue1Brown",
                "views": "1.2M",

                # Article
                "author": "John Doe",
                "published_date": "2024-01-15",
                "read_time": "5 min",

                # Code
                "language": "Python",
                "repository": "username/repo",
                "stars": "1.2k"
            },
            "summary": "Brief 1-2 sentence summary",
            "tags": ["machine-learning", "tutorial", "python"],
            "clean_content": "Main text content for embedding",
            "key_points": ["point 1", "point 2", "point 3"]
        }
        """

        try:
            # STEP 0: Detect platform from URL for better categorization
            platform_hint = self._detect_platform_hint(url)
            if platform_hint:
                print(f"[Analyzer] Platform detected from URL: {platform_hint} - USING DIRECTLY")

            # STEP 1: Analyze text content
            text_prompt = self._build_analysis_prompt(url, title, html_content, platform_hint)

            messages = [
                {
                    "role": "user",
                    "content": text_prompt
                }
            ]

            response = await self.llm_client.chat_completion(
                messages=messages,
                model="claude-sonnet-4-5-20250929",
                temperature=0.3,  # Lower for more consistent JSON
                max_tokens=2000
            )

            result = self._parse_response(response, platform_hint)

            # Override content_type with platform hint if detected
            if platform_hint:
                print(f"[Analyzer] Forcing content_type to platform hint: {platform_hint}")
                result['content_type'] = platform_hint

            # STEP 2: Analyze screenshot if provided
            if screenshot_data:
                try:
                    visual_analysis = await self._analyze_screenshot(screenshot_data, result['content_type'])
                    result['visual_analysis'] = visual_analysis

                    # Enhance metadata with visual insights
                    if visual_analysis.get('detected_elements'):
                        result.setdefault('visual_elements', []).extend(visual_analysis['detected_elements'])

                except Exception as e:
                    print(f"Screenshot analysis failed (non-critical): {e}")
                    result['visual_analysis'] = None

            # Add timestamp
            result['analyzed_at'] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            print(f"Error analyzing content: {e}")
            import traceback
            traceback.print_exc()
            # Return fallback analysis
            return self._fallback_analysis(url, title, html_content)

    def _build_analysis_prompt(self, url: str, title: str, html_content: str, platform_hint: Optional[str] = None) -> str:
        """Build comprehensive prompt for single-shot analysis"""

        # Limit content to avoid token limits
        content_preview = html_content[:8000]

        platform_context = ""
        if platform_hint:
            platform_context = f"\nPLATFORM HINT: Based on the URL, this appears to be a '{platform_hint}' page. Verify this with the content and adjust if needed."

        return f"""Analyze this web page and extract structured information. Return ONLY valid JSON.

URL: {url}
Title: {title}{platform_context}
Content Preview:
{content_preview}

Detect the content type and extract ALL relevant metadata. Be thorough.
IMPORTANT: The platform hint (if provided) is based on the URL domain. Use it as a strong suggestion but verify with the actual content.

Return JSON in this EXACT format:
{{
    "content_type": "product|video|article|code|recipe|documentation|social|forum|news|other",
    "metadata": {{
        // For PRODUCTS (Amazon, shopping sites):
        "price": "29.99",
        "currency": "USD",
        "brand": "Brand Name",
        "rating": "4.5",
        "availability": "In Stock",

        // For VIDEOS (YouTube, Vimeo):
        "duration": "12:34",
        "channel": "Channel Name",
        "views": "1.2M",
        "upload_date": "2024-01-15",

        // For ARTICLES/BLOGS:
        "author": "Author Name",
        "published_date": "2024-01-15",
        "read_time": "5 min",
        "source": "Website Name",

        // For CODE (GitHub, GitLab):
        "language": "Python",
        "repository": "username/repo",
        "stars": "1.2k",
        "last_commit": "2024-01-15",

        // For RECIPES:
        "cook_time": "30 min",
        "servings": "4",
        "difficulty": "Easy",

        // For DOCUMENTATION:
        "version": "2.0.0",
        "category": "API Reference"
    }},
    "summary": "1-2 sentence summary of the main content. Be concise and informative.",
    "tags": ["tag1", "tag2", "tag3"],
    "clean_content": "Main textual content stripped of navigation, ads, etc. Keep paragraphs.",
    "key_points": [
        "First key point or takeaway",
        "Second key point or takeaway",
        "Third key point or takeaway"
    ],
    "entities": {{
        "people": ["Name 1", "Name 2"],
        "organizations": ["Org 1"],
        "locations": ["Location 1"],
        "technologies": ["Tech 1", "Tech 2"]
    }}
}}

IMPORTANT:
- Only include metadata fields that are actually present on the page
- Be accurate with numbers (prices, dates, durations)
- Tags should be lowercase, hyphenated (e.g., "machine-learning")
- clean_content should be the main valuable text, 500-1000 words max
- Return ONLY the JSON, no markdown formatting, no extra text"""

    def _parse_response(self, response_text: str, platform_hint: Optional[str] = None) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]

            # Parse JSON
            result = json.loads(text.strip())

            # Validate required fields
            required = ['content_type', 'summary', 'tags', 'clean_content']
            for field in required:
                if field not in result:
                    result[field] = self._get_default_value(field, platform_hint)

            # Use platform hint as fallback for content_type if invalid
            if result['content_type'] == 'other' and platform_hint:
                print(f"[Analyzer] Using platform hint '{platform_hint}' as content_type")
                result['content_type'] = platform_hint

            # Ensure metadata exists
            if 'metadata' not in result:
                result['metadata'] = {}

            return result

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response_text[:500]}")
            raise

    def _fallback_analysis(self, url: str, title: str, html_content: str) -> Dict[str, Any]:
        """Return basic analysis if LLM fails"""
        return {
            'content_type': 'other',
            'metadata': {},
            'summary': title,
            'tags': self._extract_basic_tags(url, title),
            'clean_content': html_content[:1000],
            'key_points': [],
            'entities': {},
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def _extract_basic_tags(self, url: str, title: str) -> List[str]:
        """Extract basic tags from URL and title"""
        tags = []

        # Extract from URL
        if 'youtube.com' in url or 'youtu.be' in url:
            tags.append('video')
        elif 'github.com' in url:
            tags.append('code')
        elif 'amazon.com' in url or 'shop' in url:
            tags.append('product')
        elif 'wikipedia.org' in url:
            tags.append('reference')

        # Extract from title
        title_lower = title.lower()
        if 'tutorial' in title_lower:
            tags.append('tutorial')
        if 'guide' in title_lower:
            tags.append('guide')
        if 'recipe' in title_lower:
            tags.append('recipe')

        return tags if tags else ['article']

    async def _analyze_screenshot(self, screenshot_data: bytes, content_type: str) -> Dict[str, Any]:
        """
        Analyze screenshot for visual context using vision model

        Returns:
        {
            "description": "What's visible in the screenshot",
            "detected_elements": ["button", "image", "price tag"],
            "colors": ["blue", "white"],
            "ui_type": "e-commerce" | "article" | "video" | "dashboard"
        }
        """
        prompt = f"""Analyze this screenshot of a {content_type} page.

Extract visual information:
1. Main UI elements visible (buttons, images, text blocks, etc.)
2. Dominant colors/theme
3. UI type (e-commerce, article, video player, dashboard, etc.)
4. Any visible text snippets (prices, titles, labels)
5. Notable visual patterns or design elements

Return ONLY valid JSON:
{{
    "description": "Brief description of what's shown",
    "detected_elements": ["element1", "element2"],
    "colors": ["color1", "color2"],
    "ui_type": "type",
    "visible_text": ["text1", "text2"]
}}"""

        try:
            response = await self.llm_client.analyze_image(
                screenshot_data,
                prompt,
                model="claude-sonnet-4-5-20250929"
            )

            # Parse JSON response
            text = response.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]

            return json.loads(text.strip())

        except Exception as e:
            print(f"Visual analysis error: {e}")
            return {
                "description": "Unable to analyze screenshot",
                "detected_elements": [],
                "colors": [],
                "ui_type": "unknown"
            }

    def _get_default_value(self, field: str, platform_hint: Optional[str] = None) -> Any:
        """Get default value for missing field"""
        defaults = {
            'content_type': platform_hint or 'other',  # Use platform hint if available
            'summary': 'No summary available',
            'tags': [],
            'clean_content': '',
            'key_points': [],
            'entities': {}
        }
        return defaults.get(field, None)

# Singleton instance
_analyzer = None

def get_content_analyzer() -> ContentAnalyzer:
    """Get or create content analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ContentAnalyzer()
    return _analyzer
