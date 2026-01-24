/**
 * Type definitions for Electron IPC API exposed via preload script
 *
 * This makes window.electronAPI available in TypeScript with full type safety
 */

export interface CredentialResult {
  success: boolean;
  error?: string;
}

export interface CredentialGetResult extends CredentialResult {
  value?: string | null;
}

export interface CredentialListResult extends CredentialResult {
  credentials?: Array<{
    provider: string;
    type: string;
  }>;
}

export interface ElectronAPI {
  credentials: {
    /**
     * Store a credential securely
     */
    store: (
      provider: string,
      type: string,
      value: string
    ) => Promise<CredentialResult>;

    /**
     * Retrieve a credential
     */
    get: (
      provider: string,
      type: string
    ) => Promise<CredentialGetResult>;

    /**
     * Delete a credential
     */
    delete: (
      provider: string,
      type: string
    ) => Promise<CredentialResult>;

    /**
     * List all stored credentials
     */
    list: () => Promise<CredentialListResult>;

    /**
     * Check if encryption is available on this platform
     */
    isAvailable: () => Promise<{ available: boolean }>;
  };

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
