/**
 * Credential Service
 *
 * Manages secure credential storage using Electron safeStorage
 * and backend credential API.
 *
 * Architecture:
 * 1. Frontend stores credentials encrypted via Electron safeStorage (OS-level encryption)
 * 2. On app startup or when changed, credentials are sent to backend
 * 3. Backend keeps them in memory for LLM provider initialization
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export type CredentialProvider = 'anthropic' | 'google' | 'openai';
export type CredentialType = 'api-key' | 'token';

export interface Credential {
  provider: CredentialProvider;
  type: CredentialType;
  value?: string; // Only present when retrieved
}

export interface CredentialMetadata {
  provider: string;
  type: string;
}

export interface CredentialServiceResult {
  success: boolean;
  error?: string;
}

/**
 * Check if running in Electron with credential API available
 */
export function isElectronCredentialAPIAvailable(): boolean {
  return typeof window !== 'undefined' && !!window.electronAPI?.credentials;
}

/**
 * Check if encryption is available on this platform
 */
export async function isEncryptionAvailable(): Promise<boolean> {
  if (!isElectronCredentialAPIAvailable()) {
    return false;
  }

  try {
    const result = await window.electronAPI.credentials.isAvailable();
    return result.available;
  } catch (error) {
    console.error('[CredentialService] Failed to check encryption availability:', error);
    return false;
  }
}

/**
 * Store a credential both in Electron secure storage and backend
 */
export async function storeCredential(
  provider: CredentialProvider,
  type: CredentialType,
  value: string
): Promise<CredentialServiceResult> {
  if (!isElectronCredentialAPIAvailable()) {
    return {
      success: false,
      error: 'Electron credential API not available. Are you running in Electron?',
    };
  }

  try {
    // 1. Store in Electron secure storage (encrypted on disk)
    const electronResult = await window.electronAPI.credentials.store(provider, type, value);
    if (!electronResult.success) {
      return {
        success: false,
        error: electronResult.error || 'Failed to store credential in secure storage',
      };
    }

    // 2. Send to backend for runtime use
    const backendResponse = await axios.post(`${API_BASE_URL}/credentials/store`, {
      provider,
      type,
      value,
    });

    if (!backendResponse.data.success) {
      return {
        success: false,
        error: backendResponse.data.message || 'Failed to store credential in backend',
      };
    }

    return { success: true };
  } catch (error) {
    console.error('[CredentialService] Store failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Retrieve a credential from Electron secure storage
 */
export async function getCredential(
  provider: CredentialProvider,
  type: CredentialType
): Promise<{ success: boolean; value?: string; error?: string }> {
  if (!isElectronCredentialAPIAvailable()) {
    return {
      success: false,
      error: 'Electron credential API not available',
    };
  }

  try {
    const result = await window.electronAPI.credentials.get(provider, type);
    return result;
  } catch (error) {
    console.error('[CredentialService] Get failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Delete a credential from both Electron storage and backend
 */
export async function deleteCredential(
  provider: CredentialProvider,
  type: CredentialType
): Promise<CredentialServiceResult> {
  if (!isElectronCredentialAPIAvailable()) {
    return {
      success: false,
      error: 'Electron credential API not available',
    };
  }

  try {
    // 1. Delete from Electron storage
    const electronResult = await window.electronAPI.credentials.delete(provider, type);
    if (!electronResult.success) {
      return {
        success: false,
        error: electronResult.error || 'Failed to delete credential from secure storage',
      };
    }

    // 2. Delete from backend
    await axios.delete(`${API_BASE_URL}/credentials/${provider}/${type}`);

    return { success: true };
  } catch (error) {
    console.error('[CredentialService] Delete failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * List all stored credentials (metadata only, no values)
 */
export async function listCredentials(): Promise<{
  success: boolean;
  credentials?: CredentialMetadata[];
  error?: string;
}> {
  if (!isElectronCredentialAPIAvailable()) {
    return {
      success: false,
      error: 'Electron credential API not available',
    };
  }

  try {
    const result = await window.electronAPI.credentials.list();
    return result;
  } catch (error) {
    console.error('[CredentialService] List failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Sync credentials from Electron storage to backend
 *
 * Call this on app startup to ensure backend has latest credentials
 */
export async function syncCredentialsToBackend(): Promise<CredentialServiceResult> {
  if (!isElectronCredentialAPIAvailable()) {
    return {
      success: false,
      error: 'Electron credential API not available',
    };
  }

  try {
    const listResult = await listCredentials();
    if (!listResult.success || !listResult.credentials) {
      return {
        success: false,
        error: listResult.error || 'Failed to list credentials',
      };
    }

    // Send each credential to backend
    for (const credMeta of listResult.credentials) {
      const getResult = await window.electronAPI.credentials.get(
        credMeta.provider,
        credMeta.type
      );

      if (getResult.success && getResult.value) {
        await axios.post(`${API_BASE_URL}/credentials/store`, {
          provider: credMeta.provider,
          type: credMeta.type,
          value: getResult.value,
        });
      }
    }

    return { success: true };
  } catch (error) {
    console.error('[CredentialService] Sync failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}
