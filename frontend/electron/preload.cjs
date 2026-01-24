/**
 * Preload script for Electron IPC bridge
 *
 * This script runs in an isolated context with access to both Node.js and browser APIs.
 * It exposes a safe, limited API to the renderer process via contextBridge.
 *
 * Security: Only expose the minimal API needed. Never expose raw Node.js modules.
 */

const { contextBridge, ipcRenderer } = require('electron');

/**
 * Exposed API for Electron
 * Available in renderer as window.electronAPI
 */
contextBridge.exposeInMainWorld('electronAPI', {
  /**
   * Platform information
   */
  platform: {
    /**
     * Get the current platform
     * @returns {Promise<string>} - 'win32', 'darwin', or 'linux'
     */
    getPlatform: () => ipcRenderer.invoke('platform:get'),
  },
});
