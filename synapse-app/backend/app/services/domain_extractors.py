"""
Domain-Specific Content Extractors
Specialized processing for YouTube, Twitter, ArXiv, LinkedIn, etc.
"""

from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

class DomainExtractor:
    """Extract platform-specific metadata and content"""

    @staticmethod
    def detect_platform(url: str) -> str:
        """Detect platform from URL"""
        domain = urlparse(url).netloc.lower()

        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'arxiv.org' in domain:
            return 'arxiv'
        elif 'linkedin.com' in domain:
            return 'linkedin'
        elif 'github.com' in domain:
            return 'github'
        elif 'medium.com' in domain:
            return 'medium'
        elif 'reddit.com' in domain:
            return 'reddit'
        else:
            return 'web'

    @staticmethod
    async def extract_youtube(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract YouTube video metadata"""
        url = scraped_data['url']
        soup = BeautifulSoup(scraped_data['html'], 'html.parser')

        # Extract video ID
        video_id = None
        if 'v=' in url:
            video_id = parse_qs(urlparse(url).query).get('v', [None])[0]
        elif 'youtu.be' in url:
            video_id = urlparse(url).path.split('/')[-1]

        # Extract metadata from Open Graph and meta tags
        metadata = scraped_data.get('metadata', {})

        return {
            'video_id': video_id,
            'embed_url': f'https://www.youtube.com/embed/{video_id}' if video_id else None,
            'thumbnail': metadata.get('og_image'),
            'channel': metadata.get('og_site_name', ''),
            'description': metadata.get('og_description', ''),
            'platform': 'youtube'
        }

    @staticmethod
    async def extract_twitter(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Twitter/X post metadata"""
        metadata = scraped_data.get('metadata', {})

        return {
            'tweet_text': scraped_data.get('main_content', ''),
            'author': metadata.get('twitter_creator', ''),
            'media': metadata.get('twitter_image'),
            'platform': 'twitter'
        }

    @staticmethod
    async def extract_arxiv(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ArXiv paper metadata"""
        soup = BeautifulSoup(scraped_data['html'], 'html.parser')

        # ArXiv has specific structure
        title_elem = soup.find('h1', class_='title')
        title = title_elem.get_text().replace('Title:', '').strip() if title_elem else ''

        authors_elem = soup.find('div', class_='authors')
        authors = []
        if authors_elem:
            author_tags = authors_elem.find_all('a')
            authors = [a.get_text().strip() for a in author_tags]

        abstract_elem = soup.find('blockquote', class_='abstract')
        abstract = abstract_elem.get_text().replace('Abstract:', '').strip() if abstract_elem else ''

        # Extract paper ID
        paper_id = re.search(r'arxiv.org/(?:abs|html)/([0-9.]+)', scraped_data['url'])
        paper_id = paper_id.group(1) if paper_id else ''

        return {
            'paper_id': paper_id,
            'authors': authors,
            'abstract': abstract,
            'pdf_url': f'https://arxiv.org/pdf/{paper_id}.pdf' if paper_id else None,
            'platform': 'arxiv'
        }

    @staticmethod
    async def extract_github(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GitHub repo metadata"""
        soup = BeautifulSoup(scraped_data['html'], 'html.parser')

        # Extract repo info
        repo_pattern = re.match(r'https://github.com/([^/]+)/([^/]+)', scraped_data['url'])
        owner = repo_pattern.group(1) if repo_pattern else ''
        repo = repo_pattern.group(2) if repo_pattern else ''

        # Stars, forks, etc. from meta tags
        metadata = scraped_data.get('metadata', {})

        return {
            'owner': owner,
            'repo': repo,
            'full_name': f'{owner}/{repo}',
            'description': metadata.get('og_description', ''),
            'platform': 'github'
        }

    @staticmethod
    async def extract_linkedin(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract LinkedIn profile/post metadata"""
        metadata = scraped_data.get('metadata', {})

        return {
            'profile_name': metadata.get('og_title', ''),
            'description': metadata.get('og_description', ''),
            'image': metadata.get('og_image', ''),
            'platform': 'linkedin'
        }

    @staticmethod
    async def extract(url: str, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main extraction dispatcher"""
        platform = DomainExtractor.detect_platform(url)

        extractors = {
            'youtube': DomainExtractor.extract_youtube,
            'twitter': DomainExtractor.extract_twitter,
            'arxiv': DomainExtractor.extract_arxiv,
            'github': DomainExtractor.extract_github,
            'linkedin': DomainExtractor.extract_linkedin
        }

        extractor = extractors.get(platform)
        if extractor:
            return await extractor(scraped_data)

        return {'platform': 'web'}
