# 🚀 Robust Content Capture System

## Overview

A **comprehensive capture pipeline** that can handle ANY web page type and enable detailed Q&A about captured content.

### What Makes It Robust?

1. **JavaScript Rendering** - Uses Playwright to render dynamic pages (Twitter, SPAs, etc.)
2. **Platform-Specific Extraction** - Custom extractors for YouTube, ArXiv, Twitter, LinkedIn, GitHub
3. **Content Chunking** - Splits long pages into searchable sections
4. **Multiple Embeddings** - One embedding per chunk for granular search
5. **Comprehensive Storage** - Full HTML, all text, structured data, platform metadata

---

## 📊 Capture Pipeline

```
Extension Capture (Alt+B)
    ↓
[Basic data: URL, Title, HTML snippet, Screenshot]
    ↓
════════════════════════════════════════════════════════════
    ENHANCED BACKEND PROCESSING
════════════════════════════════════════════════════════════
    ↓
STEP 1: Robust Scraping (Playwright)
    ├─ Render JavaScript pages
    ├─ Extract ALL text content
    ├─ Get full HTML
    ├─ Extract links & images
    ├─ Get structured data (JSON-LD)
    └─ Calculate word count
    ↓
STEP 2: Platform Detection & Extraction
    ├─ Detect: YouTube, Twitter, ArXiv, GitHub, etc.
    ├─ Extract platform-specific metadata
    │   ├─ YouTube: video_id, channel, duration
    │   ├─ Twitter: tweet_text, author, media
    │   ├─ ArXiv: paper_id, authors, abstract
    │   ├─ GitHub: owner, repo, stars
    │   └─ LinkedIn: profile, description
    └─ Fallback: Generic web extraction
    ↓
STEP 3: AI Analysis (Claude Sonnet 4)
    ├─ Text analysis: content type, metadata, tags
    ├─ Screenshot analysis: UI elements, colors, visible text
    └─ Generate summary & key points
    ↓
STEP 4: Content Chunking
    ├─ Detect if page is long (>1000 words)
    ├─ Split by sections/headings if possible
    ├─ Otherwise split by paragraphs
    ├─ Create overlapping chunks (800 words, 150 overlap)
    └─ Preserve context in each chunk
    ↓
STEP 5: Multiple Embeddings
    ├─ Main embedding (summary + key points)
    └─ Per-chunk embeddings (up to 10 chunks)
    ↓
STEP 6: Comprehensive Storage (PARALLEL)
    ├─ Qdrant: Main + chunk embeddings
    └─ Supabase: Full data + all chunks
    ↓
✅ COMPLETE - Ready for Q&A
```

---

## 🗄️ Enhanced Database Schema

### Main Captures Table

```sql
captures
├── id (UUID)
├── url (TEXT)
├── title (TEXT)
├── created_at (TIMESTAMPTZ)
│
├── screenshot (TEXT)
│
├── content_type (TEXT)          -- AI-detected type
├── summary (TEXT)
├── tags (TEXT[])
│
├── metadata (JSONB)             -- Type-specific metadata
├── key_points (TEXT[])
├── entities (JSONB)
│
├── full_html (TEXT)             -- 🆕 Complete HTML
├── full_text (TEXT)             -- 🆕 All extracted text
├── main_content (TEXT)          -- 🆕 Main article content
├── word_count (INTEGER)         -- 🆕 Total words
│
├── platform (TEXT)              -- 🆕 youtube|twitter|arxiv|web
├── platform_metadata (JSONB)    -- 🆕 Platform-specific fields
│
├── structured_data (JSONB)      -- 🆕 JSON-LD, microdata
├── links (JSONB)                -- 🆕 All extracted links
├── images_data (JSONB)          -- 🆕 All extracted images
│
└── visual_analysis (JSONB)      -- Screenshot analysis
```

### Chunks Table (NEW)

```sql
capture_chunks
├── id (UUID)
├── capture_id (UUID)            -- References captures.id
├── chunk_index (INTEGER)
│
├── heading (TEXT)               -- Section heading if exists
├── chunk_text (TEXT)            -- Chunk content (800 words)
├── word_count (INTEGER)
│
├── start_position (INTEGER)
├── end_position (INTEGER)
│
└── search_vector (TSVECTOR)     -- Full-text search
```

---

## 🔍 How This Enables Q&A

### Example: ArXiv Paper

**Captured:** https://arxiv.org/html/2402.13521v1

**What gets stored:**

```json
{
  "url": "https://arxiv.org/html/2402.13521v1",
  "title": "Paper Title",
  "platform": "arxiv",
  "word_count": 15000,

  "platform_metadata": {
    "paper_id": "2402.13521v1",
    "authors": ["Author 1", "Author 2"],
    "abstract": "Full abstract text...",
    "pdf_url": "https://arxiv.org/pdf/2402.13521v1.pdf"
  },

  "full_text": "Complete paper text (15,000 words)",
  "main_content": "Introduction\n\nBackground\n\nMethodology...",

  "chunks": [
    {"chunk_id": 0, "heading": "Introduction", "text": "..."},
    {"chunk_id": 1, "heading": "Related Work", "text": "..."},
    {"chunk_id": 2, "heading": "Methodology", "text": "..."},
    ...
  ]
}
```

**Embeddings in Qdrant:**
- Main embedding: Summary of entire paper
- Chunk 0 embedding: Introduction section
- Chunk 1 embedding: Related Work section
- Chunk 2 embedding: Methodology section
- etc.

**Questions you can ask:**

```
Q: "What methodology did this paper use?"
→ Searches chunks, finds Chunk 2 (Methodology)
→ Returns specific section with context

Q: "Who are the authors of the paper about X?"
→ Searches metadata, returns authors array

Q: "Show me the abstract"
→ Returns platform_metadata.abstract

Q: "What are the key findings?"
→ Searches key_points and conclusion chunks
```

---

## 🌐 Platform Support

### YouTube Videos

**Captured:**
```
url: https://www.youtube.com/watch?v=abc123
```

**Extracted:**
```json
{
  "platform": "youtube",
  "platform_metadata": {
    "video_id": "abc123",
    "embed_url": "https://www.youtube.com/embed/abc123",
    "channel": "Channel Name",
    "thumbnail": "https://...",
    "description": "Video description..."
  }
}
```

**Can answer:**
- "What's the YouTube video about?"
- "Who uploaded this video?"
- "Show me the thumbnail"

---

### Twitter/X Posts

**Captured:**
```
url: https://x.com/user/status/123
```

**Extracted:**
```json
{
  "platform": "twitter",
  "platform_metadata": {
    "tweet_text": "Full tweet content...",
    "author": "@username",
    "media": "https://pbs.twimg.com/..."
  }
}
```

**Can answer:**
- "What did the tweet say?"
- "Who posted this?"
- "Show me the attached media"

---

### Blog Articles (Long-form)

**Captured:**
```
url: https://amanda-wanders.com/best-beaches-on-praslin-seychelles/
```

**Extracted:**
```json
{
  "platform": "web",
  "word_count": 3500,
  "chunks": [
    {"heading": "Introduction", "text": "..."},
    {"heading": "Best Time to Visit", "text": "..."},
    {"heading": "Anse Lazio Beach", "text": "..."},
    {"heading": "Anse Georgette Beach", "text": "..."}
  ]
}
```

**Can answer:**
- "What's the best time to visit Praslin?"
  → Searches chunks, finds "Best Time to Visit" section
- "Tell me about Anse Lazio beach"
  → Returns specific beach section
- "List all beaches mentioned"
  → Searches all chunks for beach names

---

## 🧪 Testing with Sample Links

### Installation

```bash
cd synapse-app/backend

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (IMPORTANT!)
playwright install chromium
```

### Test Each Platform

```python
# Start backend
python -m uvicorn app.main:app --reload

# Then capture these URLs with Alt+B:

# 1. Travel blog (long content)
https://amanda-wanders.com/best-beaches-on-praslin-seychelles/

# 2. Technical blog (with code)
https://karpathy.bearblog.dev/vibe-coding-menugen/

# 3. News article
https://www.wired.com/story/ai-generated-medium-posts-content-moderation/

# 4. Documentation
https://moonshotai.github.io/Kimi-K2/thinking.html

# 5. Twitter post
https://x.com/MiniMax__AI/status/1985375617622454566

# 6. ArXiv paper
https://arxiv.org/html/2402.13521v1

# 7. YouTube video
https://www.youtube.com/watch?v=WJRf7dh5Zws

# 8. LinkedIn profile
https://www.linkedin.com/in/gergelyorosz/
```

### Expected Results

**For each capture, check:**

1. **Terminal logs show:**
   ```
   ✓ Scraped [X] words
   ✓ Detected platform: [youtube|arxiv|twitter|web]
   ✓ Created [N] chunks
   ✓ Generated [N+1] embeddings
   ✓ Stored in Qdrant: main + chunks
   ✓ Stored in Supabase: main + chunks
   ```

2. **Supabase shows:**
   - Full content in `captures` table
   - Chunks in `capture_chunks` table
   - Platform-specific metadata populated

3. **Qdrant shows:**
   - Multiple vectors per capture (main + chunks)

---

## 📊 Storage Comparison

### Before (Basic)
```
Capture: Wikipedia article (5,000 words)
Storage:
  - HTML excerpt: 5,000 chars
  - Summary: 200 words
  - 1 embedding
```

**Can answer:**
- General questions about the topic
- What is this page about?

**Cannot answer:**
- Specific details from section 5
- Quote the methodology section
- List all references

### After (Robust)
```
Capture: Same Wikipedia article (5,000 words)
Storage:
  - Full HTML: Complete
  - Full text: 5,000 words
  - Main content: Parsed article
  - Chunks: 6 sections
    - Introduction (500 words)
    - History (800 words)
    - Methodology (900 words)
    - etc.
  - 7 embeddings (1 main + 6 chunks)
```

**Can answer:**
- What's in the methodology section?
- Quote from the history section
- List all examples in section 3
- Compare section 2 and section 5
- Show me all references

---

## 🔎 Search Capabilities

### 1. Semantic Search (Qdrant)

```python
# Search across all captures
GET /api/search?q=best beaches in Seychelles

# Finds:
  - Main document (if matches summary)
  - Specific chunk about beaches
  - Returns with similarity score
```

### 2. Chunk-Level Search

```python
# Search within a specific capture's chunks
GET /api/capture/{id}/chunks/search?q=methodology

# Returns:
  - Chunk ID
  - Section heading
  - Relevant text
  - Position in document
```

### 3. Platform Filtering

```python
# Find all YouTube videos
GET /api/search?q=machine learning&platform=youtube

# Find all ArXiv papers
GET /api/search?q=neural networks&platform=arxiv
```

---

## 💡 Frontend Q&A Integration

### How Frontend Can Query

**1. Get Full Context:**
```javascript
// Get complete capture with all chunks
GET /api/capture/{id}?include_chunks=true

Response:
{
  "id": "...",
  "title": "...",
  "summary": "...",
  "platform": "arxiv",
  "platform_metadata": {...},
  "chunks": [
    {"heading": "Introduction", "text": "..."},
    {"heading": "Methods", "text": "..."}
  ]
}
```

**2. Ask Specific Questions:**
```javascript
// Send chunk text + question to Claude
POST /api/ask
{
  "capture_id": "abc-123",
  "question": "What methodology was used?"
}

Backend:
1. Find relevant chunks (semantic search)
2. Send chunks + question to Claude
3. Return answer with sources
```

**3. Mind Map with Details:**
```javascript
// Each node can show:
- Summary (from analysis)
- Platform badge (YouTube, ArXiv, etc.)
- Chunk count
- Word count
- Click to expand → show chunks as sub-nodes
```

---

## ✅ Benefits

### For Users

1. **Capture anything** - Works on any website
2. **Ask detailed questions** - Find specific information
3. **No data loss** - Complete content preserved
4. **Smart search** - Finds exact sections

### For Developers

1. **Rich metadata** - Platform-specific data
2. **Scalable** - Handles long documents
3. **Queryable** - SQL + Vector + Full-text search
4. **Extensible** - Easy to add new platforms

---

## 🚀 Ready to Use

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Update Supabase:**
   - Run updated `SUPABASE_SCHEMA.sql`

3. **Start backend:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Capture test links:**
   - Try all 12 sample links
   - Check Supabase for chunks
   - Verify Qdrant has multiple embeddings

5. **Build frontend with Q&A:**
   - Access full content
   - Search chunks
   - Answer any question about captured pages

---

**The robust capture system is ready to power comprehensive Q&A over ANY web content!** 🎉
