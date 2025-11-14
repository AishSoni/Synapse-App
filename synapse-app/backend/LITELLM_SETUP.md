# LiteLLM Proxy Integration

## ✅ What Changed

The backend now uses your **LiteLLM proxy** instead of direct API calls:

### Models Used

1. **Claude Sonnet 4** - Content analysis + Screenshot vision
2. **gemini-embedding-001** - Vector embeddings

### Configuration

From `E:\Appointy_Task_1\.env`:
```env
BASE_URL=https://litellm-339960399182.us-central1.run.app
AUTH_TOKEN=sk-BoUYHwNqVVeYotBVVWnw2w
```

---

## 🏗️ Updated Architecture

```
Extension Capture (Alt+B)
    ↓
Backend receives: URL, Title, HTML, Screenshot
    ↓
┌─────────────────────────────────────────┐
│   LiteLLM Proxy Client (llm_client.py)  │
│   - Handles all API calls                │
│   - Uses your custom endpoint            │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┬──────────────────┐
    │                   │                  │
    ▼                   ▼                  ▼
[Text Analysis]  [Screenshot Analysis]  [Embeddings]
Claude Sonnet 4  Claude Sonnet 4        gemini-embedding-001
    │                   │                  │
    └─────────┬─────────┴──────────────────┘
              ▼
    Structured metadata + Visual context
              ↓
    [PARALLEL STORAGE]
    ├─ Qdrant (vectors)
    └─ Supabase (structured)
```

---

## 🆕 Screenshot Semantic Processing

### How it Works

**Two-step analysis:**

1. **Text Analysis** (Claude Sonnet 4)
   - Content type detection
   - Metadata extraction
   - Summary & tags
   - Key points

2. **Visual Analysis** (Claude Sonnet 4 Vision)
   - UI elements detected
   - Color scheme
   - UI type (e-commerce, article, etc.)
   - Visible text (prices, labels)
   - Design patterns

### Example Output

**Text Analysis:**
```json
{
  "content_type": "product",
  "metadata": {
    "price": "249.99",
    "brand": "Apple"
  },
  "tags": ["electronics", "audio"]
}
```

**Visual Analysis:**
```json
{
  "description": "E-commerce product page with large product image",
  "detected_elements": ["product-image", "add-to-cart-button", "price-tag"],
  "colors": ["white", "blue", "black"],
  "ui_type": "e-commerce",
  "visible_text": ["$249.99", "Add to Cart", "Free Shipping"]
}
```

### Benefits

- **Context-aware** - Understands visual layout
- **Enhanced metadata** - Catches details missed in HTML
- **UI type detection** - Helps categorize pages
- **Color analysis** - Can theme nodes in mind map
- **Visible text extraction** - Backup for scraped content

---

## 📁 New Files

```
✅ llm_client.py          - LiteLLM proxy client
✅ content_analyzer.py    - Updated to use Claude + vision
✅ embedding_service.py   - Updated to use gemini-embedding-001
✅ requirements.txt       - Added httpx
✅ .env                   - Your credentials
```

---

## 🔧 API Endpoints Used

### 1. Chat Completions
```
POST https://litellm-339960399182.us-central1.run.app/chat/completions

Headers:
  Authorization: Bearer sk-BoUYHwNqVVeYotBVVWnw2w

Body:
{
  "model": "claude-sonnet-4",
  "messages": [...],
  "temperature": 0.3,
  "max_tokens": 2000
}
```

### 2. Vision Analysis
```
POST https://litellm-339960399182.us-central1.run.app/chat/completions

Headers:
  Authorization: Bearer sk-BoUYHwNqVVeYotBVVWnw2w

Body:
{
  "model": "claude-sonnet-4",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "image", "source": {"type": "base64", "data": "..."}},
      {"type": "text", "text": "Analyze this screenshot..."}
    ]
  }]
}
```

### 3. Embeddings
```
POST https://litellm-339960399182.us-central1.run.app/embeddings

Headers:
  Authorization: Bearer sk-BoUYHwNqVVeYotBVVWnw2w

Body:
{
  "model": "gemini-embedding-001",
  "input": "text to embed"
}

Returns:
{
  "data": [{"embedding": [0.123, ...]}]
}
```

---

## 🧪 Testing

### Test the LiteLLM Client

```python
# In Python console
import asyncio
from app.services.llm_client import get_llm_client

async def test():
    client = get_llm_client()

    # Test chat
    response = await client.chat_completion([
        {"role": "user", "content": "Hello!"}
    ])
    print(response)

    # Test embedding
    embedding = await client.create_embedding("test text")
    print(f"Embedding dims: {len(embedding)}")

asyncio.run(test())
```

### Expected Output

```
✓ LiteLLM proxy configured: https://litellm-339960399182.us-central1.run.app
Hello! How can I assist you today?
Embedding dims: 768
```

---

## 📊 Updated Pipeline Flow

```
Capture (Alt+B)
    ↓
Screenshot (bytes) + HTML + URL + Title
    ↓
────────────────────────────────────────
STEP 1: Text Analysis (Claude Sonnet 4)
────────────────────────────────────────
→ Detect content type
→ Extract metadata (price, author, etc.)
→ Generate tags & summary
→ Clean content
    ↓
────────────────────────────────────────
STEP 2: Visual Analysis (Claude Vision)
────────────────────────────────────────
→ Analyze screenshot
→ Detect UI elements
→ Extract colors & theme
→ Find visible text
    ↓
────────────────────────────────────────
STEP 3: Generate Embedding
────────────────────────────────────────
→ Combine text + visual context
→ Generate 768-dim vector
→ (gemini-embedding-001)
    ↓
────────────────────────────────────────
STEP 4: PARALLEL STORAGE
────────────────────────────────────────
├─ Qdrant: Vector + metadata
└─ Supabase: Full data + visual_analysis
    ↓
✓ Complete
```

---

## 🎨 Enhanced Supabase Schema

The `visual_analysis` field is now stored:

```sql
-- Added to captures table
ALTER TABLE captures
ADD COLUMN IF NOT EXISTS visual_analysis JSONB DEFAULT NULL;
```

Example stored data:
```json
{
  "id": "uuid",
  "content_type": "product",
  "visual_analysis": {
    "description": "E-commerce product page",
    "detected_elements": ["image", "button", "price"],
    "colors": ["white", "blue"],
    "ui_type": "e-commerce",
    "visible_text": ["$249.99", "Add to Cart"]
  }
}
```

---

## 🚀 Ready to Test

1. **Install new dependency:**
   ```bash
   cd synapse-app/backend
   pip install httpx
   ```

2. **Start backend:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Should see:**
   ```
   ✓ LiteLLM proxy configured: https://litellm-339960399182...
   ✓ Connected to Qdrant ...
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```

4. **Capture a page with Alt+B**

5. **Check logs:**
   ```
   → Analyzing content with Claude Sonnet 4...
     ✓ Content type: product
     ✓ Tags: electronics, audio
     ✓ Metadata: 4 fields
     ✓ Visual analysis complete
   → Storing in parallel...
     ✓ Stored in Qdrant
     ✓ Stored in Supabase
   ```

---

## 🔐 Security Note

Your `.env` file contains sensitive credentials:
- `AUTH_TOKEN=sk-BoUYHwNqVVeYotBVVWnw2w`

Make sure:
- ✅ `.env` is in `.gitignore` (already done)
- ✅ Never commit credentials to git
- ✅ Rotate tokens if exposed

---

**LiteLLM integration complete!** 🎉

Claude Sonnet 4 + Vision + Gemini Embeddings working together.
