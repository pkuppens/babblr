/**
 * Simple encryption utility for API keys using Web Crypto API
 * This provides basic obfuscation for localStorage storage
 * For production, consider using Electron's safeStorage API
 */

const ENCRYPTION_KEY = 'babblr-encryption-key-v1';
const IV_LENGTH = 16;

/**
 * Generate a consistent key from a passphrase using PBKDF2
 */
async function getEncryptionKey(): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(ENCRYPTION_KEY),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('babblr-salt'),
      iterations: 100000,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt a string value
 */
export async function encrypt(value: string): Promise<string> {
  try {
    const key = await getEncryptionKey();
    const encoder = new TextEncoder();
    const data = encoder.encode(value);

    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
    const encryptedData = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, data);

    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encryptedData.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encryptedData), iv.length);

    // Convert to base64 for storage
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    console.error('Encryption failed:', error);
    throw new Error('Failed to encrypt data');
  }
}

/**
 * Decrypt a string value
 */
export async function decrypt(encryptedValue: string): Promise<string> {
  try {
    const key = await getEncryptionKey();

    // Decode from base64
    const combined = Uint8Array.from(atob(encryptedValue), c => c.charCodeAt(0));

    // Extract IV and encrypted data
    const iv = combined.slice(0, IV_LENGTH);
    const encryptedData = combined.slice(IV_LENGTH);

    const decryptedData = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, encryptedData);

    const decoder = new TextDecoder();
    return decoder.decode(decryptedData);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt data');
  }
}

/**
 * Mask an API key for display (show first 8 and last 4 characters)
 */
export function maskApiKey(apiKey: string): string {
  if (!apiKey || apiKey.length < 12) {
    return '•'.repeat(20);
  }
  const start = apiKey.substring(0, 8);
  const end = apiKey.substring(apiKey.length - 4);
  const masked = '•'.repeat(Math.max(8, apiKey.length - 12));
  return `${start}${masked}${end}`;
}
