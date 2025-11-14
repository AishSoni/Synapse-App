// Listen for keyboard shortcut - INSTANT capture
chrome.commands.onCommand.addListener((command) => {
  if (command === 'capture-page') {
    captureInstantly();
  }
});

async function captureInstantly() {
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.id) {
      console.error('No active tab');
      return;
    }

    // Ignore chrome:// pages and extension pages
    if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) {
      console.log('Cannot capture chrome pages');
      return;
    }

    // Trigger visual feedback FIRST (instant response)
    chrome.tabs.sendMessage(tab.id, { action: 'showCaptureFeedback' }).catch(() => {
      // Content script might not be loaded yet, that's OK
    });

    // Capture in parallel for speed
    const [pageData, screenshot] = await Promise.all([
      // Get page data
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: extractPageData
      }).then(results => results[0].result),

      // Capture screenshot
      chrome.tabs.captureVisibleTab(null, {
        format: 'jpeg', // JPEG is faster and smaller than PNG
        quality: 85
      })
    ]);

    // Convert screenshot to blob
    const screenshotBlob = await (await fetch(screenshot)).blob();

    // Send to backend (fire and forget - don't wait)
    sendToBackend(pageData, screenshotBlob);

  } catch (error) {
    console.error('Capture error:', error);
  }
}

// Extract page data - runs in page context
function extractPageData() {
  // User's browser has already rendered the page - capture FULL HTML
  // This is more reliable than any headless browser scraping

  return {
    url: window.location.href,
    title: document.title,
    html: document.documentElement.outerHTML, // Full HTML - no limits!
    timestamp: new Date().toISOString()
  };
}

// Send to backend asynchronously
async function sendToBackend(pageData, screenshotBlob) {
  try {
    const formData = new FormData();
    formData.append('url', pageData.url);
    formData.append('title', pageData.title);
    formData.append('html', pageData.html);
    formData.append('screenshot', screenshotBlob, 'screenshot.jpg');

    const response = await fetch('http://localhost:8000/api/capture', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (!data.success) {
      console.error('Backend error:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
    // Silently fail - don't interrupt user
  }
}

// Keep service worker alive
chrome.runtime.onInstalled.addListener(() => {
  console.log('Synapse extension installed');
});
