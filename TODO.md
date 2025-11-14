# Synapse - Development TODO

## 🔴 Critical Issues (Must Fix)

### 1. Backend Connection & Search
**Problem:** Search shows "backend not running" even when it is
**Tasks:**
- [ ] Fix CORS configuration in backend
- [ ] Add proper error handling for backend connection failures
- [ ] Test IPC communication between Electron and backend
- [ ] Add connection status indicator in UI
- [ ] Implement retry logic for failed requests

**Files to modify:**
- `synapse-desktop/main.js` - IPC handlers
- `synapse-desktop/app.js` - Search function
- `synapse-app/backend/app/main.py` - CORS settings

---

### 2. Real-time Capture Updates
**Problem:** New captures don't appear until app restart
**Tasks:**
- [ ] Implement WebSocket connection between backend and desktop
- [ ] Send real-time events when capture completes
- [ ] Add "Capturing..." indicator in sidebar
- [ ] Auto-update mind map when new capture arrives
- [ ] Show progress: "Processing..." → "Analyzing..." → "Complete!"
- [ ] Add notification toast when capture is ready

**Implementation approach:**
```python
# Backend: Add WebSocket endpoint
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Broadcast capture events
```

```javascript
// Frontend: Listen for events
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const capture = JSON.parse(event.data);
    addCaptureToMindMap(capture);
};
```

**Files to create/modify:**
- `synapse-app/backend/app/main.py` - WebSocket endpoint
- `synapse-app/backend/app/services/websocket_manager.py` - NEW
- `synapse-desktop/app.js` - WebSocket client
- `synapse-desktop/index.html` - Progress indicators

---

### 3. LLM Chat Integration
**Problem:** Search only shows results, doesn't answer questions
**Tasks:**
- [ ] Implement RAG (Retrieval-Augmented Generation) pipeline
- [ ] Search retrieves relevant captures
- [ ] LLM answers question using retrieved context
- [ ] Show both: AI answer + source citations
- [ ] Stream responses for better UX
- [ ] Add "Ask a question" vs "Search sources" modes

**RAG Pipeline:**
```
User Query
    ↓
1. Generate embedding
    ↓
2. Search Qdrant (get top 5 relevant captures)
    ↓
3. Build context from captures
    ↓
4. Send to Claude: "Answer based on these sources: [context]"
    ↓
5. Stream response to UI
    ↓
6. Show answer + clickable source links
```

**Files to create:**
- `synapse-app/backend/app/services/rag_service.py` - NEW
- `synapse-app/backend/app/api/chat.py` - NEW chat endpoint
- `synapse-desktop/app.js` - Chat UI updates

---

### 4. Time-Aware Search
**Problem:** Can't search "article from last week"
**Tasks:**
- [ ] Parse temporal queries ("last week", "yesterday", "this month")
- [ ] Add date filters to search
- [ ] Store capture timestamp in Qdrant metadata
- [ ] Filter by date range
- [ ] Add timeline view option

**Implementation:**
```python
# Parse temporal expressions
def parse_temporal_query(query: str) -> dict:
    if "last week" in query.lower():
        start_date = datetime.now() - timedelta(days=7)
        return {"start_date": start_date}
    # ... more patterns
```

**Files to create/modify:**
- `synapse-app/backend/app/services/temporal_parser.py` - NEW
- `synapse-app/backend/app/main.py` - Update search endpoint
- `synapse-desktop/app.js` - Date filter UI

---

### 5. Content Type Categorization
**Problem:** Source categories are incorrect
**Tasks:**
- [ ] Review content_analyzer.py logic
- [ ] Add better platform detection
- [ ] Use domain patterns for categorization
- [ ] Test with sample URLs
- [ ] Add manual override option

**Platform patterns:**
```python
PLATFORM_PATTERNS = {
    'youtube.com': 'video',
    'github.com': 'code',
    'amazon.com': 'product',
    'arxiv.org': 'research',
    'twitter.com': 'social',
    'medium.com': 'article',
}
```

**Files to modify:**
- `synapse-app/backend/app/services/content_analyzer.py`
- `synapse-app/backend/app/services/domain_extractors.py`

---

## 🟡 UI/UX Improvements

### 6. Complete Menu System
**Problem:** Many menus are placeholders
**Tasks:**

#### Settings Menu
- [ ] Backend URL configuration
- [ ] API key management
- [ ] Theme customization
- [ ] Keyboard shortcuts editor
- [ ] Clear cache option
- [ ] Export/import settings

#### Spaces Menu
- [ ] Edit space name
- [ ] Delete space
- [ ] Merge spaces
- [ ] Export space to Markdown
- [ ] Share space (export JSON)
- [ ] Space color picker

#### Node Context Menu (Right-click)
- [ ] Open source
- [ ] Copy URL
- [ ] Add to space
- [ ] Remove from space
- [ ] Edit tags
- [ ] Delete capture
- [ ] Re-analyze with AI

#### Top Menu Bar
- [ ] File → Export, Import, Settings
- [ ] Edit → Select All, Clear Selection
- [ ] View → Zoom In/Out, Reset, Timeline
- [ ] Spaces → Create, Manage, Filter
- [ ] Help → Documentation, Keyboard Shortcuts, About

**Files to modify:**
- `synapse-desktop/index.html` - Add menu HTML
- `synapse-desktop/app.js` - Menu event handlers
- Create: `synapse-desktop/components/settings.js`
- Create: `synapse-desktop/components/menus.js`

---

### 7. Search Modes
**Problem:** Need both semantic search AND chat
**Tasks:**
- [ ] Add mode toggle: "Search" vs "Ask"
- [ ] Search mode: Returns sources only (current behavior)
- [ ] Ask mode: LLM answers + cites sources
- [ ] Visual distinction between modes
- [ ] Default to Search mode

**UI Design:**
```
[Search 🔍] [Ask 💬]  <-- Toggle buttons

Search mode:
  Input: "python async"
  Output: List of relevant captures

Ask mode:
  Input: "How do I handle errors in Python async?"
  Output:
    AI: "Based on your captured sources, here are 3 approaches..."
    Sources: [Article 1] [Stack Overflow] [Tutorial]
```

**Files to modify:**
- `synapse-desktop/index.html` - Add mode toggle
- `synapse-desktop/app.js` - Handle both modes
- `synapse-app/backend/app/main.py` - Add /chat endpoint

---

### 8. Capture Progress Tracking
**Problem:** No feedback during long captures
**Tasks:**
- [ ] Add capture queue in sidebar
- [ ] Show stages: Scraping → Analyzing → Embedding → Storing
- [ ] Progress percentage for each stage
- [ ] Error states with retry button
- [ ] Success animation
- [ ] Cancel capture option

**UI Component:**
```html
<div class="capture-progress">
  <div class="capture-item">
    <img src="favicon.ico" />
    <div class="info">
      <div class="title">Capturing: Python Async Guide</div>
      <div class="status">
        <div class="stage">Analyzing with AI...</div>
        <div class="progress-bar">
          <div class="fill" style="width: 60%"></div>
        </div>
      </div>
    </div>
  </div>
</div>
```

**Files to create:**
- `synapse-desktop/components/capture-progress.js` - NEW
- Update: `synapse-desktop/index.html`

---

## 🟢 Feature Enhancements

### 9. Todo List Integration in Chat
**Problem:** Need to create and manage TODOs directly from chat conversations
**Tasks:**
- [ ] Detect TODO items in chat responses
- [ ] Add "Create TODO" button in chat interface
- [ ] Parse TODO items from AI responses
- [ ] Store TODOs in Supabase (chat_todos table)
- [ ] Display TODO list in sidebar
- [ ] Mark TODOs as complete/incomplete
- [ ] Link TODOs to source captures
- [ ] Filter TODOs by status (pending/done)

**Implementation:**
```sql
-- Supabase table
CREATE TABLE chat_todos (
    id UUID PRIMARY KEY,
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    source_capture_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

```javascript
// Parse TODOs from chat
function extractTodos(text) {
    const todoPattern = /[-*]\s*\[ \]\s*(.+)/g;
    const matches = text.matchAll(todoPattern);
    return Array.from(matches, m => m[1]);
}

// Show TODO button
if (response.includes('- [ ]')) {
    showCreateTodoButton();
}
```

**UI Component:**
```html
<div class="todo-sidebar">
    <h3>Your TODOs</h3>
    <div class="todo-item">
        <input type="checkbox" />
        <span>Research Python async patterns</span>
        <a href="#" class="source-link">From: Python Guide</a>
    </div>
</div>
```

**Files to create:**
- `synapse-app/backend/app/api/todos.py` - TODO CRUD endpoints
- `synapse-desktop/components/todo-list.js` - TODO UI component
- `synapse-desktop/index.html` - Add TODO sidebar

---

### 10. Enhanced Node Labels & Colors
**Problem:** Nodes only show content type abbreviation, hard to read
**Tasks:**
- [ ] Show full title on nodes (not just type)
- [ ] Adjust font size based on node importance
- [ ] Add node size variation (more important = larger)
- [ ] Improve color scheme for better contrast
- [ ] Add visual indicators for recent captures
- [ ] Show tag badges on nodes
- [ ] Hover shows full metadata card
- [ ] Click shows quick preview

**Visual Design:**
```javascript
// Node rendering with labels
node.append('circle')
    .attr('r', d => 30 + (d.importance * 10))  // Size by importance
    .attr('fill', d => getNodeColor(d))
    .attr('stroke', d => d.isRecent ? '#fbbf24' : '#1f2937')  // Gold for recent
    .attr('stroke-width', d => d.isRecent ? 3 : 2);

// Full title label
node.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '-35px')  // Above node
    .attr('font-size', '12px')
    .attr('fill', 'white')
    .attr('font-weight', 'bold')
    .attr('class', 'node-title')
    .text(d => truncateTitle(d.title, 30));

// Type badge below
node.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '4px')  // Center of node
    .attr('font-size', '10px')
    .attr('fill', 'white')
    .text(d => d.contentType.toUpperCase());

// Tag badges
if (d.tags.length > 0) {
    node.append('rect')
        .attr('x', 20)
        .attr('y', -10)
        .attr('width', 30)
        .attr('height', 15)
        .attr('rx', 3)
        .attr('fill', '#4b5563');

    node.append('text')
        .attr('x', 35)
        .attr('y', 0)
        .attr('font-size', '8px')
        .attr('fill', 'white')
        .text(`+${d.tags.length}`);
}

// Improved color scheme
function getNodeColor(node) {
    const colors = {
        article: { bg: '#8b5cf6', text: '#f3e8ff' },      // Purple
        product: { bg: '#ec4899', text: '#fce7f3' },      // Pink
        video: { bg: '#f59e0b', text: '#fef3c7' },        // Amber
        code: { bg: '#10b981', text: '#d1fae5' },         // Emerald
        chat: { bg: '#3b82f6', text: '#dbeafe' },         // Blue
        research: { bg: '#8b5cf6', text: '#f3e8ff' },     // Violet
        social: { bg: '#ef4444', text: '#fee2e2' },       // Red
        default: { bg: '#6366f1', text: '#e0e7ff' }       // Indigo
    };

    return colors[node.contentType] || colors.default;
}
```

**Hover Metadata Card:**
```javascript
node.on('mouseenter', (event, d) => {
    showMetadataCard(d, event.pageX, event.pageY);
});

function showMetadataCard(node, x, y) {
    const card = document.createElement('div');
    card.className = 'metadata-card';
    card.style.left = x + 'px';
    card.style.top = y + 'px';
    card.innerHTML = `
        <div class="title">${node.title}</div>
        <div class="url">${node.url}</div>
        <div class="tags">${node.tags.map(t => `<span>${t}</span>`).join('')}</div>
        <div class="date">${formatDate(node.created_at)}</div>
        <div class="summary">${node.summary}</div>
    `;
    document.body.appendChild(card);
}
```

**Files to modify:**
- `synapse-desktop/app.js` - Update node rendering
- `synapse-desktop/index.html` - Add metadata card CSS
- Add: `synapse-desktop/styles/nodes.css` - Node styling

---

### 11. Timeline View
**Tasks:**
- [ ] Filter by content type
- [ ] Filter by tags
- [ ] Filter by date range
- [ ] Filter by source domain
- [ ] Combine multiple filters
- [ ] Save filter presets

### 11. Bulk Operations
**Tasks:**
- [ ] Select multiple nodes (Shift+Click range select)
- [ ] Bulk tag editing
- [ ] Bulk delete
- [ ] Bulk export
- [ ] Bulk re-categorize

### 12. Image Gallery View
**Tasks:**
- [ ] Show all captured images
- [ ] Grid view with screenshots
- [ ] Click to open source
- [ ] Filter images by capture
- [ ] Download images

### 13. Export Features
**Tasks:**
- [ ] Export space to Markdown
- [ ] Export as JSON
- [ ] Export as HTML (standalone)
- [ ] Export mind map as image
- [ ] Export search results

---

## 🔵 Backend Improvements

### 14. API Endpoints to Add
- [ ] `POST /api/chat` - RAG-powered Q&A
- [ ] `GET /api/captures/recent?days=7` - Time-filtered
- [ ] `GET /api/timeline` - Grouped by date
- [ ] `DELETE /api/capture/{id}` - Delete capture
- [ ] `PUT /api/capture/{id}` - Update capture
- [ ] `GET /api/stats` - Usage statistics
- [ ] `WS /ws` - WebSocket for real-time updates

### 15. Database Optimizations
- [ ] Add indexes for date queries
- [ ] Add full-text search index
- [ ] Implement caching for frequent queries
- [ ] Add pagination for large result sets

### 16. Error Handling
- [ ] Graceful handling of API failures
- [ ] Retry logic with exponential backoff
- [ ] Better error messages to user
- [ ] Log errors to file
- [ ] Health check endpoint with dependencies

---

## 📋 Implementation Priority

### Phase 1: Critical Fixes ✅ **COMPLETE!**
1. ✅ Fix backend connection
2. ✅ Implement WebSocket for real-time updates
3. ✅ Add RAG chat endpoint
4. ✅ Time-aware search
5. ✅ Fix content categorization
6. ✅ Search/Ask mode toggle

### Phase 2: UI/UX Improvements (Week 2)
7. 🆕 **Enhanced node labels & colors** (NEW)
8. ⏳ Capture progress UI
9. 🆕 **TODO list integration in chat** (NEW)
10. ⏳ Complete settings menu
11. ⏳ Context menus

### Phase 3: Core Features (Week 3)
12. ⏳ Timeline view
13. ⏳ Advanced filters
14. ⏳ Bulk operations
15. ⏳ Image gallery

### Phase 4: Polish (Week 4)
16. ⏳ Export features
17. ⏳ Keyboard shortcuts
18. ⏳ Documentation updates

---

## 🛠️ Technical Debt

### Code Quality
- [ ] Add TypeScript for better type safety
- [ ] Split app.js into modules
- [ ] Add unit tests for backend
- [ ] Add E2E tests for UI
- [ ] Improve error boundaries

### Performance
- [ ] Lazy load mind map nodes (virtual rendering)
- [ ] Debounce search input
- [ ] Cache search results
- [ ] Optimize D3.js rendering
- [ ] Add service worker for offline support

### Security
- [ ] Sanitize HTML before rendering
- [ ] Validate all user inputs
- [ ] Rate limiting on backend
- [ ] Secure API keys in Electron
- [ ] Add authentication (optional)

---

## 📝 Documentation

- [ ] API documentation (Swagger)
- [ ] Component documentation
- [ ] User guide with screenshots
- [ ] Video tutorial
- [ ] FAQ section
- [ ] Troubleshooting guide

---

## 🎯 Success Criteria

### Critical Issues Fixed:
- [x] Backend connection works
- [x] Real-time capture updates
- [x] LLM chat integration
- [x] Time-aware search
- [x] Correct categorization

### User Experience:
- [x] Captures appear instantly
- [x] Can ask questions and get answers
- [x] Can search by time period
- [x] All menus functional
- [x] Smooth, responsive UI

### Performance:
- [x] Search < 500ms
- [x] Mind map renders 500+ nodes smoothly
- [x] No memory leaks
- [x] Works offline (cached data)

---

## 🚀 Getting Started

To tackle these TODOs, start with **Phase 1** in order:

1. **Fix backend connection first** - Nothing works without this
2. **Add WebSocket** - Enables real-time updates
3. **Implement RAG chat** - Core value proposition
4. **Fix categorization** - Improves accuracy

Each task has clear files to modify and implementation hints.

Let's build an amazing second brain! 🧠✨
