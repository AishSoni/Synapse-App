import { app, BrowserWindow, globalShortcut } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

function startBackend() {
  console.log('Starting FastAPI backend...');

  // In development, use Python directly
  // In production, use the bundled executable
  const isDev = process.env.NODE_ENV === 'development';

  if (isDev) {
    backendProcess = spawn('python', [
      '-m', 'uvicorn',
      'app.main:app',
      '--port', '8000',
      '--reload'
    ], {
      cwd: path.join(__dirname, '../../backend'),
      shell: true
    });
  } else {
    // Production: run bundled backend executable
    const backendPath = path.join(process.resourcesPath, 'backend', 'main');
    backendProcess = spawn(backendPath);
  }

  backendProcess.stdout?.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr?.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#0a0a0a',
    titleBarStyle: 'hidden',
    frame: false
  });

  // In development, load from webpack-dev-server
  // In production, load from file
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:9000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Start the backend server
  startBackend();

  // Create the main window
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  // Kill backend process when app quits
  if (backendProcess) {
    backendProcess.kill();
  }
});
