"""
Content Chunking Service
Splits long content into searchable chunks for better retrieval
"""

from typing import List, Dict, Any
import re

class ContentChunker:
    """
    Chunk long content for:
    - Better semantic search (find specific sections)
    - Answer detailed questions
    - Handle pages with 10k+ words
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Args:
            chunk_size: Target words per chunk
            chunk_overlap: Words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_content(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split content into semantic chunks

        Returns list of:
        {
            "chunk_id": 0,
            "text": "chunk content...",
            "start_pos": 0,
            "end_pos": 1000,
            "word_count": 1000,
            "metadata": {...}  # Inherited from parent
        }
        """
        if not content or len(content.strip()) < 100:
            return []

        # First try to split by sections (headings)
        sections = self._split_by_sections(content)

        if len(sections) > 1:
            # Good sectioning exists
            chunks = self._chunk_sections(sections, metadata)
        else:
            # No clear sections, chunk by paragraphs
            chunks = self._chunk_by_paragraphs(content, metadata)

        return chunks

    def _split_by_sections(self, content: str) -> List[Dict[str, str]]:
        """Split content by markdown-style headings or HTML headers"""
        # Pattern for headings: ## Heading or <h2>Heading</h2>
        heading_pattern = r'(^#{1,6}\s+.+$|^.+\n[=-]+$)'

        sections = []
        current_section = {"heading": "", "content": ""}
        lines = content.split('\n')

        for line in lines:
            # Check if it's a heading
            if re.match(r'^#{1,6}\s+', line) or \
               (len(lines) > lines.index(line) + 1 and
                re.match(r'^[=-]+$', lines[lines.index(line) + 1])):
                # Save previous section
                if current_section["content"].strip():
                    sections.append(current_section)
                # Start new section
                current_section = {"heading": line.strip(), "content": ""}
            else:
                current_section["content"] += line + "\n"

        # Add last section
        if current_section["content"].strip():
            sections.append(current_section)

        return sections

    def _chunk_sections(self, sections: List[Dict], metadata: Dict) -> List[Dict]:
        """Chunk content that has clear sections"""
        chunks = []
        chunk_id = 0

        for section in sections:
            heading = section["heading"]
            content = section["content"]

            # If section is small enough, keep as one chunk
            word_count = len(content.split())

            if word_count <= self.chunk_size:
                chunks.append({
                    "chunk_id": chunk_id,
                    "heading": heading,
                    "text": content.strip(),
                    "word_count": word_count,
                    "metadata": metadata
                })
                chunk_id += 1
            else:
                # Split large section into multiple chunks
                section_chunks = self._split_large_section(content, heading, metadata, chunk_id)
                chunks.extend(section_chunks)
                chunk_id += len(section_chunks)

        return chunks

    def _split_large_section(self, content: str, heading: str, metadata: Dict, start_id: int) -> List[Dict]:
        """Split a large section into smaller chunks"""
        chunks = []
        paragraphs = content.split('\n\n')

        current_chunk = ""
        chunk_id = start_id

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if adding this paragraph exceeds chunk size
            potential_chunk = current_chunk + "\n\n" + para
            word_count = len(potential_chunk.split())

            if word_count > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "chunk_id": chunk_id,
                    "heading": heading,
                    "text": current_chunk.strip(),
                    "word_count": len(current_chunk.split()),
                    "metadata": metadata
                })
                chunk_id += 1

                # Start new chunk with overlap
                current_chunk = self._get_overlap(current_chunk) + para
            else:
                current_chunk = potential_chunk

        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "heading": heading,
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split()),
                "metadata": metadata
            })

        return chunks

    def _chunk_by_paragraphs(self, content: str, metadata: Dict) -> List[Dict]:
        """Chunk content by paragraphs when no clear sections"""
        chunks = []
        paragraphs = content.split('\n\n')

        current_chunk = ""
        chunk_id = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            potential_chunk = current_chunk + "\n\n" + para
            word_count = len(potential_chunk.split())

            if word_count > self.chunk_size and current_chunk:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": current_chunk.strip(),
                    "word_count": len(current_chunk.split()),
                    "metadata": metadata
                })
                chunk_id += 1
                current_chunk = self._get_overlap(current_chunk) + para
            else:
                current_chunk = potential_chunk

        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split()),
                "metadata": metadata
            })

        return chunks

    def _get_overlap(self, text: str) -> str:
        """Get last N words for overlap"""
        words = text.split()
        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
        return " ".join(overlap_words) + "\n\n"

# Singleton
_chunker = None

def get_chunker() -> ContentChunker:
    """Get or create chunker singleton"""
    global _chunker
    if _chunker is None:
        _chunker = ContentChunker(chunk_size=800, chunk_overlap=150)
    return _chunker
