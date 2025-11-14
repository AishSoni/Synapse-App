# Synapse MVP - Comprehensive Development Plan

## 🎯 Project Overview

**Goal:** Build a working "second brain" application where users can:
1. Capture web pages with a keyboard shortcut
2. Store captures with AI-powered semantic understanding
3. Search captures using natural language
4. View captures in a beautiful visual interface

**Tech Stack:**
- **Electron App** (React + TypeScript) - Main UI
- **FastAPI** (Python) - Backend API embedded in Electron
- **Chrome Extension** - Capture tool
- **Supabase** - Database for captures
- **Qdrant** - Vector database for semantic search
- **Google Gemini** - AI embeddings and content extraction

---

## 📋 Development Phases

### Phase 1: Foundation Setup (Day 1)

#### 1.1 Environment Setup
- [ ] Install Node.js, Python, Chrome
- [ ] Create Supabase account and project
- [ ] Set up Qdrant (Cloud or local)
- [ ] Get Gemini API key
- [ ] Configure all API keys in `.env`

#### 1.2 Webpack Configuration
**Files to create:**
- `webpack.main.config.js` - For Electron main process
- `webpack.renderer.config.js` - For React UI
- `postcss.config.js` - For Tailwind CSS

**Why:** Electron needs separate webpack configs for main and renderer processes

#### 1.3 Extension Icons
**Files to create:**
- `synapse-extension/icons/icon16.png`
- `synapse-extension/icons/icon32.png`
- `synapse-extension/icons/icon48.png`
- `synapse-extension/icons/icon128.png`

**Quick solution:** Use a simple purple gradient square with "S" letter

---

### Phase 2: Backend Development (Day 1-2)

#### 2.1 Database Setup (Supabase)
**SQL Schema:**
```sql
CREATE TABLE captures (
  id UUID PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  html TEXT,
  screenshot TEXT,  -- Base64 encoded
  extracted_content TEXT,  -- AI-extracted summary
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_captures_created_at ON captures(created_at DESC);
CREATE INDEX idx_captures_url ON captures(url);
```

**Testing:**
- Verify table creation in Supabase dashboard
- Test connection from Python backend
- Insert test row manually

#### 2.2 Backend API Implementation
**Files completed:**
- ✅ `backend/app/main.py` - FastAPI app with endpoints
- ✅ `backend/app/services/supabase_client.py` - Database client
- ✅ `backend/app/services/gemini_client.py` - AI integration
- ✅ `backend/app/services/qdrant_client.py` - Vector search

**Endpoints to test:**
1. `GET /` - Health check
2. `POST /api/capture` - Save new capture
3. `GET /api/captures` - List all captures
4. `GET /api/search?q=query` - Semantic search
5. `GET /api/capture/{id}` - Get single capture

**Testing strategy:**
```bash
# Start backend
cd synapse-app/backend
python -m uvicorn app.main:app --reload

# Test with curl or Postman
curl http://localhost:8000/
curl http://localhost:8000/api/captures
```

#### 2.3 AI Integration
**Gemini features:**
1. **Content Extraction** - Parse HTML → meaningful summary
2. **Embeddings** - Convert text → vector for search
3. **Categorization** - Auto-detect content type (article, product, etc.)

**Testing:**
- Extract content from sample HTML
- Generate embedding for text
- Verify embedding has 768 dimensions

#### 2.4 Vector Search Setup (Qdrant)
**Collection schema:**
- **Name:** `synapse_captures`
- **Vector size:** 768 (Gemini embedding dimensions)
- **Distance:** Cosine similarity

**Testing:**
- Create collection
- Insert test vector
- Search for similar vectors

---

### Phase 3: Chrome Extension (Day 2)

#### 3.1 Extension Files
**Files completed:**
- ✅ `manifest.json` - Extension config
- ✅ `background.js` - Service worker (capture logic)
- ✅ `popup/popup.html` - Extension popup UI
- ✅ `popup/popup.js` - Popup interactions

**Key features:**
- Keyboard shortcut: `Ctrl+Shift+S`
- Captures: URL, title, HTML, screenshot
- Sends data to `localhost:8000`
- Shows success/error notifications

#### 3.2 Testing Extension
1. Load extension in Chrome
2. Open test website (e.g., Wikipedia article)
3. Press `Ctrl+Shift+S`
4. Check backend receives data
5. Verify notification appears

**Common issues:**
- CORS errors → Check backend CORS middleware
- Capture fails → Check backend is running
- No notification → Check Chrome notification permissions

---

### Phase 4: Electron App UI (Day 2-3)

#### 4.1 Webpack Setup
Need to create these configs:

**webpack.main.config.js:**
- Compiles TypeScript for main process
- Entry: `src/main/main.ts`
- Output: `dist/main/main.js`
- Target: `electron-main`

**webpack.renderer.config.js:**
- Compiles React + TypeScript
- Entry: `src/renderer/index.tsx`
- Output: `dist/renderer/`
- Includes HtmlWebpackPlugin
- Dev server on port 9000

**postcss.config.js:**
- Tailwind CSS processing
- Autoprefixer

#### 4.2 Electron Main Process
**File:** `src/main/main.ts`

**Responsibilities:**
1. Spawn FastAPI backend as subprocess
2. Create app window
3. Handle app lifecycle
4. Kill backend on quit

**Testing:**
```bash
npm install
npm run dev
```
- Verify Electron window opens
- Check backend starts automatically
- Confirm React UI loads

#### 4.3 React UI Components
**Files completed:**
- ✅ `src/renderer/App.tsx` - Main app component
- ✅ `src/renderer/App.css` - Styles
- ✅ `src/renderer/index.tsx` - React entry

**Features implemented:**
- Custom title bar (frameless window)
- Sidebar navigation
- Search bar with live search
- Card grid for captures
- Empty state

**Additional components to create:**
- `components/CaptureCard.tsx` - Individual card
- `components/SearchBar.tsx` - Search component
- `components/MindMap.tsx` - Mind map view (later)

#### 4.4 UI Testing
1. Launch Electron app
2. Verify empty state shows
3. Capture a page from extension
4. See card appear in grid
5. Test search functionality
6. Check card interactions

---

### Phase 5: Integration & Testing (Day 3-4)

#### 5.1 End-to-End Flow
**Complete user journey:**
1. User opens Electron app
2. Backend starts automatically
3. User browses web, finds interesting page
4. User presses `Ctrl+Shift+S`
5. Extension captures page data
6. Sends to backend API
7. Backend processes with Gemini
8. Stores in Supabase + Qdrant
9. Electron UI polls and shows new capture
10. User searches for capture later
11. Semantic search finds it

#### 5.2 Testing Checklist

**Backend Tests:**
- [ ] Health check endpoint works
- [ ] Can create new capture
- [ ] Gemini extracts content correctly
- [ ] Embedding generated (768 dims)
- [ ] Supabase stores data
- [ ] Qdrant stores vector
- [ ] List captures returns data
- [ ] Search finds relevant results

**Extension Tests:**
- [ ] Loads in Chrome without errors
- [ ] Icon appears in toolbar
- [ ] Keyboard shortcut works
- [ ] Captures current tab correctly
- [ ] Screenshot quality is good
- [ ] Sends data to backend
- [ ] Shows success notification
- [ ] Handles errors gracefully

**Electron App Tests:**
- [ ] App launches successfully
- [ ] Backend subprocess starts
- [ ] UI renders correctly
- [ ] Empty state displays
- [ ] Captures list loads
- [ ] Search bar works
- [ ] Cards display properly
- [ ] Images load correctly
- [ ] Clicking card shows details
- [ ] App closes cleanly

**Integration Tests:**
- [ ] Capture → Backend → Database → UI
- [ ] Search → Query embedding → Qdrant → Results
- [ ] Multiple captures work
- [ ] Captures persist after restart
- [ ] Cross-device sync (Supabase)

#### 5.3 Bug Fixes & Polish
Common issues to fix:
- Loading states for async operations
- Error handling and user feedback
- Image optimization for screenshots
- Search debouncing (don't search on every keystroke)
- Pagination for large capture lists
- Duplicate capture detection

---

### Phase 6: Polish & Distribution (Day 4-5)

#### 6.1 UI Enhancements
- [ ] Loading skeletons for cards
- [ ] Smooth animations (Framer Motion)
- [ ] Hover effects and transitions
- [ ] Keyboard shortcuts in app
- [ ] Context menus (right-click)
- [ ] Dark mode (already default)

#### 6.2 Performance Optimization
- [ ] Lazy load images
- [ ] Virtual scrolling for large lists
- [ ] Debounce search input
- [ ] Cache search results
- [ ] Optimize screenshot size
- [ ] Bundle size optimization

#### 6.3 Build & Package
```bash
# Build for production
npm run build

# Package for distribution
npm run package
```

**Outputs:**
- Windows: `release/Synapse Setup.exe`
- Mac: `release/Synapse.dmg`

**electron-builder config:**
- Already set up in `package.json`
- Includes app icon
- Bundles backend executable
- Creates installer

#### 6.4 Documentation
**Files to create:**
- ✅ `PROJECT_SETUP.md` - Setup instructions
- [ ] `USER_GUIDE.md` - How to use the app
- [ ] `TROUBLESHOOTING.md` - Common issues
- [ ] `CONTRIBUTING.md` - For developers

---

## 🚀 Quick Start Workflow

### For Development (First Time)

**Day 1 Morning:**
1. Set up all external services (Supabase, Qdrant, Gemini)
2. Configure `.env` file
3. Create webpack configs
4. Install dependencies

**Day 1 Afternoon:**
5. Test backend API standalone
6. Create extension icons
7. Load extension in Chrome
8. Test extension → backend flow

**Day 2:**
9. Set up Electron app
10. Test Electron + React rendering
11. Integrate backend subprocess
12. Test end-to-end capture

**Day 3:**
13. Polish UI
14. Add search functionality
15. Fix bugs
16. Improve error handling

**Day 4:**
17. Performance optimization
18. Build for production
19. Create distribution package
20. Write user documentation

---

## 📁 File Structure

```
Appointy_Task_1/
├── vision.md                        # Original vision
├── PROJECT_SETUP.md                 # Setup guide
├── DEVELOPMENT_PLAN.md             # This file
│
├── synapse-app/                    # Electron App
│   ├── package.json
│   ├── tsconfig.json
│   ├── webpack.main.config.js      # TODO: Create
│   ├── webpack.renderer.config.js  # TODO: Create
│   ├── postcss.config.js           # TODO: Create
│   │
│   ├── src/
│   │   ├── main/
│   │   │   ├── main.ts             # ✅ Main process
│   │   │   └── preload.ts          # ✅ Preload script
│   │   │
│   │   └── renderer/
│   │       ├── index.tsx           # ✅ React entry
│   │       ├── App.tsx             # ✅ Main component
│   │       ├── App.css             # ✅ Styles
│   │       └── components/         # TODO: Add components
│   │
│   └── backend/                    # FastAPI Backend
│       ├── requirements.txt        # ✅ Dependencies
│       ├── .env.example            # ✅ Template
│       ├── .env                    # TODO: Create with real keys
│       │
│       └── app/
│           ├── main.py             # ✅ FastAPI app
│           └── services/
│               ├── supabase_client.py  # ✅ Database
│               ├── gemini_client.py    # ✅ AI
│               └── qdrant_client.py    # ✅ Vector search
│
└── synapse-extension/              # Chrome Extension
    ├── manifest.json               # ✅ Extension config
    ├── background.js               # ✅ Service worker
    ├── popup/
    │   ├── popup.html              # ✅ Popup UI
    │   └── popup.js                # ✅ Popup logic
    └── icons/                      # TODO: Add icons
        ├── icon16.png
        ├── icon32.png
        ├── icon48.png
        └── icon128.png
```

---

## 🔧 Missing Pieces to Complete

### Critical (Must have for MVP):

1. **Webpack Configurations** (3 files)
   - Required for Electron to build and run
   - Estimated time: 30 minutes

2. **Extension Icons** (4 files)
   - Can use simple placeholder images
   - Estimated time: 15 minutes

3. **Environment Variables** (.env file)
   - Copy from .env.example and fill in
   - Estimated time: 10 minutes

4. **Service Setup** (External)
   - Supabase project + SQL schema
   - Qdrant account (or Docker)
   - Gemini API key
   - Estimated time: 45 minutes

### Nice to Have (Can add later):

5. **Component Breakdown**
   - Separate React components
   - Better code organization

6. **Error Boundaries**
   - Graceful error handling in React

7. **Loading States**
   - Better UX during async operations

8. **Tests**
   - Unit tests for components
   - Integration tests for API

---

## 🎯 Next Immediate Steps

Ready to start building? Here's what to do next:

1. **Create Webpack configs** - Let me know and I'll generate them
2. **Create extension icons** - I can generate simple placeholder icons
3. **Set up external services** - Follow PROJECT_SETUP.md
4. **Install dependencies** - Run `npm install` and `pip install`
5. **Start testing** - Run backend and Electron app

Which component would you like me to work on first?
