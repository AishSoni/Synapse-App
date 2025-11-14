# Synapse - Distribution Guide

## 📦 Package Contents

This guide covers how to distribute and install Synapse components:

1. **Chrome Extension** - Web page capture
2. **Desktop App** - Mind map visualization and search
3. **Backend** - AI processing and database

---

## 1. Chrome Extension Distribution

### Package Location
- **File:** `synapse-chrome-extension.zip` (2.6 KB)
- **Contents:**
  - `manifest.json` - Extension configuration
  - `background.js` - Service worker
  - `content.js` - Page capture script

### Installation Instructions

#### For End Users (Developer Mode)
1. Download `synapse-chrome-extension.zip`
2. Extract to a folder on your computer
3. Open Chrome and go to `chrome://extensions/`
4. Enable "Developer mode" (toggle in top right)
5. Click "Load unpacked"
6. Select the extracted folder
7. The extension is now installed!

#### For Chrome Web Store Publishing
1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Click "New Item"
3. Upload `synapse-chrome-extension.zip`
4. Fill in store listing details:
   - **Name:** Synapse - AI-Powered Second Brain
   - **Description:** Capture web pages with Alt+B and build your personal knowledge base
   - **Category:** Productivity
   - **Screenshots:** Add screenshots of the extension in action
5. Submit for review

#### Usage
- Press **Alt+B** on any webpage to capture it
- Captured pages are sent to your local backend for processing
- View and search captures in the Desktop app

---

## 2. Desktop App Distribution

### Package Location
- **File:** `synapse-desktop/dist/Synapse 1.0.0.exe` (67 MB)
- **Type:** Portable executable (no installation required)

### Installation Instructions

#### For Windows Users
1. Download `Synapse 1.0.0.exe`
2. **No installation needed!** - It's a portable app
3. Double-click to run
4. Grant permissions if Windows Defender asks
5. The app opens and connects to the backend

#### For Distribution
- Upload `Synapse 1.0.0.exe` to your download server
- Users can run it directly without admin rights
- Alternatively, create an installer version:
  ```bash
  cd synapse-desktop
  # Edit package.json: change "portable" to "nsis"
  npm run build
  # Creates an installer at dist/Synapse Setup 1.0.0.exe
  ```

### System Requirements
- **Windows:** Windows 10 or later (x64)
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 200 MB for app + storage for captures
- **Network:** Backend must be running (local or remote)

---

## 3. Backend Deployment

### Local Development
```bash
cd synapse-app/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment Options

#### Option 1: Docker (Recommended)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t synapse-backend .
docker run -p 8000:8000 --env-file .env synapse-backend
```

#### Option 2: Systemd Service (Linux)
Create `/etc/systemd/system/synapse.service`:
```ini
[Unit]
Description=Synapse Backend
After=network.target

[Service]
Type=simple
User=synapse
WorkingDirectory=/opt/synapse/backend
Environment="PATH=/opt/synapse/venv/bin"
ExecStart=/opt/synapse/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable synapse
sudo systemctl start synapse
```

#### Option 3: Cloud Platforms

**Render.com:**
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env`

**Railway.app:**
1. Click "Deploy from GitHub repo"
2. Select `synapse-app/backend`
3. Railway auto-detects Python and runs `uvicorn`
4. Add environment variables

**Heroku:**
Create `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Deploy:
```bash
git init
heroku create synapse-backend
git add .
git commit -m "Deploy backend"
git push heroku main
```

### Environment Variables Required
```bash
# .env file
BASE_URL=https://api.litellm.com  # Or your LLM proxy
AUTH_TOKEN=your_auth_token_here

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

QDRANT_URL=http://localhost:6333  # Or cloud URL
QDRANT_API_KEY=your_qdrant_key  # Optional for cloud
```

### Dependencies
All dependencies are in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client
- `qdrant-client` - Vector database
- `supabase` - Database client
- `python-dotenv` - Environment config

---

## 4. Complete Setup Flow

### For End Users

1. **Download all components:**
   - `synapse-chrome-extension.zip`
   - `Synapse 1.0.0.exe`
   - Backend deployed or running locally

2. **Set up backend (if self-hosting):**
   ```bash
   cd synapse-app/backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Install Chrome extension:**
   - Extract ZIP
   - Load in Chrome (chrome://extensions/)

4. **Run Desktop app:**
   - Double-click `Synapse 1.0.0.exe`
   - App opens and connects to backend

5. **Start using:**
   - Browse to any webpage
   - Press Alt+B to capture
   - Toast notification confirms capture
   - View in Desktop app mind map
   - Search and ask questions

### For Developers

```bash
# Clone repo
git clone <repo-url>
cd synapse

# Backend
cd synapse-app/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
uvicorn app.main:app --reload

# Desktop (new terminal)
cd synapse-desktop
npm install
npm start

# Extension (new terminal)
cd synapse-extension
# Load in Chrome as unpacked extension
```

---

## 5. Architecture Overview

```
┌─────────────────┐
│  Web Browser    │
│  + Extension    │──┐
└─────────────────┘  │
                     │ Alt+B captures page
                     │
                     ↓
┌─────────────────────────────┐
│   Backend (FastAPI)         │
│   • Content Analysis (LLM)  │
│   • Embedding Generation    │
│   • Vector Storage (Qdrant) │
│   • Database (Supabase)     │
│   • WebSocket Server        │
└─────────────────────────────┘
        ↑              ↓
        │              │ Real-time
        │              │ updates
        ↓              ↓
┌─────────────────────────────┐
│   Desktop App (Electron)    │
│   • Mind Map Visualization  │
│   • Semantic Search         │
│   • AI Q&A (RAG)            │
│   • WebSocket Client        │
└─────────────────────────────┘
```

---

## 6. Troubleshooting

### Extension not capturing
- Check backend is running (`http://localhost:8000/api/health`)
- Check CORS is enabled in backend
- Check browser console for errors

### Desktop app can't connect
- Verify backend URL in app settings
- Check firewall isn't blocking port 8000
- Try accessing `http://localhost:8000` in browser

### Backend errors
- Check `.env` file has all required keys
- Verify Supabase and Qdrant are accessible
- Check logs: backend terminal shows detailed errors
- Test LLM connection: `curl http://your-llm-url`

### No captures appearing in mind map
- Check WebSocket connection (console shows `[WS] Connected!`)
- Refresh the desktop app
- Check backend logs for capture processing errors

---

## 7. Security Notes

### For Production
1. **Use HTTPS** for backend
2. **Secure API keys** - use secrets manager
3. **Enable authentication** if exposing publicly
4. **Rate limiting** on endpoints
5. **Sanitize inputs** (already implemented)
6. **Regular updates** for dependencies

### Privacy
- All data stays on your infrastructure
- No third-party tracking
- LLM calls go through your proxy
- Embeddings stored in your Qdrant instance
- Database hosted on your Supabase

---

## 8. Updates and Versioning

### Extension Updates
- Increment version in `manifest.json`
- Rebuild ZIP: `cd synapse-extension && powershell -command "Compress-Archive ..."`
- Publish to Chrome Web Store (auto-updates users)

### Desktop App Updates
- Update version in `package.json`
- Run `npm run build`
- Distribute new `.exe` file
- Users download and replace old version

### Backend Updates
- Git pull latest code
- `pip install -r requirements.txt` (if deps changed)
- Restart service: `systemctl restart synapse` or Docker restart

---

## 9. License and Support

**License:** MIT (adjust as needed)

**Support:**
- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Community: Discord/Slack link

**Contributing:**
- Fork repository
- Create feature branch
- Submit pull request
- Follow code style guidelines

---

## Contact

For questions or support:
- Email: support@synapse.example
- GitHub: github.com/your-org/synapse
- Documentation: docs.synapse.example

---

**Last Updated:** November 2025
**Version:** 1.0.0
