const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const credentialStorage = require('./credentialStorage.cjs');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      // Security: Enable context isolation and use preload script
      // This prevents renderer from directly accessing Node.js APIs
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.cjs'),
    },
    autoHideMenuBar: true,
    icon: path.join(__dirname, '../public/icon.png'),
  });

  // In development, load from Vite dev server
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    // Keep the dev server URL configurable so we can evolve the dev setup
    // without having to touch this file again.
    const devServerUrl = process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173';
    win.loadURL(devServerUrl);
    win.webContents.openDevTools();
  } else {
    // In production, load the built files
    win.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

// ============================================================================
// IPC Handlers for Credential Management
// ============================================================================

/**
 * Store a credential securely
 */
ipcMain.handle('credentials:store', async (event, { provider, type, value }) => {
  try {
    console.log(`[IPC] credentials:store - ${provider}:${type}`);
    return await credentialStorage.storeCredential(provider, type, value);
  } catch (error) {
    console.error('[IPC] credentials:store error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
});

/**
 * Retrieve a credential
 */
ipcMain.handle('credentials:get', async (event, { provider, type }) => {
  try {
    console.log(`[IPC] credentials:get - ${provider}:${type}`);
    return await credentialStorage.getCredential(provider, type);
  } catch (error) {
    console.error('[IPC] credentials:get error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
});

/**
 * Delete a credential
 */
ipcMain.handle('credentials:delete', async (event, { provider, type }) => {
  try {
    console.log(`[IPC] credentials:delete - ${provider}:${type}`);
    return await credentialStorage.deleteCredential(provider, type);
  } catch (error) {
    console.error('[IPC] credentials:delete error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
});

/**
 * List all stored credentials
 */
ipcMain.handle('credentials:list', async () => {
  try {
    console.log('[IPC] credentials:list');
    return await credentialStorage.listCredentials();
  } catch (error) {
    console.error('[IPC] credentials:list error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
});

/**
 * Check if encryption is available
 */
ipcMain.handle('credentials:is-available', async () => {
  try {
    const available = credentialStorage.isEncryptionAvailable();
    console.log(`[IPC] credentials:is-available - ${available}`);
    return { available };
  } catch (error) {
    console.error('[IPC] credentials:is-available error:', error);
    return { available: false };
  }
});

/**
 * Get platform information
 */
ipcMain.handle('platform:get', async () => {
  return process.platform;
});

// ============================================================================
// App Lifecycle
// ============================================================================

app.whenReady().then(() => {
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


