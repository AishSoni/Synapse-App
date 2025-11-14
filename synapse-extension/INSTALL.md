# Synapse Extension - Installation Guide

## Step 1: Create Icons

We need to generate the extension icons first.

1. Open `icons/create_icons.html` in your browser
2. Right-click on each canvas image
3. Select "Save image as..."
4. Save them in the `icons/` folder with these exact names:
   - icon16.png
   - icon32.png
   - icon48.png
   - icon128.png

## Step 2: Add Capture Sound

We need a subtle capture sound. You have two options:

### Option A: Use a free sound
1. Download a short "camera shutter" or "click" sound from:
   - https://freesound.org/
   - https://mixkit.co/free-sound-effects/
2. Save as `capture.mp3` in the extension folder
3. Keep it short (< 1 second) and subtle

### Option B: No sound (temporary)
1. Create an empty file: `capture.mp3`
2. The extension will work fine, just without audio feedback

## Step 3: Load Extension in Chrome

1. Open Chrome browser
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right corner)
4. Click "Load unpacked" button
5. Navigate to the `synapse-extension` folder
6. Select it and click "Open"

## Step 4: Verify Installation

1. You should see "Synapse" in your extensions list
2. The purple "S" icon should appear in your toolbar
3. Try the keyboard shortcut:
   - Windows/Linux: `Ctrl+Shift+S`
   - Mac: `Cmd+Shift+S`

## Step 5: Test Capture

**Note:** The backend must be running for captures to save!

1. Open any website (like Wikipedia)
2. Press `Ctrl+Shift+S` (or `Cmd+Shift+S`)
3. You should see:
   - Quick white flash on the page
   - "Captured" toast notification (top-right)
   - Hear a subtle sound (if you added the audio file)

## Troubleshooting

### Icons not showing?
- Make sure you saved all 4 icon files in the `icons/` folder
- Names must be exact: icon16.png, icon32.png, icon48.png, icon128.png
- Try reloading the extension

### Keyboard shortcut not working?
1. Go to `chrome://extensions/shortcuts`
2. Find "Synapse"
3. Make sure a shortcut is assigned
4. If it conflicts with another extension, change it

### No visual feedback when capturing?
- The page might be blocking the content script
- Try refreshing the page first
- Check browser console for errors (F12)

### Capture not saving?
- Make sure the Synapse backend is running on `http://localhost:8000`
- Check the extension console:
  1. Go to `chrome://extensions/`
  2. Click "Details" on Synapse
  3. Click "Inspect views: service worker"
  4. Check for errors in the console

## Next Steps

Once the extension is installed and working:

1. Make sure the Synapse Electron app is running
2. Start capturing interesting pages!
3. View your captures in the Synapse app

## Updating the Extension

After making changes to the extension code:

1. Go to `chrome://extensions/`
2. Click the refresh icon on the Synapse extension
3. The changes will take effect immediately

---

**Enjoy capturing your thoughts!** 🧠✨
