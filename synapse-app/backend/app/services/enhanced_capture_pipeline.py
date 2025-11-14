"""
Enhanced Capture Pipeline
Comprehensive processing: Scrape → Extract → Chunk → Embed → Store
"""

from typing import Dict, Any, List
import asyncio
import base64
import uuid
import os
from datetime import datetime

from .domain_extractors import DomainExtractor
from .content_chunker import get_chunker
from .content_analyzer import get_content_analyzer
from .embedding_service import get_embedding_service
from .qdrant_client import get_qdrant_client
from .supabase_client import get_supabase_client

# Playwright is optional - only import if enabled
USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "false").lower() == "true"
if USE_PLAYWRIGHT:
    from .content_scraper import get_scraper

class EnhancedCapturePipeline:
    """
    Complete capture pipeline for ANY webpage:
    1. Robust scraping with Playwright
    2. Platform-specific extraction
    3. Content chunking for long pages
    4. Multiple embeddings (one per chunk)
    5. Comprehensive storage
    """

    async def process_capture(
        self,
        url: str,
        title: str,
        html: str,  # From extension (fallback)
        screenshot_data: bytes,
        capture_id: str
    ) -> Dict[str, Any]:
        """
        Main processing pipeline

        Returns complete analysis + storage confirmation
        """
        print(f"\n{'='*70}")
        print(f"[CAPTURE] ENHANCED CAPTURE PIPELINE")
        print(f"{'='*70}")
        print(f"URL: {url[:60]}...")
        print(f"Capture ID: {capture_id}")

        # STEP 1: Process HTML and extract content
        # NOTE: Extension captures FULL HTML from user's browser (already rendered)
        # This is better than Playwright because:
        # - User's browser has already done the work
        # - No need for headless browser (faster, more reliable)
        # - Works with authenticated pages, cookies, etc.
        # Playwright is optional (set USE_PLAYWRIGHT=true) for special cases

        print(f"\n> Step 1: Processing HTML and extracting content...")
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)

        # Extract images
        images = []
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            }
            if img_data['src']:
                images.append(img_data)

        # Extract links
        links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href:
                links.append({
                    'url': href,
                    'text': link.get_text(strip=True)
                })

        scraped = {
            "url": url,
            "title": title,
            "html": html,
            "text_content": text_content,
            "main_content": text_content[:8000],  # First 8000 chars for analysis
            "metadata": {},
            "word_count": len(text_content.split()),
            "images": images,
            "links": links
        }

        print(f"  [OK] Processed {scraped['word_count']} words (FULL HTML from browser)")
        print(f"  [OK] Extracted {len(images)} images")
        print(f"  [OK] Extracted {len(links)} links")

        # STEP 2: Platform-specific extraction
        print(f"\n> Step 2: Platform-specific extraction...")
        platform_data = await DomainExtractor.extract(url, scraped)
        platform = platform_data.get('platform', 'web')
        print(f"  [OK] Detected platform: {platform}")
        if platform != 'web':
            print(f"  [OK] Extracted platform metadata: {len(platform_data)} fields")

        # STEP 3: LLM analysis (text + screenshot)
        print(f"\n> Step 3: AI analysis with Claude Sonnet 4...")
        analyzer = get_content_analyzer()
        analysis = await analyzer.analyze(
            url,
            scraped.get('title', title),
            scraped.get('main_content', html[:8000]),
            screenshot_data
        )
        print(f"  [OK] Content type: {analysis['content_type']}")
        print(f"  [OK] Tags: {', '.join(analysis['tags'][:5])}")
        print(f"  [OK] Generated summary")
        if analysis.get('visual_analysis'):
            print(f"  [OK] Visual analysis complete")

        # STEP 4: Content chunking
        print(f"\n> Step 4: Chunking long content...")
        chunker = get_chunker()
        chunks = chunker.chunk_content(
            scraped.get('main_content', ''),
            {
                "url": url,
                "title": scraped.get('title', title),
                "content_type": analysis['content_type']
            }
        )
        print(f"  [OK] Created {len(chunks)} chunks")

        # STEP 5: Generate embeddings (one per chunk + one for summary)
        print(f"\n> Step 5: Generating embeddings...")
        embedding_service = get_embedding_service()

        # Main embedding (summary + key points)
        main_embedding_text = embedding_service.prepare_text_for_embedding(analysis)
        main_embedding = await embedding_service.generate_embedding(main_embedding_text)
        print(f"  [OK] Generated main embedding")

        # Chunk embeddings
        chunk_embeddings = []
        if chunks:
            for chunk in chunks[:10]:  # Limit to first 10 chunks
                chunk_text = f"{chunk.get('heading', '')}\n\n{chunk['text']}"
                emb = await embedding_service.generate_embedding(chunk_text)
                chunk_embeddings.append({
                    "chunk_id": chunk['chunk_id'],
                    "embedding": emb,
                    "text": chunk_text
                })
            print(f"  [OK] Generated {len(chunk_embeddings)} chunk embeddings")

        # STEP 6: Parallel storage
        print(f"\n> Step 6: Storing in Qdrant + Supabase...")

        async def store_in_qdrant():
            """Store main embedding + chunk embeddings in Qdrant"""
            qdrant = get_qdrant_client()

            # Main document embedding
            created_at = datetime.utcnow()
            main_metadata = {
                "url": url,
                "title": scraped.get('title', title),
                "content_type": analysis['content_type'],
                "platform": platform,
                "tags": analysis['tags'],
                "summary": analysis['summary'],
                "key_points": analysis.get('key_points', []),
                "metadata": analysis['metadata'],
                "created_at_timestamp": created_at.timestamp(),  # Unix timestamp for date filtering
                "created_at": created_at.isoformat()  # ISO string for display
            }

            await qdrant.upsert_capture(capture_id, main_embedding, main_metadata)

            # Chunk embeddings (with chunk reference)
            for idx, chunk_emb in enumerate(chunk_embeddings):
                chunk_metadata = {
                    **main_metadata,
                    "chunk_id": chunk_emb['chunk_id'],
                    "is_chunk": True,
                    "parent_id": capture_id
                }
                # Generate a proper UUID for the chunk point
                chunk_point_id = str(uuid.uuid4())
                await qdrant.upsert_capture(
                    chunk_point_id,
                    chunk_emb['embedding'],
                    chunk_metadata
                )

            print(f"  [OK] Stored in Qdrant: 1 main + {len(chunk_embeddings)} chunks")

        async def store_in_supabase():
            """Store comprehensive data in Supabase"""
            supabase = get_supabase_client()
            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')

            # Main capture
            capture_data = {
                "id": capture_id,
                "url": url,
                "title": scraped.get('title', title),
                "screenshot": screenshot_base64,
                "created_at": datetime.utcnow().isoformat(),

                # Analysis results
                "content_type": analysis['content_type'],
                "summary": analysis['summary'],
                "tags": analysis['tags'],
                "metadata": analysis['metadata'],
                "key_points": analysis.get('key_points', []),
                "entities": analysis.get('entities', {}),

                # Comprehensive content
                "full_html": scraped.get('html', html),
                "full_text": scraped.get('text_content', ''),
                "main_content": scraped.get('main_content', ''),
                "word_count": scraped.get('word_count', 0),

                # Platform data
                "platform": platform,
                "platform_metadata": platform_data,

                # Structured data
                "structured_data": scraped.get('structured_data', []),
                "links": scraped.get('links', []),
                "images_data": scraped.get('images', []),

                # Visual analysis
                "visual_analysis": analysis.get('visual_analysis'),

                # Legacy fields (for compatibility)
                "html_excerpt": html[:5000],
                "clean_content": analysis['clean_content'][:2000]
            }

            supabase.table("captures").insert(capture_data).execute()

            # Store chunks
            if chunks:
                chunk_data = []
                for chunk in chunks:
                    chunk_data.append({
                        "capture_id": capture_id,
                        "chunk_index": chunk['chunk_id'],
                        "heading": chunk.get('heading', ''),
                        "chunk_text": chunk['text'],
                        "word_count": chunk.get('word_count', 0)
                    })

                if chunk_data:
                    supabase.table("capture_chunks").insert(chunk_data).execute()

            print(f"  [OK] Stored in Supabase: main + {len(chunks)} chunks")

        # Execute parallel storage
        await asyncio.gather(
            store_in_qdrant(),
            store_in_supabase()
        )

        print(f"\n{'='*70}")
        print(f"[COMPLETE] CAPTURE COMPLETE")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "capture_id": capture_id,
            "analysis": {
                "content_type": analysis['content_type'],
                "platform": platform,
                "tags": analysis['tags'],
                "summary": analysis['summary'],
                "word_count": scraped.get('word_count', 0),
                "chunks": len(chunks)
            }
        }

# Singleton
_pipeline = None

def get_capture_pipeline() -> EnhancedCapturePipeline:
    """Get or create pipeline singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = EnhancedCapturePipeline()
    return _pipeline
