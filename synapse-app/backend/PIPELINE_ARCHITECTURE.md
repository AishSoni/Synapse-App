# Synapse Backend Pipeline Architecture

## 🎯 Design Goals

1. **Single LLM Call** - All preprocessing in one API request (efficient)
2. **Parallel Execution** - Qdrant + Supabase storage simultaneously (fast)
3. **Smart Detection** - Automatically detect content types and extract metadata
4. **Rich Metadata** - Extract prices, authors, durations, ratings, etc.
5. **Flexible Search** - Vector search + filters + full-text

---

## 🏗️ Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chrome Extension (Alt+B)                      │
│  Captures: URL, Title, HTML Content, Screenshot                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (/api/capture)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: Content Analysis (Gemini Flash)             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Single LLM Call Extracts:                                │  │
│  │  • content_type (product/video/article/code/etc.)         │  │
│  │  • metadata (price, author, duration, rating, etc.)       │  │
│  │  • summary (1-2 sentences)                                │  │
│  │  • tags (AI-generated categories)                         │  │
│  │  • key_points (main takeaways)                            │  │
│  │  • entities (people, places, technologies)                │  │
│  │  • clean_content (stripped text)                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           STEP 2: Prepare Optimized Embedding Text               │
│  Combines: Summary + Key Points + Tags + Content Excerpt        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│             STEP 3: PARALLEL EXECUTION (async)                   │
│                                                                  │
│   ┌──────────────────────┐        ┌──────────────────────┐     │
│   │   Track A: Qdrant    │        │  Track B: Supabase   │     │
│   ├──────────────────────┤        ├──────────────────────┤     │
│   │ 1. Generate          │        │ 1. Structure data    │     │
│   │    embedding         │        │    for UI display    │     │
│   │    (768 dims)        │        │                      │     │
│   │                      │        │ 2. Include:          │     │
│   │ 2. Store vector +    │        │    • All metadata    │     │
│   │    metadata          │        │    • Tags            │     │
│   │                      │        │    • Screenshot      │     │
│   │ 3. Enable semantic   │        │    • Analysis        │     │
│   │    search            │        │                      │     │
│   └──────────────────────┘        └──────────────────────┘     │
│            │                                   │                 │
│            └───────────────┬───────────────────┘                │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Return Success + Analysis                      │
│         {content_type, tags, summary, capture_id}               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
synapse-app/backend/
├── app/
│   ├── main.py                     # API endpoints
│   └── services/
│       ├── content_analyzer.py     # 🆕 Smart LLM analysis
│       ├── embedding_service.py    # 🆕 Vector generation
│       ├── qdrant_client.py        # ✏️ Updated with filters
│       ├── supabase_client.py      # Database client
│       └── gemini_client.py        # (Old - not used anymore)
│
├── requirements.txt
├── .env.example
├── .env                            # Your API keys
│
├── SUPABASE_SCHEMA.sql            # 🆕 Database schema
├── BACKEND_SETUP.md               # 🆕 Setup guide
└── PIPELINE_ARCHITECTURE.md       # 🆕 This file
```

---

## 🔧 Key Components

### 1. Content Analyzer (`content_analyzer.py`)

**Purpose:** Single LLM call to extract everything

**Input:**
```python
url: "https://amazon.com/airpods"
title: "Apple AirPods Pro"
html: "<html>...</html>"
```

**Output:**
```python
{
    "content_type": "product",
    "metadata": {
        "price": "249.99",
        "currency": "USD",
        "brand": "Apple",
        "rating": "4.5",
        "availability": "In Stock"
    },
    "summary": "Apple AirPods Pro with active noise cancellation",
    "tags": ["electronics", "audio", "apple", "wireless"],
    "key_points": [
        "Active noise cancellation",
        "Transparency mode",
        "MagSafe charging case"
    ],
    "entities": {
        "technologies": ["Active Noise Cancellation", "Bluetooth"],
        "organizations": ["Apple"]
    },
    "clean_content": "Main product description text..."
}
```

**Features:**
- Detects 10+ content types automatically
- Extracts type-specific metadata
- Generates smart tags
- Fast (uses Gemini Flash, not Pro)
- Fallback if LLM fails

---

### 2. Embedding Service (`embedding_service.py`)

**Purpose:** Generate optimal embeddings for search

**Process:**
```python
# Combines multiple fields for best search results
embedding_text = f"""
Summary: {summary}

Key points: {key_points}

Tags: {tags}

Content: {excerpt}
"""

# Generate 768-dim vector
embedding = gemini.embed_content(embedding_text)
```

**Features:**
- Optimized text preparation
- Separate embeddings for queries vs documents
- 768 dimensions (Gemini standard)
- Fallback to zero vector if fails

---

### 3. Qdrant Service (`qdrant_client.py`)

**Purpose:** Vector storage and semantic search

**Storage:**
```python
{
    "id": "uuid",
    "vector": [0.123, 0.456, ...],  # 768 dims
    "payload": {
        "url": "...",
        "title": "...",
        "content_type": "product",
        "tags": [...],
        "summary": "...",
        "metadata": {...}
    }
}
```

**Search:**
```python
# Semantic search
results = qdrant.search(
    query_embedding,
    limit=20,
    filter={"content_type": "product"}  # Optional filter
)

# Returns: [{id, score, metadata}, ...]
```

**Features:**
- Cosine similarity search
- Optional filters (by content_type, tags, etc.)
- Supports Cloud or local Docker
- Auto-creates collection on startup

---

### 4. Supabase Schema

**Table:** `captures`

```sql
captures
├── id (UUID)
├── url (TEXT)
├── title (TEXT)
├── created_at (TIMESTAMPTZ)
├── screenshot (TEXT)           -- Base64
│
├── content_type (TEXT)         -- product|video|article|...
├── summary (TEXT)
├── tags (TEXT[])               -- Array of tags
│
├── metadata (JSONB)            -- Flexible metadata
│   ├── price, currency, brand  (products)
│   ├── duration, channel       (videos)
│   ├── author, read_time       (articles)
│   └── language, stars         (code)
│
├── key_points (TEXT[])
├── entities (JSONB)
│
├── html_excerpt (TEXT)
├── clean_content (TEXT)
└── search_vector (TSVECTOR)    -- Full-text search
```

**Indexes:**
- `created_at DESC` - Chronological listing
- `content_type` - Filter by type
- `tags` (GIN) - Tag search
- `metadata` (GIN) - JSON queries
- `search_vector` (GIN) - Full-text search

**View:** `mind_map_nodes`
- Pre-joins common metadata fields
- Optimized for UI display

---

## 🎨 Content Type Detection

The system automatically detects and handles:

| Type | Detection Signals | Extracted Metadata |
|------|------------------|-------------------|
| **product** | Price tags, "Add to cart", ratings | price, currency, brand, rating, availability |
| **video** | YouTube, Vimeo, video player | duration, channel, views, upload_date |
| **article** | Blog structure, author byline | author, published_date, read_time, source |
| **code** | GitHub, code snippets | language, repository, stars, last_commit |
| **recipe** | Ingredients, cooking instructions | cook_time, servings, difficulty |
| **documentation** | API docs, technical content | version, category, framework |
| **social** | Twitter, Reddit, forums | author, upvotes, comments |
| **news** | News sites, current events | source, published_date, category |
| **forum** | Discussion threads | topic, replies, last_activity |
| **other** | Fallback for unrecognized | Basic tags only |

---

## 🔍 Search Capabilities

### 1. Semantic Search (Qdrant)

```python
# Natural language queries
"cheap wireless headphones under $50"
"Python tutorials for beginners"
"recipes with chicken and rice"
```

**How it works:**
1. Query → embedding vector
2. Qdrant finds similar vectors
3. Returns ranked results by similarity

### 2. Filter Search

```python
# By content type
GET /api/search?q=laptop&content_type=product

# Future: By tags, date range, price range, etc.
```

### 3. Full-Text Search (Supabase)

```sql
-- Direct SQL queries
SELECT * FROM captures
WHERE search_vector @@ to_tsquery('machine & learning');
```

---

## ⚡ Performance Characteristics

### Latency Breakdown

```
Extension capture: ~50ms (user sees feedback)
    ↓
Backend processing:
├─ LLM Analysis:     ~2-3 seconds (Gemini Flash)
├─ Embedding gen:    ~1 second (Gemini Embedding)
└─ Parallel storage: ~200ms (both Qdrant + Supabase)
    ↓
Total: ~3-4 seconds
```

**User Experience:**
- Instant visual feedback (50ms)
- User continues browsing immediately
- Backend processes in background
- No perceived delay

### Optimization Techniques

1. **Parallel Execution**
   - Qdrant + Supabase storage simultaneously
   - Saves ~1 second vs sequential

2. **Gemini Flash vs Pro**
   - Flash is 2x faster
   - Good enough for metadata extraction
   - Pro only needed for complex analysis

3. **Content Limiting**
   - HTML trimmed to 8k chars for LLM
   - Clean content limited to 1k chars for embedding
   - Reduces token costs and latency

4. **Async Architecture**
   - Non-blocking I/O
   - Can handle multiple captures simultaneously

---

## 🧪 Testing Examples

### Test 1: Amazon Product

**Input:** https://amazon.com/product/B09X5

**Expected Output:**
```json
{
    "content_type": "product",
    "metadata": {
        "price": "29.99",
        "currency": "USD",
        "brand": "Anker",
        "rating": "4.6"
    },
    "tags": ["electronics", "charging", "usb-c"],
    "summary": "Anker USB-C charger with fast charging"
}
```

### Test 2: YouTube Video

**Input:** https://youtube.com/watch?v=abc123

**Expected Output:**
```json
{
    "content_type": "video",
    "metadata": {
        "duration": "15:23",
        "channel": "Fireship",
        "views": "500K"
    },
    "tags": ["programming", "tutorial", "javascript"],
    "summary": "JavaScript tutorial covering modern features"
}
```

### Test 3: Wikipedia Article

**Input:** https://wikipedia.org/wiki/Machine_Learning

**Expected Output:**
```json
{
    "content_type": "article",
    "metadata": {
        "source": "Wikipedia"
    },
    "tags": ["machine-learning", "ai", "reference"],
    "summary": "Overview of machine learning concepts and applications"
}
```

---

## 🎯 Success Criteria

Backend is working correctly if:

- ✅ All API keys configured
- ✅ Qdrant collection created
- ✅ Supabase table created
- ✅ LLM analysis returns structured JSON
- ✅ Content type detected correctly
- ✅ Metadata extracted for each type
- ✅ Tags are relevant and useful
- ✅ Embeddings generated (768 dims)
- ✅ Both Qdrant + Supabase show data
- ✅ Search returns relevant results
- ✅ Terminal shows "✓ Stored in Qdrant" and "✓ Stored in Supabase"

---

## 🚀 Next Steps

With the backend complete, you can now:

1. **Test extensively** - Try 10+ different websites
2. **Build Electron app** - UI to display the mind map
3. **Add more content types** - Recipes, tweets, etc.
4. **Improve metadata extraction** - Fine-tune prompts
5. **Add filtering** - By date, tags, price range
6. **Build mind map visualization** - React Flow or D3.js

---

**The intelligent backend pipeline is complete and ready!** 🎉
