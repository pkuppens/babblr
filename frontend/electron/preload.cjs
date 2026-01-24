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
 * Exposed API for credential management
 * Available in renderer as window.electronAPI
 */
contextBridge.exposeInMainWorld('electronAPI', {
  /**
   * Credential Storage API
   * Uses Electron safeStorage (Windows DPAPI, macOS Keychain, Linux libsecret)
   */
  credentials: {
    /**
     * Store a credential securely
     * @param {string} provider - Provider name (e.g., 'anthropic', 'google', 'openai')
     * @param {string} type - Credential type (e.g., 'api-key', 'token')
     * @param {string} value - The credential value to encrypt and store
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    store: (provider, type, value) =>
      ipcRenderer.invoke('credentials:store', { provider, type, value }),

    /**
     * Retrieve a credential
     * @param {string} provider - Provider name
     * @param {string} type - Credential type
     * @returns {Promise<{success: boolean, value?: string, error?: string}>}
     */
    get: (provider, type) =>
      ipcRenderer.invoke('credentials:get', { provider, type }),

    /**
     * Delete a credential
     * @param {string} provider - Provider name
     * @param {string} type - Credential type
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    delete: (provider, type) =>
      ipcRenderer.invoke('credentials:delete', { provider, type }),

    /**
     * List all stored credentials
     * @returns {Promise<{success: boolean, credentials?: Array<{provider: string, type: string}>, error?: string}>}
     */
    list: () =>
      ipcRenderer.invoke('credentials:list'),

    /**
     * Check if encryption is available on this platform
     * @returns {Promise<{available: boolean}>}
     */
    isAvailable: () =>
      ipcRenderer.invoke('credentials:is-available'),
  },

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
