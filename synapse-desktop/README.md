# Synapse Desktop - Mind Map UI

Beautiful dark-themed desktop application for visualizing and exploring your second brain.

## Features

### 🧠 Mind Map Visualization
- **Interactive Node Graph** - D3.js-powered force-directed layout
- **Semantic Links** - AI-generated connections based on shared topics
- **Color-Coded Nodes** - Different colors for articles, products, videos, code, chats
- **Zoom & Pan** - Smooth navigation of large knowledge graphs
- **Multi-Select** - Cmd/Ctrl+Click to select multiple nodes

### 📦 Spaces (Collections)
- **User-Defined Groups** - Organize nodes into named Spaces
- **Drag & Drop** - Move nodes between Spaces
- **Auto-Grouping** - AI can suggest groupings based on content
- **Persistent Storage** - Spaces saved in localStorage

### 🔍 Intelligent Search
- **Semantic Search** - Find by meaning, not just keywords
- **Floating Chat Window** - Quick access with Cmd+K
- **Real-time Results** - Instant search as you type
- **Similarity Scores** - See how well results match your query

### 🎨 Design Highlights
- **Dark Theme** - Easy on the eyes for long sessions
- **Neon Accents** - Indigo/Violet highlights (#6366f1)
- **Smooth Animations** - 60 FPS transitions
- **Native Feel** - Custom title bar, optimized for desktop

## Installation

### Prerequisites
- Node.js 16+ and npm
- Synapse backend running on `http://localhost:8000`
- Some captured content (use Chrome extension)

### Setup

1. **Install dependencies:**
```bash
cd synapse-desktop
npm install
```

2. **Make sure backend is running:**
```bash
cd ../synapse-app/backend
python -m uvicorn app.main:app --reload
```

3. **Start the Electron app:**
```bash
cd ../synapse-desktop
npm start
```

Or in development mode:
```bash
npm run dev
```

## Usage

### Navigation

**Left Sidebar:**
- **Mind Map** - Main visualization view
- **Spaces** - View and manage your collections
- **+ Create Space** - Make a new collection
- **Setup Guide** - Quick start instructions
- **Settings** - App configuration

**Mind Map Canvas:**
- **Click node** - View details in right panel
- **Cmd/Ctrl + Click** - Multi-select nodes
- **Drag** - Reposition nodes
- **Scroll** - Zoom in/out
- **Drag background** - Pan around

**Search (Bottom Center):**
- **Click** or **Cmd+K** - Open search
- **Type query** - Semantic search across all captures
- **Click result** - View full details
- **Esc** - Close search

### Creating Spaces

**Method 1: From Selected Nodes**
1. Hold Cmd/Ctrl and click multiple nodes
2. Click "Group into Space" button (top right)
3. Enter a name
4. Space created!

**Method 2: Empty Space**
1. Click "+ Create Space" in sidebar
2. Enter a name
3. Manually add nodes later

### Keyboard Shortcuts

- **Cmd+K / Ctrl+K** - Open search
- **Esc** - Close panels/search
- **Cmd/Ctrl + Click** - Multi-select nodes

## Architecture

```
synapse-desktop/
├── main.js         # Electron main process
├── index.html      # UI structure
├── app.js          # Mind map & interaction logic
└── package.json    # Dependencies & build config
```

### Technology Stack

- **Electron** - Desktop framework
- **D3.js** - Mind map force simulation
- **Tailwind CSS** - Styling (via CDN)
- **IPC** - Communication with FastAPI backend

### Data Flow

```
Desktop App (Electron)
    ↓ IPC
Backend API (FastAPI)
    ↓
Qdrant (Semantic Search) + Supabase (Structured Data)
```

## Color Scheme

| Content Type | Color | Hex |
|---|---|---|
| Article | Violet | #8b5cf6 |
| Product | Pink | #ec4899 |
| Video | Amber | #f59e0b |
| Code | Emerald | #10b981 |
| Chat | Blue | #3b82f6 |
| Default | Indigo | #6366f1 |

## Building for Production

### Windows
```bash
npm run build
```
Output: `dist/Synapse Setup.exe`

### macOS
```bash
npm run build
```
Output: `dist/Synapse.dmg`

### Linux
```bash
npm run build
```
Output: `dist/Synapse.AppImage`

## Troubleshooting

### "No captures found"
- Make sure backend is running
- Capture some pages with Chrome extension (Alt+B)
- Refresh the app

### "Search not working"
- Check backend is running on port 8000
- Test backend: `curl http://localhost:8000/api/health`
- Check browser console for errors

### "Nodes overlapping"
- Zoom out (scroll)
- Drag nodes to reposition
- Restart simulation (refresh app)

### "Mind map not rendering"
- Check browser console for D3.js errors
- Make sure you have captures in database
- Try refreshing (Cmd+R / Ctrl+R)

## Customization

### Changing Colors

Edit `app.js`:
```javascript
const COLORS = {
    article: '#8b5cf6',  // Change these hex values
    product: '#ec4899',
    // ...
};
```

### Adjusting Force Simulation

Edit `initializeMindMap()` in `app.js`:
```javascript
simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-300)) // Repulsion
    .force('link', d3.forceLink(links).distance(150))  // Link length
    .force('collision', d3.forceCollide().radius(50)); // Node spacing
```

### Changing Node Size

Edit CSS in `index.html`:
```css
node.append('circle')
    .attr('r', 30)  // Change radius here
```

## Roadmap

- [ ] Drag & drop nodes into Spaces
- [ ] Timeline view (chronological)
- [ ] Graph view (hierarchical)
- [ ] Export to Markdown/PDF
- [ ] Local LLM integration for offline Q&A
- [ ] Sync across devices
- [ ] Mobile companion app

## Performance Notes

- **Recommended**: < 500 nodes for smooth interaction
- **Maximum**: ~2000 nodes (may slow down)
- **Optimization**: Use Spaces to filter and focus on subsets

For large knowledge bases (>1000 captures), consider:
1. Creating focused Spaces for specific topics
2. Using search instead of viewing all nodes
3. Implementing lazy loading (future feature)

## License

MIT

## Support

- GitHub Issues: [Report bugs](https://github.com/yourname/synapse)
- Documentation: See `SETUP_GUIDE.md` in project root
- Questions: [Discussions](https://github.com/yourname/synapse/discussions)

---

**Built with ❤️ for knowledge workers, researchers, and lifelong learners.**
