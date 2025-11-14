"""
Mock backend server for testing the Synapse extension
Run this to test the extension without setting up external services
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Synapse Test Server")

# Enable CORS for extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Synapse Test Server is running", "status": "OK"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "mode": "test"}

@app.post("/api/capture")
async def test_capture(
    url: str = Form(...),
    title: str = Form(...),
    html: str = Form(...),
    screenshot: UploadFile = File(...)
):
    """Mock capture endpoint - just logs and returns success"""

    # Read screenshot to get size
    screenshot_data = await screenshot.read()
    screenshot_size = len(screenshot_data)

    # Log what we received
    print("\n" + "="*60)
    print("CAPTURE RECEIVED!")
    print("="*60)
    print(f"URL:        {url}")
    print(f"Title:      {title}")
    print(f"Content:    {len(html)} characters")
    print(f"Screenshot: {screenshot_size:,} bytes ({screenshot_size/1024:.1f} KB)")
    print("="*60 + "\n")

    # Return success
    return JSONResponse({
        "success": True,
        "message": "Capture received by test server",
        "data": {
            "url": url,
            "title": title,
            "content_length": len(html),
            "screenshot_size": screenshot_size
        }
    })

@app.get("/api/captures")
async def get_captures():
    """Mock endpoint - returns empty list"""
    return []

if __name__ == "__main__":
    print("\n" + "Starting Synapse Test Server...")
    print("="*60)
    print("This is a MOCK server for testing the extension")
    print("It will receive captures but not store them")
    print("="*60)
    print("\nServer running at: http://localhost:8000")
    print("API docs at:       http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
