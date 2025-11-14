# Synapse Backend Setup Guide

## 🎯 Overview

The Synapse backend is an intelligent processing pipeline that:

1. **Analyzes** captured content using Gemini (single LLM call)
2. **Extracts** structured metadata (prices, authors, tags, etc.)
3. **Stores** in parallel:
   - **Qdrant** → Vector embeddings for semantic search
   - **Supabase** → Structured data for UI display

---

## 📋 Prerequisites

You'll need accounts and API keys for:

1. **Google Gemini** (AI analysis & embeddings) - FREE
2. **Supabase** (PostgreSQL database) - FREE
3. **Qdrant** (Vector database) - FREE or Docker

---

## 🚀 Quick Setup (15 minutes)

### Step 1: Get API Keys

#### Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### Supabase
1. Go to: https://supabase.com
2. Create account + new project
3. Wait ~2 minutes for project setup
4. Go to **Settings → API**
5. Copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

#### Qdrant (Choose ONE option)

**Option A: Qdrant Cloud (Recommended)**
1. Go to: https://cloud.qdrant.io
2. Create free account
3. Create cluster (free tier: 1GB)
4. Copy **Cluster URL** and **API Key**

**Option B: Local Docker**
```bash
docker run -p 6333:6333 qdrant/qdrant
# URL: http://localhost:6333
# No API key needed
```

---

### Step 2: Create Supabase Database

1. Open your Supabase project
2. Go to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy the entire contents of `SUPABASE_SCHEMA.sql`
5. Paste and click **Run**
6. You should see: "Success. No rows returned"

**Verify:**
- Go to **Table Editor**
- You should see `captures` table
- Columns: id, url, title, content_type, tags, metadata, etc.

---

### Step 3: Configure Backend

```bash
cd E:\Appointy_Task_1\synapse-app\backend
```

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```env
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxxxxxxxxxxxx

# Qdrant (Cloud OR Local)
# For Qdrant Cloud:
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# For Local Docker:
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=  (leave empty)
```

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Should install:
- fastapi
- uvicorn
- supabase-py
- qdrant-client
- google-generativeai
- python-multipart
- python-dotenv

---

### Step 5: Test the Backend

```bash
python -m uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
✓ Connected to Qdrant Cloud: https://xxxxx.qdrant.io
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test in browser:**
- http://localhost:8000 → Should show: `{"message":"Synapse API is running"}`
- http://localhost:8000/docs → Should show API documentation

---

## 🧪 Test the Full Pipeline

### 1. Use the Extension

With backend running:
1. Open Chrome
2. Navigate to a product page (e.g., Amazon)
3. Press **Alt+B**
4. Check terminal logs

**You should see:**
```
============================================================
Processing capture: Apple AirPods Pro...
============================================================
→ Analyzing content with Gemini...
  ✓ Content type: product
  ✓ Tags: electronics, audio, apple
  ✓ Metadata: 4 fields
→ Storing in parallel (Qdrant + Supabase)...
  ✓ Stored in Qdrant
  ✓ Stored in Supabase
============================================================
✓ Capture complete: abc123...
============================================================
```

### 2. Test with cURL

```bash
# Check captures
curl http://localhost:8000/api/captures

# Test search
curl "http://localhost:8000/api/search?q=apple+products"

# Filter by content type
curl "http://localhost:8000/api/search?q=headphones&content_type=product"
```

### 3. Check Supabase

1. Open Supabase → Table Editor → captures
2. You should see your captured data
3. Expand the `metadata` column → Should show extracted data (price, brand, etc.)
4. Check `tags` column → Should show AI-generated tags

### 4. Test Different Content Types

Capture various pages to test detection:

**Product (Amazon):**
```
Content type: product
Metadata: price, brand, rating, availability
```

**Video (YouTube):**
```
Content type: video
Metadata: duration, channel, views, upload_date
```

**Article (Medium/Blog):**
```
Content type: article
Metadata: author, read_time, published_date
```

**Code (GitHub):**
```
Content type: code
Metadata: language, repository, stars
```

---

## 📊 Architecture Flow

```
Extension Capture (Alt+B)
    ↓
Backend receives: URL, Title, HTML, Screenshot
    ↓
[STEP 1] Gemini Analysis (SINGLE API CALL)
    ├─ Detect content type
    ├─ Extract metadata (price, author, etc.)
    ├─ Generate summary
    ├─ Assign tags
    └─ Clean content
    ↓
[STEP 2] Prepare for storage
    ├─ Create embedding text
    └─ Structure data
    ↓
[STEP 3] PARALLEL EXECUTION
    ├─ Track A: Qdrant
    │   ├─ Generate vector embedding
    │   └─ Store with metadata
    │
    └─ Track B: Supabase
        └─ Store structured data + tags
    ↓
Return success to extension
```

---

## 🔍 Querying Your Data

### Supabase Queries

```sql
-- Get all products
SELECT * FROM captures WHERE content_type = 'product';

-- Get expensive products
SELECT * FROM captures
WHERE content_type = 'product'
  AND (metadata->>'price')::numeric > 100;

-- Get recent videos
SELECT * FROM captures
WHERE content_type = 'video'
ORDER BY created_at DESC
LIMIT 10;

-- Search by tag
SELECT * FROM captures WHERE 'python' = ANY(tags);

-- Get captures from last week
SELECT * FROM captures
WHERE created_at >= NOW() - INTERVAL '7 days';

-- Count by content type
SELECT content_type, COUNT(*)
FROM captures
GROUP BY content_type;
```

### API Queries

```bash
# Semantic search
curl "http://localhost:8000/api/search?q=machine+learning+tutorials"

# Filter by type
curl "http://localhost:8000/api/search?q=laptop&content_type=product"

# Get recent captures
curl "http://localhost:8000/api/captures?limit=10"

# Get specific capture
curl "http://localhost:8000/api/capture/{id}"
```

---

## 🐛 Troubleshooting

### Gemini API errors

**Error:** "API key not valid"
- Check `.env` file has correct `GEMINI_API_KEY`
- Verify key at https://makersuite.google.com/app/apikey

**Error:** "Resource exhausted"
- You hit the free tier limit
- Wait 1 minute and try again
- Or upgrade to paid tier

### Supabase errors

**Error:** "relation 'captures' does not exist"
- Run `SUPABASE_SCHEMA.sql` in SQL Editor
- Verify table was created in Table Editor

**Error:** "Invalid API key"
- Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Make sure you copied the **anon/public** key, not service_role

### Qdrant errors

**Error:** "Connection refused"
- If using Docker: Make sure `docker run -p 6333:6333 qdrant/qdrant` is running
- If using Cloud: Check `QDRANT_URL` is correct

**Error:** "Unauthorized"
- Check `QDRANT_API_KEY` matches your cluster
- If using local Docker, remove the API key from `.env`

### Analysis failures

**Error:** "Failed to parse JSON from LLM"
- This is rare - the LLM response was malformed
- The system will use fallback analysis
- Check logs for the raw response

---

## 📈 Performance

**Expected timings:**
- LLM Analysis: ~2-3 seconds
- Embedding generation: ~1 second
- Qdrant storage: ~100ms
- Supabase storage: ~200ms
- **Total: ~3-4 seconds per capture**

**Optimization tips:**
- Parallel execution saves ~1 second
- Gemini Flash is 2x faster than Pro (we use Flash)
- Caching embeddings can help repeated content

---

## 🔐 Security

**API Keys:**
- Never commit `.env` file to git
- `.env` is already in `.gitignore`
- Use environment variables in production

**Supabase RLS (Row Level Security):**
- Currently disabled for development
- Enable RLS for multi-user production
- Add auth policies per user

---

## ✅ Backend is Ready!

Once you see successful captures with all metadata extracted, you're ready to build the Electron app!

**Next steps:**
1. Test on 5-10 different types of pages
2. Verify all content types are detected correctly
3. Check that metadata extraction works
4. Move on to building the mind map UI!

---

**Need help?** Check logs in the terminal for detailed error messages.
