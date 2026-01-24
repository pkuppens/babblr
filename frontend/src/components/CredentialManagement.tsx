/**
 * Credential Management Component
 *
 * UI for managing API credentials securely stored via Electron safeStorage
 */

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  storeCredential,
  deleteCredential,
  listCredentials,
  isEncryptionAvailable,
  type CredentialProvider,
  type CredentialMetadata,
} from '../services/credentialService';

interface ProviderConfig {
  id: CredentialProvider;
  name: string;
  description: string;
  placeholder: string;
}

const PROVIDERS: ProviderConfig[] = [
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    description: 'Claude API key for conversation generation',
    placeholder: 'sk-ant-...',
  },
  {
    id: 'google',
    name: 'Google Gemini',
    description: 'Gemini API key for conversation generation',
    placeholder: 'AIza...',
  },
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'OpenAI API key for future support',
    placeholder: 'sk-...',
  },
];

export default function CredentialManagement() {
  const [encryptionAvailable, setEncryptionAvailable] = useState<boolean | null>(null);
  const [storedCredentials, setStoredCredentials] = useState<CredentialMetadata[]>([]);
  const [inputValues, setInputValues] = useState<Record<CredentialProvider, string>>({
    anthropic: '',
    google: '',
    openai: '',
  });
  const [showValues, setShowValues] = useState<Record<CredentialProvider, boolean>>({
    anthropic: false,
    google: false,
    openai: false,
  });
  const [loading, setLoading] = useState(false);

  // Check encryption availability on mount
  useEffect(() => {
    checkEncryption();
    loadStoredCredentials();
  }, []);

  const checkEncryption = async () => {
    const available = await isEncryptionAvailable();
    setEncryptionAvailable(available);

    if (!available) {
      toast.error('Secure credential storage not available on this platform');
    }
  };

  const loadStoredCredentials = async () => {
    const result = await listCredentials();
    if (result.success && result.credentials) {
      setStoredCredentials(result.credentials);
    }
  };

  const handleStore = async (provider: CredentialProvider) => {
    const value = inputValues[provider];
    if (!value || !value.trim()) {
      toast.error('Please enter an API key');
      return;
    }

    setLoading(true);
    try {
      const result = await storeCredential(provider, 'api-key', value.trim());
      if (result.success) {
        toast.success(`${PROVIDERS.find(p => p.id === provider)?.name} credential stored securely`);
        setInputValues(prev => ({ ...prev, [provider]: '' }));
        await loadStoredCredentials();
      } else {
        toast.error(result.error || 'Failed to store credential');
      }
    } catch (error) {
      toast.error('Failed to store credential');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (provider: CredentialProvider) => {
    if (!confirm(`Delete ${PROVIDERS.find(p => p.id === provider)?.name} credential?`)) {
      return;
    }

    setLoading(true);
    try {
      const result = await deleteCredential(provider, 'api-key');
      if (result.success) {
        toast.success('Credential deleted');
        await loadStoredCredentials();
      } else {
        toast.error(result.error || 'Failed to delete credential');
      }
    } catch (error) {
      toast.error('Failed to delete credential');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const isStored = (provider: CredentialProvider): boolean => {
    return storedCredentials.some(c => c.provider === provider && c.type === 'api-key');
  };

  if (encryptionAvailable === null) {
    return (
      <div className="credential-management">
        <h3>API Credentials</h3>
        <p>Checking encryption availability...</p>
      </div>
    );
  }

  if (!encryptionAvailable) {
    return (
      <div className="credential-management">
        <h3>API Credentials</h3>
        <div className="credential-error">
          <p>Secure credential storage is not available on this platform.</p>
          <p>
            Please use environment variables (.env file) for API keys during development.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="credential-management">
      <h3>API Credentials</h3>
      <p className="credential-description">
        Store your API keys securely using platform encryption (Windows DPAPI, macOS Keychain, Linux libsecret).
      </p>

      <div className="credential-providers">
        {PROVIDERS.map(provider => {
          const stored = isStored(provider.id);
          return (
            <div key={provider.id} className="credential-provider">
              <div className="credential-provider-header">
                <h4>{provider.name}</h4>
                {stored && <span className="credential-status">Stored</span>}
              </div>
              <p className="credential-provider-description">{provider.description}</p>

              {stored ? (
                <div className="credential-actions">
                  <button
                    onClick={() => handleDelete(provider.id)}
                    disabled={loading}
                    className="credential-button credential-button-delete"
                  >
                    Delete Credential
                  </button>
                </div>
              ) : (
                <div className="credential-input-group">
                  <input
                    type={showValues[provider.id] ? 'text' : 'password'}
                    value={inputValues[provider.id]}
                    onChange={e => setInputValues(prev => ({ ...prev, [provider.id]: e.target.value }))}
                    placeholder={provider.placeholder}
                    className="credential-input"
                    disabled={loading}
                  />
                  <button
                    onClick={() => setShowValues(prev => ({ ...prev, [provider.id]: !prev[provider.id] }))}
                    className="credential-button credential-button-toggle"
                    disabled={loading}
                  >
                    {showValues[provider.id] ? 'Hide' : 'Show'}
                  </button>
                  <button
                    onClick={() => handleStore(provider.id)}
                    disabled={loading || !inputValues[provider.id].trim()}
                    className="credential-button credential-button-save"
                  >
                    Save
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="credential-info">
        <h4>Security Information</h4>
        <ul>
          <li>Credentials are encrypted using your operating system's secure storage</li>
          <li>Windows: DPAPI (Data Protection API)</li>
          <li>macOS: Keychain</li>
          <li>Linux: libsecret/keyring</li>
          <li>Credentials are never stored in plain text</li>
        </ul>
      </div>
    </div>
  );
}
