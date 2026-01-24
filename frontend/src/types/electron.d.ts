/**
 * Type definitions for Electron IPC API exposed via preload script
 *
 * This makes window.electronAPI available in TypeScript with full type safety
 */

export interface ElectronAPI {
  platform: {
    /**
     * Get the current platform
     */
    getPlatform: () => Promise<string>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
