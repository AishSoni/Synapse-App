# Synapse Chrome Extension

A minimal, non-intrusive thought capture extension.

## Philosophy

**Capture a thought first, a webpage second.**

This extension is designed to be invisible until you need it. No popups, no forms, no distractions. Just one keyboard shortcut to capture the moment and continue.

## Features

- **Instant Capture**: Press `Ctrl+Shift+S` (or `Cmd+Shift+S` on Mac)
- **Subtle Feedback**: Brief camera flash + small toast notification
- **Audio Confirmation**: Gentle sound to confirm capture
- **Zero Friction**: No forms, no popups, no interruptions
- **Fast**: Optimized for speed - captures in milliseconds

## How It Works

1. User finds something worth saving
2. Presses keyboard shortcut
3. Extension captures:
   - Page URL and title
   - Main content (text)
   - Visual screenshot
4. Shows brief visual + audio feedback
5. Sends to Synapse app in background
6. User continues browsing

**Total interruption time: ~0.5 seconds**

## Installation

### For Development

1. Clone the repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `synapse-extension` folder
6. Extension is now active!

### For Users

*(Distribution instructions will be added when published to Chrome Web Store)*

## Usage

1. Browse the web normally
2. When you see something worth capturing:
   - Press `Ctrl+Shift+S` (Windows/Linux)
   - Press `Cmd+Shift+S` (Mac)
3. See a quick flash and "Captured" notification
4. Continue browsing
5. Your capture is saved to the Synapse app

## What Gets Captured

- **URL**: Full page address
- **Title**: Page title
- **Content**: Main text content (up to 10,000 characters)
- **Screenshot**: Visual snapshot of the page
- **Timestamp**: When it was captured

## Privacy

- All data is sent to your local Synapse app (localhost:8000)
- Nothing is sent to external servers
- You own all your data
- No tracking, no analytics

## Keyboard Shortcut

**Default:** `Ctrl+Shift+S` (Windows/Linux) or `Cmd+Shift+S` (Mac)

To change:
1. Go to `chrome://extensions/shortcuts`
2. Find "Synapse"
3. Click the edit icon
4. Set your preferred shortcut

## Troubleshooting

### Extension not capturing?

1. Check that the Synapse app is running
2. Verify backend is accessible at http://localhost:8000
3. Try reloading the extension:
   - Go to `chrome://extensions/`
   - Click refresh icon on Synapse extension
4. Check console for errors:
   - Right-click extension icon → "Inspect popup"
   - Check for error messages

### No visual feedback?

1. Content script might not have loaded
2. Try refreshing the page
3. Check if you're on a restricted page (chrome://, extensions, etc.)

### Sound not playing?

- Browser might be blocking autoplay
- This is normal and doesn't affect functionality
- Visual feedback will still work

## Technical Details

### Files

- `manifest.json` - Extension configuration
- `background.js` - Service worker (handles capture logic)
- `content.js` - Visual feedback on pages
- `content.css` - Styles for feedback UI
- `capture.mp3` - Audio feedback sound
- `icons/` - Extension icons

### Permissions

- `activeTab` - Access current tab data
- `tabs` - Capture screenshots
- `scripting` - Inject content extraction script
- `notifications` - Show capture confirmation

### Performance

- Captures in < 200ms on average
- Uses JPEG compression for screenshots (faster than PNG)
- Limits content extraction to 10,000 characters
- Sends data asynchronously (doesn't block UI)

## Development

### Building

No build step required - it's vanilla JavaScript.

### Testing

1. Load extension in development mode
2. Open any webpage
3. Press keyboard shortcut
4. Check:
   - Visual flash appears
   - Toast notification shows
   - Sound plays
   - Backend receives data

### Debugging

**Background script:**
```
chrome://extensions/ → Synapse → Inspect views: service worker
```

**Content script:**
```
Right-click on page → Inspect → Console
```

## Future Enhancements

- [ ] Offline queue (capture when backend is down)
- [ ] Capture selection (highlight text to capture)
- [ ] Quick tags/notes (optional annotation)
- [ ] Smart content detection (auto-detect products, articles, etc.)
- [ ] Duplicate detection (warn if already captured)

## License

MIT
