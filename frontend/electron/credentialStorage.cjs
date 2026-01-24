/**
 * Credential Storage Service
 *
 * Secure credential storage using Electron safeStorage API
 * - Windows: DPAPI (Data Protection API)
 * - macOS: Keychain
 * - Linux: libsecret
 *
 * Storage format: Encrypted files in userData directory
 * Key format: babblr_cred_{provider}_{type}.enc
 */

const { safeStorage, app } = require('electron');
const fs = require('fs').promises;
const path = require('path');

class CredentialStorageService {
  constructor() {
    // Store credentials in Electron's userData directory
    // This ensures proper permissions and platform-specific locations
    this.storageDir = path.join(app.getPath('userData'), 'credentials');
    this._ensureStorageDir();
  }

  /**
   * Ensure the credentials directory exists
   */
  async _ensureStorageDir() {
    try {
      await fs.mkdir(this.storageDir, { recursive: true });
    } catch (error) {
      console.error('[CredentialStorage] Failed to create storage directory:', error);
      throw new Error('Failed to initialize credential storage');
    }
  }

  /**
   * Generate storage key for a credential
   * @param {string} provider - Provider name
   * @param {string} type - Credential type
   * @returns {string} Storage key
   */
  _storageKey(provider, type) {
    // Sanitize provider and type to prevent path traversal
    const sanitize = str => str.replace(/[^a-zA-Z0-9_-]/g, '_');
    return `babblr_cred_${sanitize(provider)}_${sanitize(type)}.enc`;
  }

  /**
   * Get file path for a credential
   * @param {string} provider - Provider name
   * @param {string} type - Credential type
   * @returns {string} File path
   */
  _getFilePath(provider, type) {
    const key = this._storageKey(provider, type);
    return path.join(this.storageDir, key);
  }

  /**
   * Check if encryption is available on this platform
   * @returns {boolean}
   */
  isEncryptionAvailable() {
    return safeStorage.isEncryptionAvailable();
  }

  /**
   * Store a credential securely
   * @param {string} provider - Provider name (e.g., 'anthropic', 'google')
   * @param {string} type - Credential type (e.g., 'api-key', 'token')
   * @param {string} value - Credential value to encrypt
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async storeCredential(provider, type, value) {
    try {
      // Validate inputs
      if (!provider || !type || !value) {
        return {
          success: false,
          error: 'Provider, type, and value are required',
        };
      }

      // Check if encryption is available
      if (!this.isEncryptionAvailable()) {
        return {
          success: false,
          error: 'Encryption not available on this platform',
        };
      }

      // Ensure storage directory exists
      await this._ensureStorageDir();

      // Encrypt the credential
      const encrypted = safeStorage.encryptString(value);

      // Write to file
      const filePath = this._getFilePath(provider, type);
      await fs.writeFile(filePath, encrypted);

      console.log(`[CredentialStorage] Stored credential for ${provider}:${type}`);
      return { success: true };
    } catch (error) {
      console.error('[CredentialStorage] Store failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to store credential',
      };
    }
  }

  /**
   * Retrieve a credential
   * @param {string} provider - Provider name
   * @param {string} type - Credential type
   * @returns {Promise<{success: boolean, value?: string, error?: string}>}
   */
  async getCredential(provider, type) {
    try {
      // Validate inputs
      if (!provider || !type) {
        return {
          success: false,
          error: 'Provider and type are required',
        };
      }

      const filePath = this._getFilePath(provider, type);

      // Check if file exists
      try {
        await fs.access(filePath);
      } catch {
        // Credential not found - return success with null value
        return {
          success: true,
          value: null,
        };
      }

      // Read encrypted data
      const encrypted = await fs.readFile(filePath);

      // Decrypt
      const decrypted = safeStorage.decryptString(encrypted);

      return {
        success: true,
        value: decrypted,
      };
    } catch (error) {
      console.error('[CredentialStorage] Get failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to retrieve credential',
      };
    }
  }

  /**
   * Delete a credential
   * @param {string} provider - Provider name
   * @param {string} type - Credential type
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async deleteCredential(provider, type) {
    try {
      // Validate inputs
      if (!provider || !type) {
        return {
          success: false,
          error: 'Provider and type are required',
        };
      }

      const filePath = this._getFilePath(provider, type);

      // Try to delete the file
      try {
        await fs.unlink(filePath);
        console.log(`[CredentialStorage] Deleted credential for ${provider}:${type}`);
      } catch (error) {
        // If file doesn't exist, that's fine (already deleted)
        if (error.code === 'ENOENT') {
          return { success: true };
        }
        throw error;
      }

      return { success: true };
    } catch (error) {
      console.error('[CredentialStorage] Delete failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete credential',
      };
    }
  }

  /**
   * List all stored credentials
   * @returns {Promise<{success: boolean, credentials?: Array<{provider: string, type: string}>, error?: string}>}
   */
  async listCredentials() {
    try {
      // Ensure directory exists
      await this._ensureStorageDir();

      // Read directory
      const files = await fs.readdir(this.storageDir);

      // Parse credential files
      const credentials = files
        .filter(file => file.startsWith('babblr_cred_') && file.endsWith('.enc'))
        .map(file => {
          // Parse: babblr_cred_{provider}_{type}.enc
          const match = file.match(/^babblr_cred_(.+?)_(.+?)\.enc$/);
          if (match) {
            return {
              provider: match[1],
              type: match[2],
            };
          }
          return null;
        })
        .filter(Boolean); // Remove nulls

      return {
        success: true,
        credentials,
      };
    } catch (error) {
      console.error('[CredentialStorage] List failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to list credentials',
      };
    }
  }

  /**
   * Delete all credentials (for testing/cleanup)
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async deleteAll() {
    try {
      const { success, credentials } = await this.listCredentials();
      if (!success) {
        return { success: false, error: 'Failed to list credentials' };
      }

      for (const cred of credentials) {
        await this.deleteCredential(cred.provider, cred.type);
      }

      console.log('[CredentialStorage] Deleted all credentials');
      return { success: true };
    } catch (error) {
      console.error('[CredentialStorage] DeleteAll failed:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete all credentials',
      };
    }
  }
}

// Export singleton instance
module.exports = new CredentialStorageService();
