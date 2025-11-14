# Synapse - Packaging Summary

## ✅ Packaged Components

### 1. Chrome Extension ✅
**Location:** `synapse-chrome-extension.zip` (2.6 KB)

**Install:**
```bash
1. Extract ZIP file
2. Chrome → chrome://extensions/
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select extracted folder
```

**Rebuild if needed:**
```bash
cd synapse-extension
powershell -command "Compress-Archive -Path manifest.json,background.js,content.js -DestinationPath ../synapse-chrome-extension.zip -Force"
```

---

### 2. Desktop Application ✅
**Location:** `synapse-desktop/dist/Synapse 1.0.0.exe` (67 MB)

**Type:** Portable executable (no installation required!)

**Install:**
- Download and double-click to run
- No admin rights needed
- Works on Windows 10+ (x64)

**Rebuild if needed:**
```bash
cd synapse-desktop
npm install
npm run build
# Output: dist/Synapse 1.0.0.exe
```

---

### 3. Backend (Not Packaged - See Deployment Options)

**Local Development:**
```bash
cd synapse-app/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Options:**
- Docker (recommended)
- Cloud platforms (Render, Railway, Heroku)
- Linux systemd service
- See DISTRIBUTION.md for detailed instructions

---

## 📦 Distribution Package Structure

```
synapse-distribution/
├── synapse-chrome-extension.zip    # Chrome extension
├── Synapse 1.0.0.exe               # Desktop app (portable)
├── DISTRIBUTION.md                  # Full distribution guide
├── SETUP_GUIDE.md                   # User setup instructions
└── backend/                         # Backend source code
    ├── requirements.txt
    ├── .env.example
    └── app/
```

---

## 🚀 Quick Start for End Users

### 1. Prerequisites
- Windows 10 or later
- Google Chrome browser
- Backend running (local or cloud)

### 2. Installation Steps

**Step 1: Install Chrome Extension**
```
1. Extract synapse-chrome-extension.zip
2. Load in Chrome (chrome://extensions/)
3. Enable and grant permissions
```

**Step 2: Run Desktop App**
```
1. Download Synapse 1.0.0.exe
2. Double-click to run (no install needed!)
3. App opens automatically
```

**Step 3: Connect to Backend**
```
Option A (Cloud): Backend already hosted
Option B (Local):
  cd backend
  pip install -r requirements.txt
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 4: Start Capturing**
```
1. Browse to any webpage
2. Press Alt+B to capture
3. See toast: "✓ Captured: [Title]"
4. View in Desktop app mind map
```

---

## 🔧 Developer Build Instructions

### Chrome Extension
```bash
cd synapse-extension
# Edit files as needed
powershell -command "Compress-Archive -Path manifest.json,background.js,content.js -DestinationPath ../synapse-chrome-extension.zip -Force"
```

### Desktop App
```bash
cd synapse-desktop

# Development
npm install
npm start

# Build for distribution
npm run build

# Outputs:
# - dist/Synapse 1.0.0.exe (portable)
# - dist/win-unpacked/ (unpacked files)
```

### Backend
```bash
cd synapse-app/backend

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn app.main:app --reload
```

---

## 📋 Package Verification

### Chrome Extension Checklist
- [ ] ZIP contains manifest.json, background.js, content.js
- [ ] manifest.json version is correct
- [ ] No development files included
- [ ] Size is reasonable (~2-3 KB)

### Desktop App Checklist
- [ ] EXE file is ~67 MB
- [ ] Double-click launches app successfully
- [ ] WebSocket connection works
- [ ] Search and Ask modes functional
- [ ] Mind map renders correctly

### Backend Checklist
- [ ] All dependencies in requirements.txt
- [ ] .env.example has all required variables
- [ ] Health endpoint returns 200: `/api/health`
- [ ] CORS allows frontend requests
- [ ] WebSocket endpoint accessible: `/ws`

---

## 🐛 Common Packaging Issues

### Extension won't load in Chrome
**Fix:** Check manifest.json is valid JSON
```bash
# Validate
python -c "import json; json.load(open('manifest.json'))"
```

### Desktop app won't start
**Fix:** Missing dependencies
```bash
cd synapse-desktop
npm install
npm run build
```

### Desktop app "Backend not running"
**Fix:** Verify backend is accessible
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","timestamp":"..."}
```

---

## 📊 File Sizes Reference

| Component | Size | Notes |
|-----------|------|-------|
| Chrome Extension ZIP | 2.6 KB | Very small, quick download |
| Desktop App EXE | 67 MB | Includes Electron + dependencies |
| Backend (source) | ~500 KB | Python files only |
| Backend (with venv) | ~200 MB | Includes all Python packages |

---

## 🔄 Update Workflow

### Extension Updates
1. Edit source files in `synapse-extension/`
2. Increment version in manifest.json
3. Run package script
4. Upload new ZIP to Chrome Web Store
5. Users auto-update within 24 hours

### Desktop App Updates
1. Edit source files in `synapse-desktop/`
2. Update version in package.json
3. Run `npm run build`
4. Distribute new EXE file
5. Users manually download and replace

### Backend Updates
1. Git pull or update source
2. `pip install -r requirements.txt` if deps changed
3. Restart service
4. No user action needed (if centrally hosted)

---

## 🎯 Distribution Channels

### Chrome Extension
- **Chrome Web Store** (recommended)
  - Automatic updates
  - User reviews and ratings
  - Built-in distribution

- **Direct Distribution**
  - Provide ZIP file
  - Users load as unpacked
  - Manual updates

### Desktop App
- **GitHub Releases**
  - Tag releases with version
  - Attach EXE file
  - Users download directly

- **Website Download**
  - Host EXE on your server
  - Provide download link
  - Track downloads

- **Enterprise Distribution**
  - Internal network share
  - MSI installer (requires nsis target)
  - Group policy deployment

### Backend
- **Cloud Platform** (easiest for users)
  - Deploy to Render/Railway/Heroku
  - Provide hosted URL
  - Users just configure endpoint

- **Docker Hub**
  - Publish Docker image
  - Users run with docker-compose
  - Easy updates

- **Self-Hosted Guide**
  - Provide deployment docs
  - Users run on own infrastructure
  - Full control and privacy

---

## 📝 Version Information

**Current Version:** 1.0.0

**Build Date:** November 14, 2025

**Components:**
- Chrome Extension: 1.0.0
- Desktop App: 1.0.0
- Backend API: 1.0.0

---

## 📞 Support

For packaging or distribution questions:
- See DISTRIBUTION.md for detailed deployment guide
- Check SETUP_GUIDE.md for user installation help
- GitHub Issues for bug reports
- Community Discord for help

---

**Next Steps:**
1. Test all packaged components
2. Create setup instructions for end users
3. Deploy backend to cloud platform
4. Submit extension to Chrome Web Store
5. Create release on GitHub with downloads
