# Extension Testing Guide

## Quick Test (2 options)

### Option A: Test with Mock Backend (Fastest - 2 minutes)

Test the extension UI without setting up external services.

### Option B: Test with Full Backend (Complete - 15 minutes)

Test the complete flow including data storage.

---

## Option A: Mock Backend Test (Recommended to start)

### Step 1: Create Mock Backend

We'll create a simple test server that just responds "OK" to captures.

```bash
cd synapse-app/backend
python test_server.py
```

This confirms:
- Extension captures correctly
- Screenshot works
- Visual feedback works
- Network communication works

### Step 2: Load Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Select: `E:\Appointy_Task_1\synapse-extension`

### Step 3: Test Capture

1. Open any website (try Wikipedia)
2. Press `Ctrl+Shift+S`
3. Watch for:
   - White flash
   - "Captured" toast (top-right)
   - Sound (if you added capture.mp3)

### Step 4: Verify Backend Received It

Check the terminal running test_server.py:
- Should show "Received capture" log
- Shows URL, title, screenshot size

---

## Option B: Full Backend Test

### Prerequisites

You'll need API keys for:
- **Supabase** (database) - Free at supabase.com
- **Gemini** (AI) - Free at makersuite.google.com/app/apikey
- **Qdrant** (optional) - Can use local mode

### Step 1: Setup Environment

```bash
cd synapse-app/backend
cp .env.example .env
```

Edit `.env` and add your keys:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=http://localhost:6333
```

### Step 2: Setup Supabase Database

1. Go to https://supabase.com
2. Create new project
3. Go to SQL Editor
4. Run the schema from PROJECT_SETUP.md

### Step 3: Install Dependencies

```bash
cd synapse-app/backend
pip install -r requirements.txt
```

### Step 4: Start Backend

```bash
python -m uvicorn app.main:app --reload
```

Should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 5: Load Extension (same as Option A)

### Step 6: Test Complete Flow

1. Capture a page
2. Check backend logs (should show processing)
3. Check Supabase (should show new row in captures table)
4. Test search endpoint:
   ```bash
   curl "http://localhost:8000/api/captures"
   ```

---

## Which Option Should You Choose?

**Choose Option A if:**
- You want to test the extension UI immediately
- Don't have API keys yet
- Just want to verify the extension works

**Choose Option B if:**
- You want to test the complete system
- Have time to set up external services
- Want to see end-to-end data flow

---

## Let's Start with Option A

I'll create the mock test server now so you can test immediately!
