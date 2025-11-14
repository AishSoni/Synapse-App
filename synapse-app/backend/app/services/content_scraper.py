"""
Robust Content Scraper
Handles JavaScript-rendered pages, extracts comprehensive content
"""

import sys
import asyncio

# Fix for Playwright on Windows - MUST be set before importing playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.async_api import async_playwright, Page
from typing import Dict, Any, Optional, List
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class ContentScraper:
    """
    Comprehensive web scraper that:
    - Renders JavaScript pages
    - Extracts structured content
    - Handles different content types
    - Gets full page content (not just excerpts)
    """

    def __init__(self):
        self.playwright = None
        self.browser = None

    async def initialize(self):
        """Initialize Playwright browser"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)

    async def close(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape comprehensive content from URL

        Returns:
        {
            "url": "...",
            "title": "...",
            "html": "Full HTML",
            "text_content": "Full extracted text",
            "main_content": "Main article/content",
            "metadata": {
                "description": "...",
                "author": "...",
                "published_date": "...",
                "og_image": "...",
                ...
            },
            "links": [...],
            "images": [...],
            "scripts": [...],
            "word_count": 1234
        }
        """
        await self.initialize()

        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            # Navigate and wait for page to load
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait a bit more for dynamic content
            await page.wait_for_timeout(2000)

            # Get comprehensive data
            result = await self._extract_all_content(page, url)

            return result

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            # Return basic structure with error
            return {
                "url": url,
                "title": "",
                "html": "",
                "text_content": "",
                "main_content": "",
                "metadata": {},
                "error": str(e)
            }

        finally:
            await context.close()

    async def _extract_all_content(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract comprehensive content from page"""

        # Get basic page data
        title = await page.title()
        html = await page.content()

        # Parse with BeautifulSoup for better extraction
        soup = BeautifulSoup(html, 'html.parser')

        # Extract metadata
        metadata = self._extract_metadata(soup)

        # Extract main content
        main_content = self._extract_main_content(soup)

        # Extract all text
        text_content = self._extract_all_text(soup)

        # Extract links and images
        links = await self._extract_links(page)
        images = await self._extract_images(page)

        # Extract structured data (JSON-LD, microdata)
        structured_data = await self._extract_structured_data(page)

        # Calculate word count
        word_count = len(text_content.split())

        return {
            "url": url,
            "title": title,
            "html": html,  # Full HTML for reference
            "text_content": text_content,  # All text
            "main_content": main_content,  # Main article content
            "metadata": metadata,
            "structured_data": structured_data,
            "links": links[:50],  # Limit to first 50
            "images": images[:20],  # Limit to first 20
            "word_count": word_count,
            "domain": urlparse(url).netloc
        }

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meta tags and Open Graph data"""
        metadata = {}

        # Meta description
        desc = soup.find("meta", {"name": "description"})
        if desc:
            metadata["description"] = desc.get("content", "")

        # Author
        author = soup.find("meta", {"name": "author"})
        if author:
            metadata["author"] = author.get("content", "")

        # Published date
        date_meta = soup.find("meta", {"property": "article:published_time"}) or \
                    soup.find("meta", {"name": "publish_date"})
        if date_meta:
            metadata["published_date"] = date_meta.get("content", "")

        # Open Graph data
        og_tags = soup.find_all("meta", property=re.compile("^og:"))
        for tag in og_tags:
            prop = tag.get("property", "").replace("og:", "")
            metadata[f"og_{prop}"] = tag.get("content", "")

        # Twitter card
        twitter_tags = soup.find_all("meta", attrs={"name": re.compile("^twitter:")})
        for tag in twitter_tags:
            prop = tag.get("name", "").replace("twitter:", "")
            metadata[f"twitter_{prop}"] = tag.get("content", "")

        return metadata

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main article content using heuristics
        Tries multiple selectors for different sites
        """
        # Common article selectors
        selectors = [
            "article",
            "main",
            "[role='main']",
            ".post-content",
            ".article-content",
            ".entry-content",
            "#content",
            ".content",
            ".blog-post",
            ".post-body"
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Remove script and style tags
                for tag in element.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                    tag.decompose()

                text = element.get_text(separator="\n", strip=True)
                if len(text) > 200:  # Meaningful content
                    return text

        # Fallback: get body text
        body = soup.find("body")
        if body:
            for tag in body.find_all(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                tag.decompose()
            return body.get_text(separator="\n", strip=True)

        return ""

    def _extract_all_text(self, soup: BeautifulSoup) -> str:
        """Extract all readable text from page"""
        # Remove script, style, and navigation elements
        for tag in soup.find_all(['script', 'style', 'nav', 'footer']):
            tag.decompose()

        return soup.get_text(separator="\n", strip=True)

    async def _extract_links(self, page: Page) -> List[Dict[str, str]]:
        """Extract all links from page"""
        links = await page.evaluate('''() => {
            const anchors = Array.from(document.querySelectorAll('a[href]'));
            return anchors.map(a => ({
                url: a.href,
                text: a.innerText.trim().substring(0, 100)
            })).filter(l => l.url && l.text);
        }''')
        return links

    async def _extract_images(self, page: Page) -> List[Dict[str, str]]:
        """Extract all images from page"""
        images = await page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('img[src]'));
            return imgs.map(img => ({
                src: img.src,
                alt: img.alt || '',
                width: img.naturalWidth,
                height: img.naturalHeight
            })).filter(i => i.width > 100 && i.height > 100);
        }''')
        return images

    async def _extract_structured_data(self, page: Page) -> List[Dict]:
        """Extract JSON-LD and microdata"""
        structured = await page.evaluate('''() => {
            const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
            return scripts.map(s => {
                try {
                    return JSON.parse(s.textContent);
                } catch(e) {
                    return null;
                }
            }).filter(Boolean);
        }''')
        return structured

# Singleton instance
_scraper = None

async def get_scraper() -> ContentScraper:
    """Get or create scraper singleton"""
    global _scraper
    if _scraper is None:
        _scraper = ContentScraper()
        await _scraper.initialize()
    return _scraper
