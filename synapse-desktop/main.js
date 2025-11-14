const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  console.log('Creating window...');

  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    backgroundColor: '#111827', // bg-gray-900
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    show: true  // Show immediately for debugging
  });

  console.log('Loading index.html...');
  mainWindow.loadFile('index.html');

  // Always open DevTools for debugging
  mainWindow.webContents.openDevTools();

  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page loaded successfully!');
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load:', errorCode, errorDescription);
  });

  mainWindow.on('closed', () => {
    console.log('Window closed');
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for backend communication
ipcMain.handle('search-captures', async (event, query) => {
  // Forward to backend API
  const axios = require('axios');
  console.log('[IPC] Search request:', query);

  try {
    const response = await axios.get(`http://localhost:8000/api/search`, {
      params: { q: query, limit: 20 },
      timeout: 10000
    });
    console.log('[IPC] Search response:', response.data?.length, 'results');
    return response.data;
  } catch (error) {
    console.error('[IPC] Search error:', error.message);
    if (error.code === 'ECONNREFUSED') {
      return [];  // Return empty array instead of error object
    }
    return [];
  }
});

ipcMain.handle('get-captures', async (event, limit = 50) => {
  const axios = require('axios');
  console.log('[IPC] Get captures request, limit:', limit);

  try {
    const response = await axios.get(`http://localhost:8000/api/captures`, {
      params: { limit },
      timeout: 10000
    });
    console.log('[IPC] Got', response.data?.length, 'captures');
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('[IPC] Get captures error:', error.message);
    return [];  // Return empty array
  }
});

ipcMain.handle('ask-question', async (event, question) => {
  const axios = require('axios');
  console.log('[IPC] Ask question:', question);

  try {
    const response = await axios.post(`http://localhost:8000/api/chat`, {
      question: question
    }, {
      timeout: 30000  // 30 seconds for RAG processing
    });
    console.log('[IPC] Chat response received');
    return response.data;
  } catch (error) {
    console.error('[IPC] Ask question error:', error.message);
    return {
      answer: 'Failed to get answer. Please check if the backend is running.',
      sources: [],
      confidence: 'none'
    };
  }
});

ipcMain.handle('get-capture-detail', async (event, captureId) => {
  const axios = require('axios');
  try {
    const response = await axios.get(`http://localhost:8000/api/capture/${captureId}`);
    return response.data;
  } catch (error) {
    console.error('Get capture detail error:', error);
    return { error: error.message };
  }
});

ipcMain.handle('open-external', async (event, url) => {
  try {
    await shell.openExternal(url);
    return { success: true };
  } catch (error) {
    console.error('Open external error:', error);
    return { error: error.message };
  }
});
