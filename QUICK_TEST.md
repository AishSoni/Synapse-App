# Quick Extension Test (2 Minutes)

Let's test the extension RIGHT NOW without any external setup!

## Step 1: Start Mock Backend (30 seconds)

Open a terminal and run:

```bash
cd E:\Appointy_Task_1\synapse-app\backend
python test_server.py
```

You should see:
```
🚀 Starting Synapse Test Server...
============================================================
Server running at: http://localhost:8000
```

**Keep this terminal open!**

---

## Step 2: Load Extension in Chrome (1 minute)

1. Open **Google Chrome**
2. Type in address bar: `chrome://extensions/`
3. **Enable "Developer mode"** (toggle in top-right corner)
4. Click **"Load unpacked"** button
5. Navigate to: `E:\Appointy_Task_1\synapse-extension`
6. Click **"Select Folder"**

You should see:
- Synapse extension card appears
- Purple "S" icon in your toolbar
- No errors

---

## Step 3: Test the Capture! (30 seconds)

1. Open a new tab
2. Go to any website (try: https://wikipedia.org)
3. Press **`Alt+B`**

**What you should see:**
- ⚡ Quick white flash on the page
- 🟣 Purple toast notification appears (top-right): "Captured"
- 🔊 Sound plays (if you added capture.mp3)

**In your terminal:**
```
============================================================
📸 CAPTURE RECEIVED!
============================================================
URL:        https://wikipedia.org/
Title:      Wikipedia
Content:    1234 characters
Screenshot: 45.2 KB
============================================================
```

---

## ✅ Success Checklist

If you saw all of this, **the extension works perfectly!**

- [x] White flash appeared
- [x] "Captured" toast showed
- [x] Terminal logged the capture
- [x] No errors in Chrome console

---

## 🐛 Troubleshooting

### Nothing happened when I pressed Ctrl+Shift+S

**Check #1:** Is the extension loaded?
- Go to `chrome://extensions/`
- Find "Synapse"
- Should say "Errors: 0"

**Check #2:** Is the shortcut registered?
- Go to `chrome://extensions/shortcuts`
- Find "Synapse - Capture this moment"
- Should show `Ctrl+Shift+S`
- If not, click and set it

**Check #3:** Reload the page and try again
- Refresh the Wikipedia page
- Try `Ctrl+Shift+S` again

### I saw the flash but no toast notification

**This is OK!** The content script might not have loaded yet.

Try:
1. Refresh the page
2. Wait 2 seconds
3. Try capturing again

### Backend error in terminal

**Check:** Is port 8000 already in use?

Try:
```bash
# Kill anything on port 8000
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /F /PID <pid_number>

# Restart test server
python test_server.py
```

### Extension not loading

**Check:** Are icons present?
```bash
ls synapse-extension/icons/
```

Should show:
- icon16.png
- icon32.png
- icon48.png
- icon128.png

If missing:
```bash
cd synapse-extension/icons
python generate_icons.py
```

---

## 🎉 Next Steps

Once the test works:

1. **Add sound** (optional):
   - Download a short click/shutter sound
   - Save as `synapse-extension/capture.mp3`
   - Reload extension
   - Test again

2. **Test on different sites**:
   - GitHub
   - Reddit
   - News articles
   - Product pages
   - Verify capture works everywhere

3. **Move to full setup**:
   - Set up real backend with Supabase
   - Build the Electron app
   - Create the full experience

---

## 🚀 Ready to Test?

**Commands summary:**

```bash
# Terminal 1: Start test server
cd E:\Appointy_Task_1\synapse-app\backend
python test_server.py

# Chrome: Load extension
chrome://extensions/
→ Developer mode ON
→ Load unpacked
→ Select: E:\Appointy_Task_1\synapse-extension

# Test: Open any website
→ Press Ctrl+Shift+S
→ See flash + toast + terminal log
```

**Let me know when you're ready and I'll help you through each step!**
