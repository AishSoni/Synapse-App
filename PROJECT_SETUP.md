# Synapse - Setup Guide

## Architecture Overview

```
Synapse (Electron App)
├── Frontend (React UI)
├── Backend (FastAPI embedded)
│   ├── Supabase (Database)
│   ├── Qdrant (Vector Search)
│   └── Gemini (AI/Embeddings)
└── Chrome Extension (Capture Tool)
```

## Quick Start

### 1. Prerequisites

Install these first:
- **Node.js 18+** - https://nodejs.org/
- **Python 3.10+** - https://www.python.org/
- **Chrome Browser**

### 2. Setup Supabase (Database)

1. Go to https://supabase.com and create a free account
2. Create a new project
3. Go to **Table Editor** and run this SQL:

```sql
CREATE TABLE captures (
  id UUID PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  html TEXT,
  screenshot TEXT,
  extracted_content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_captures_created_at ON captures(created_at DESC);
```

4. Go to **Settings → API** and copy:
   - Project URL (SUPABASE_URL)
   - Anon/Public Key (SUPABASE_KEY)

### 3. Setup Qdrant (Vector Search)

**Option A: Qdrant Cloud (Recommended)**
1. Go to https://cloud.qdrant.io/ and create free account
2. Create a cluster
3. Copy the URL and API key

**Option B: Local Qdrant**
```bash
# Run in Docker (optional)
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Copy the key

### 5. Configure Backend

```bash
cd synapse-app/backend
cp .env.example .env
```

Edit `.env` file with your keys:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key
QDRANT_URL=your_qdrant_url (or http://localhost:6333)
QDRANT_API_KEY=your_qdrant_key (if using cloud)
```

### 6. Install Dependencies

**Backend:**
```bash
cd synapse-app/backend
pip install -r requirements.txt
```

**Frontend (Electron App):**
```bash
cd synapse-app
npm install
```

### 7. Run in Development Mode

**Terminal 1 - Start Backend:**
```bash
cd synapse-app/backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Start Electron App:**
```bash
cd synapse-app
npm run dev
```

The Electron app should open automatically!

### 8. Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `synapse-extension` folder
5. The extension icon should appear in your toolbar

## Testing the Flow

1. Open any website in Chrome
2. Press `Ctrl+Shift+S` (or `Cmd+Shift+S` on Mac)
3. You should see a notification "Capturing page..."
4. Open the Synapse app - your capture should appear in the grid!
5. Try searching for content in the search bar

## Troubleshooting

### Backend not starting?
- Make sure Python 3.10+ is installed: `python --version`
- Check that all API keys in `.env` are correct
- Look for error messages in the terminal

### Extension not capturing?
- Make sure the backend is running on port 8000
- Check Chrome extension errors: `chrome://extensions/` → Details → Errors
- Try reloading the extension

### Electron app not showing captures?
- Open DevTools in the app (Ctrl+Shift+I)
- Check console for errors
- Verify backend is accessible at http://localhost:8000

### Search not working?
- Ensure Qdrant is running (check QDRANT_URL in .env)
- Verify Gemini API key is valid
- Check backend logs for embedding errors

## Next Steps

Once everything is working:

1. **Build for production:**
   ```bash
   cd synapse-app
   npm run build
   npm run package
   ```
   This creates distributable files in `synapse-app/release/`

2. **Customize the UI** - Edit files in `synapse-app/src/renderer/`

3. **Add features** - Check `vision.md` for the full roadmap

## Need Help?

- Backend API docs: http://localhost:8000/docs (when running)
- Check logs in both terminals for error messages
- Make sure all environment variables are set correctly

---

**Enjoy building your second brain! 🧠**
