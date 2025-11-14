# Synapse - Your Second Brain

Complete setup guide for the Synapse second brain application.

## 🎯 What is Synapse?

Synapse is your AI-powered second brain that:
- **Captures web pages** instantly with Alt+B keyboard shortcut
- **Stores AI conversations** from Claude, ChatGPT, and other AI apps
- **Semantic search** across all your captured content
- **Platform-aware** extraction (YouTube, Twitter, GitHub, ArXiv, etc.)
- **Full-text embeddings** for intelligent Q&A

## 📦 Components

### 1. Chrome Extension
- Instant capture with **Alt+B** shortcut
- Full HTML extraction from your browser
- Screenshots for visual analysis
- Zero configuration needed

### 2. Backend Server
- FastAPI server processing captures
- AI analysis with Claude Sonnet 4.5
- Embeddings with Gemini (3072 dimensions)
- Storage in Qdrant (vectors) + Supabase (structured data)

### 3. MCP Server
- Stores AI chat conversations
- Integrates with Claude Desktop and other MCP clients
- Semantic search across all conversations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Qdrant (local or cloud)
- Supabase account
- Chrome browser

### Step 1: Clone and Install

```bash
cd E:\Appointy_Task_1\synapse-app\backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file in `backend/` directory:

```env
# LiteLLM Proxy (Claude + Gemini)
BASE_URL=https://litellm-339960399182.us-central1.run.app
AUTH_TOKEN=sk-BoUYHwNqVVeYotBVVWnw2w

# Supabase (PostgreSQL Database)
SUPABASE_URL=https://tdwcvgfqqxrwrkbfelqg.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Qdrant (Vector Database)
QDRANT_URL=http://127.0.0.1:6333
QDRANT_API_KEY=

# Optional Features
USE_PLAYWRIGHT=false
```

### Step 3: Setup Databases

#### Supabase Tables

Go to Supabase SQL Editor and run:

**For web captures:**
```sql
-- See backend/app/models/supabase_schema.sql for full schema
-- Create captures table, capture_chunks table, etc.
```

**For chat records:**
```sql
-- Run: backend/migrations/create_chat_records_table.sql
CREATE TABLE chat_records (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_app TEXT DEFAULT 'Unknown',
    content_type TEXT DEFAULT 'chat',
    tags TEXT[] DEFAULT '{}',
    word_count INTEGER DEFAULT 0,
    text_preview TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Qdrant Setup

**Option A: Local Qdrant (Docker)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option B: Qdrant Cloud**
1. Sign up at https://cloud.qdrant.io
2. Create a cluster
3. Update `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

### Step 4: Start Backend Server

```bash
cd synapse-app/backend
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Install Chrome Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select `E:\Appointy_Task_1\synapse-extension`
6. Extension installed! Icon appears in toolbar

### Step 6: Test Capture

1. Visit any webpage (e.g., Wikipedia article)
2. Press **Alt+B**
3. See flash animation + "Captured!" toast
4. Check backend logs for processing pipeline

## 🔧 MCP Server Setup (Optional)

Store AI conversations from Claude Desktop or other MCP clients.

### Step 1: Create Supabase Table

```bash
cd synapse-app/backend
python create_chat_table.py
```

Or run SQL manually from `migrations/create_chat_records_table.sql`.

### Step 2: Configure Claude Desktop

Edit config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "synapse-chat-storage": {
      "command": "python",
      "args": [
        "E:\\Appointy_Task_1\\synapse-app\\backend\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "E:\\Appointy_Task_1\\synapse-app\\backend"
      }
    }
  }
}
```

### Step 3: Use in Claude Desktop

Restart Claude Desktop, then say:

> "Please store this conversation using the store_chat tool. Title: 'Python Best Practices', Summary: 'Discussion about Python code quality and patterns', Tags: ['python', 'programming']"

## 📊 API Endpoints

### Capture Web Page
```bash
POST /api/capture
Content-Type: multipart/form-data

Fields:
- url: Page URL
- title: Page title
- html: Full HTML
- screenshot: Screenshot file
```

### Search Captures
```bash
GET /api/search?q=python+async&limit=20

Response: Array of matching captures with similarity scores
```

### Get All Captures
```bash
GET /api/captures?limit=50

Response: Recent captures sorted by date
```

### Get Single Capture
```bash
GET /api/capture/{capture_id}

Response: Full capture details
```

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/api/health
```

### Test MCP Server
```bash
cd synapse-app/backend
python test_mcp.py
```

### Test Capture Pipeline
1. Start backend server
2. Install extension
3. Press Alt+B on any webpage
4. Check backend logs for pipeline output

## 🏗️ Architecture

```
┌─────────────────────┐
│  Chrome Extension   │ (Alt+B keyboard shortcut)
└──────────┬──────────┘
           │ POST /api/capture
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
├─────────────────────┤
│ 1. HTML Processing  │ ← BeautifulSoup
│ 2. Platform Extract │ ← YouTube, Twitter, etc.
│ 3. AI Analysis      │ ← Claude Sonnet 4.5
│ 4. Chunking         │ ← 800 word chunks
│ 5. Embeddings       │ ← Gemini (3072 dims)
│ 6. Storage          │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌──────────┐
│ Qdrant  │ │ Supabase │
│ (Vector)│ │ (SQL)    │
└─────────┘ └──────────┘

┌─────────────────────┐
│   MCP Server        │ (Separate process)
├─────────────────────┤
│ AI Chat Storage     │
│ - Embeddings        │ → Qdrant
│ - Summaries         │ → Supabase
└─────────────────────┘
```

## 📁 Project Structure

```
synapse-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── services/
│   │   │   ├── llm_client.py           # Claude API
│   │   │   ├── qdrant_client.py        # Vector DB
│   │   │   ├── supabase_client.py      # PostgreSQL
│   │   │   ├── enhanced_capture_pipeline.py
│   │   │   ├── content_analyzer.py
│   │   │   ├── content_chunker.py
│   │   │   ├── embedding_service.py
│   │   │   └── domain_extractors.py
│   │   └── models/
│   ├── mcp_server.py            # MCP server for chat storage
│   ├── requirements.txt
│   ├── .env
│   └── migrations/
│       └── create_chat_records_table.sql
│
└── synapse-extension/
    ├── manifest.json
    ├── background.js
    ├── content.js
    └── icons/

```

## 🔍 Features

### Web Capture
- ✅ Full HTML extraction (no limits)
- ✅ Screenshot capture
- ✅ Platform-specific extraction (YouTube, GitHub, etc.)
- ✅ AI content analysis
- ✅ Automatic tagging and categorization
- ✅ Content chunking for long pages
- ✅ Multiple embeddings per page

### Chat Storage (MCP)
- ✅ Store AI conversations
- ✅ Semantic search across chats
- ✅ Support for multiple AI apps
- ✅ Tag and categorize conversations

### Search
- ✅ Semantic vector search
- ✅ Filter by content type
- ✅ Filter by tags
- ✅ Similarity scoring

## 🛠️ Troubleshooting

### "Backend not responding"
- Check backend is running: `http://localhost:8000/api/health`
- Check Qdrant is running: `http://localhost:6333/dashboard`
- Verify `.env` credentials

### "Capture fails silently"
- Open Chrome DevTools Console
- Check for errors in extension
- Check backend logs for errors

### "Embeddings dimension mismatch"
- Delete Qdrant collection
- Restart backend (will recreate with 3072 dims)

### "Supabase table doesn't exist"
- Run SQL migrations in Supabase SQL Editor
- Check table names match exactly

## 📚 Next Steps

1. **Build Electron App** - Visual UI for browsing captures
2. **Mind Map Visualization** - Graph view of connected ideas
3. **Smart Collections** - Auto-organize by topic
4. **Export Features** - Markdown, PDF export
5. **Multi-user Support** - Share captures with team

## 🎓 Learn More

- [MCP Server Guide](backend/MCP_README.md)
- [Model Context Protocol Docs](https://modelcontextprotocol.io)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Built with:**
- FastAPI
- Claude Sonnet 4.5 (via LiteLLM)
- Gemini Embeddings
- Qdrant Vector Database
- Supabase PostgreSQL
- Chrome Extension API
- Model Context Protocol (MCP)
