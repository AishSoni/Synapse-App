# Synapse - Quick Start Guide

Your complete second brain is now ready! Here's how to use the entire system.

## ✅ What You Have

### 1. **Chrome Extension** (Alt+B to Capture)
- Instant web page capture
- Full HTML + screenshots
- Zero config needed
- Location: `synapse-extension/`

### 2. **Backend Server** (AI-Powered Processing)
- FastAPI server
- Claude Sonnet 4.5 analysis
- Gemini embeddings (3072d)
- Qdrant + Supabase storage
- Location: `synapse-app/backend/`

### 3. **Desktop App** (Beautiful Mind Map UI)
- Interactive node graph
- Semantic search engine
- Direct source links with images
- Spaces for organization
- Location: `synapse-desktop/`

### 4. **MCP Server** (Store AI Conversations)
- Works with Claude Desktop
- Stores chat summaries
- Searchable conversations
- Location: `synapse-app/backend/mcp_server.py`

## 🚀 How to Use the Complete System

### Step 1: Start the Backend

```bash
cd synapse-app/backend
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal running!**

### Step 2: Start the Desktop App

Open a NEW terminal:

```bash
cd synapse-desktop
npm start
```

The beautiful dark-themed UI will open!

### Step 3: Capture Some Content

1. **Install Chrome Extension:**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `synapse-extension` folder
   - Extension installed!

2. **Capture a webpage:**
   - Visit any webpage (Wikipedia, YouTube, GitHub, etc.)
   - Press **Alt+B**
   - See flash + "Captured!" toast
   - Content is now processing in the backend

3. **Watch the backend logs:**
   - You'll see the entire pipeline:
     ```
     [CAPTURE] ENHANCED CAPTURE PIPELINE
     > Step 1: Processing HTML and extracting content...
       [OK] Processed 4027 words
     > Step 2: Platform-specific extraction...
     > Step 3: AI analysis with Claude Sonnet 4...
     > Step 4: Chunking long content...
     > Step 5: Generating embeddings...
     > Step 6: Storing in Qdrant + Supabase...
     [COMPLETE] CAPTURE COMPLETE
     ```

### Step 4: Search Your Memories

In the Desktop App:

1. **Click the search bar** (or press **Cmd+K**)
2. **Type your query:** "python async patterns"
3. **See results instantly:**
   - Screenshots of captured pages
   - Direct links to original sources
   - Similarity scores
   - Tags and metadata
4. **Click a result** to open the original URL
5. **Click "View Details"** for full capture info

### Step 5: Explore the Mind Map

- **Nodes** = Your captured content
- **Links** = Semantic connections (shared topics)
- **Colors** = Content types:
  - Violet = Articles
  - Pink = Products
  - Amber = Videos
  - Emerald = Code
  - Blue = Chats

**Interactions:**
- **Click node** → View details
- **Drag node** → Reposition
- **Scroll** → Zoom
- **Cmd/Ctrl + Click** → Multi-select

### Step 6: Organize into Spaces

Create collections of related content:

1. **Method 1: From Selected Nodes**
   - Hold Cmd/Ctrl and click multiple nodes
   - Click "Group into Space" (top right)
   - Name your space (e.g., "AI Research")

2. **Method 2: Empty Space**
   - Click "+ Create Space" in sidebar
   - Name it
   - Add nodes later

## 🎯 Key Features

### 1. Search Engine for Your Memories

The app is **NOT an AI assistant**. It's a search engine that shows you:

✅ **Direct sources** - Original URLs you captured
✅ **Screenshots** - Visual preview of pages
✅ **Captured summaries** - From when you saved them
✅ **Images from pages** - All extracted images
✅ **Similarity scores** - How well they match your query

❌ **No AI-generated answers**
❌ **No hallucinations**
❌ **No made-up content**

### 2. Capture ANYTHING

Works with:
- Wikipedia articles
- YouTube videos
- GitHub repos
- Twitter/X posts
- Product pages (Amazon, etc.)
- Research papers (ArXiv)
- Blog posts
- Documentation
- **Any webpage!**

### 3. Smart Organization

- **Spaces** - Manual collections
- **Tags** - Auto-generated from content
- **Semantic Links** - AI finds connections
- **Visual Clusters** - See related ideas

## 📱 Optional: MCP Server for AI Chats

Store conversations from Claude Desktop:

### Setup (One-time)

1. **Create Supabase table:**
   ```bash
   cd synapse-app/backend
   # Run SQL from migrations/create_chat_records_table.sql in Supabase
   ```

2. **Configure Claude Desktop:**

   Edit `claude_desktop_config.json`:

   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "synapse-chat-storage": {
         "command": "python",
         "args": ["E:\\Appointy_Task_1\\synapse-app\\backend\\mcp_server.py"],
         "env": {
           "PYTHONPATH": "E:\\Appointy_Task_1\\synapse-app\\backend"
         }
       }
     }
   }
   ```

   **Update the path to match your installation!**

3. **Restart Claude Desktop**

### Usage

In Claude Desktop, say:

> "Please store this conversation using store_chat.
> Title: 'Python Best Practices'
> Summary: 'Discussion about async patterns and error handling in Python'
> Tags: ['python', 'programming']"

Claude will call the MCP tool and store it in your Synapse database. Now you can search for it in the Desktop app!

## 🔧 Troubleshooting

### "Mind map is empty"
- Capture some pages first (Alt+B)
- Check backend is running
- Refresh desktop app (Cmd+R / Ctrl+R)

### "Search returns nothing"
- Make sure backend is running on port 8000
- Check you have captured content
- Test: `curl http://localhost:8000/api/health`

### "Extension not capturing"
- Check backend logs for errors
- Verify backend is running
- Try refreshing the extension (chrome://extensions/)

### "Images not showing in search"
- Check the capture has a screenshot
- Backend may have failed to store screenshot
- Try re-capturing the page

## 📊 Example Workflow

### Research Workflow

1. **Capture sources:**
   - Press Alt+B on research papers
   - Capture related articles
   - Save code examples

2. **Search & Connect:**
   - Search: "transformer architecture"
   - See all related captures
   - Click through to original sources

3. **Organize:**
   - Select relevant nodes
   - Group into "Transformer Research" Space
   - Visual cluster appears

4. **Reference Later:**
   - Quick search finds everything
   - Direct links to sources
   - Screenshots refresh your memory

### Learning Workflow

1. **While learning Python:**
   - Capture tutorial pages
   - Save Stack Overflow answers
   - Bookmark documentation

2. **When stuck later:**
   - Search: "python async error handling"
   - Find exact pages you saved
   - See your past notes/summaries
   - Jump directly to source

## 🎨 Customization

### Change Theme Colors

Edit `synapse-desktop/app.js`:

```javascript
const COLORS = {
    article: '#8b5cf6',  // Change these!
    product: '#ec4899',
    // ...
};
```

### Adjust Mind Map Physics

Edit the force simulation:

```javascript
simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-300)) // Repulsion
    .force('link', d3.forceLink(links).distance(150))  // Link length
```

## 🔐 Privacy & Data

**Everything is LOCAL:**
- ✅ Qdrant runs locally (default)
- ✅ Supabase Cloud (your private instance)
- ✅ Desktop app stores Spaces in localStorage
- ✅ No tracking, no telemetry
- ✅ Your data never leaves your control

**APIs Used:**
- LiteLLM Proxy (your custom endpoint)
- Claude Sonnet 4.5 (for analysis)
- Gemini Embeddings (for search)

## 📈 Performance Tips

- **< 500 captures**: Smooth experience
- **500-1000 captures**: Use Spaces to filter
- **1000+ captures**: Rely on search instead of showing all nodes

## 🎯 Next Steps

1. **Capture 10-20 pages** to build your knowledge base
2. **Try semantic search** - search by concept, not exact words
3. **Create Spaces** for different topics/projects
4. **Setup MCP** to store AI conversations
5. **Build your second brain!** 🧠

## 📚 Documentation

- **Backend Guide**: `synapse-app/backend/README.md`
- **Desktop App**: `synapse-desktop/README.md`
- **MCP Server**: `synapse-app/backend/MCP_README.md`
- **Full Setup**: `SETUP_GUIDE.md`

## 🆘 Getting Help

- Check backend logs for errors
- Open browser console in desktop app (Cmd+Option+I / Ctrl+Shift+I)
- Verify all services are running:
  - Backend: `http://localhost:8000/api/health`
  - Qdrant: `http://localhost:6333/dashboard`
  - Desktop app: Should open automatically

## 🎉 You're All Set!

Your complete second brain system is ready to use. Start capturing and organizing your knowledge!

**Quick Commands:**

```bash
# Terminal 1: Backend
cd synapse-app/backend && python -m uvicorn app.main:app --reload

# Terminal 2: Desktop App
cd synapse-desktop && npm start

# Then: Press Alt+B in Chrome to capture pages!
```

---

**Built with:** FastAPI • Claude Sonnet 4.5 • Gemini Embeddings • Qdrant • Supabase • Electron • D3.js
