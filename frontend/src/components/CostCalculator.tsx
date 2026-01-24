/**
 * Cost Calculator Component
 *
 * Shows estimated API costs for conversations based on selected provider and model.
 * Helps users understand the cost implications of using different LLM providers.
 */

import { useState } from 'react';
import { Calculator, Info } from 'lucide-react';

type Provider = 'anthropic' | 'google' | 'openai' | 'ollama';

interface ProviderPricing {
  name: string;
  models: {
    [key: string]: {
      name: string;
      inputCost: number; // Cost per 1M tokens
      outputCost: number; // Cost per 1M tokens
      recommended?: boolean;
    };
  };
}

// Pricing data (as of January 2026)
const PRICING: Record<Provider, ProviderPricing> = {
  anthropic: {
    name: 'Anthropic Claude',
    models: {
      'claude-haiku-4.5': {
        name: 'Claude Haiku 4.5',
        inputCost: 1.0,
        outputCost: 5.0,
      },
      'claude-sonnet-4.5': {
        name: 'Claude Sonnet 4.5',
        inputCost: 3.0,
        outputCost: 15.0,
        recommended: true,
      },
      'claude-opus-4.5': {
        name: 'Claude Opus 4.5',
        inputCost: 5.0,
        outputCost: 25.0,
      },
    },
  },
  google: {
    name: 'Google Gemini',
    models: {
      'gemini-2.0-flash': {
        name: 'Gemini 2.0 Flash',
        inputCost: 0.0,
        outputCost: 0.0, // Free tier available
        recommended: true,
      },
      'gemini-1.5-flash': {
        name: 'Gemini 1.5 Flash',
        inputCost: 0.075,
        outputCost: 0.3,
      },
      'gemini-1.5-pro': {
        name: 'Gemini 1.5 Pro',
        inputCost: 1.25,
        outputCost: 5.0,
      },
    },
  },
  openai: {
    name: 'OpenAI',
    models: {
      'gpt-4o-mini': {
        name: 'GPT-4o Mini',
        inputCost: 0.15,
        outputCost: 0.6,
        recommended: true,
      },
      'gpt-4o': {
        name: 'GPT-4o',
        inputCost: 5.0,
        outputCost: 15.0,
      },
      'o1': {
        name: 'O1',
        inputCost: 15.0,
        outputCost: 60.0,
      },
    },
  },
  ollama: {
    name: 'Ollama (Local)',
    models: {
      local: {
        name: 'Any Model (Local)',
        inputCost: 0,
        outputCost: 0,
      },
    },
  },
};

// Estimated tokens for a typical conversation turn
const TYPICAL_CONVERSATION = {
  userMessageTokens: 50, // User's message
  systemPromptTokens: 200, // System prompt + context
  responseTokens: 150, // AI's response
};

export default function CostCalculator() {
  const [selectedProvider, setSelectedProvider] = useState<Provider>('anthropic');
  const [selectedModel, setSelectedModel] = useState<string>('claude-sonnet-4.5');
  const [conversationsPerMonth, setConversationsPerMonth] = useState(100);
  const [turnsPerConversation, setTurnsPerConversation] = useState(10);

  const providerData = PRICING[selectedProvider];
  const modelData = providerData?.models[selectedModel];

  // Calculate costs
  const totalTurns = conversationsPerMonth * turnsPerConversation;
  const inputTokens =
    totalTurns * (TYPICAL_CONVERSATION.userMessageTokens + TYPICAL_CONVERSATION.systemPromptTokens);
  const outputTokens = totalTurns * TYPICAL_CONVERSATION.responseTokens;

  const inputCostPerMillion = modelData?.inputCost || 0;
  const outputCostPerMillion = modelData?.outputCost || 0;

  const totalInputCost = (inputTokens / 1_000_000) * inputCostPerMillion;
  const totalOutputCost = (outputTokens / 1_000_000) * outputCostPerMillion;
  const totalCost = totalInputCost + totalOutputCost;

  // Update selected model when provider changes
  const handleProviderChange = (provider: Provider) => {
    setSelectedProvider(provider);
    const firstModel = Object.keys(PRICING[provider].models)[0];
    setSelectedModel(firstModel);
  };

  return (
    <div className="cost-calculator">
      <div className="cost-calculator-header">
        <Calculator size={20} />
        <h3>Cost Calculator</h3>
      </div>
      <p className="cost-calculator-description">
        Estimate monthly API costs based on your usage patterns. Actual costs may vary.
      </p>

      <div className="cost-calculator-inputs">
        {/* Provider Selection */}
        <div className="cost-input-group">
          <label htmlFor="cost-provider">Provider</label>
          <select
            id="cost-provider"
            value={selectedProvider}
            onChange={e => handleProviderChange(e.target.value as Provider)}
            className="cost-select"
          >
            {Object.entries(PRICING).map(([key, data]) => (
              <option key={key} value={key}>
                {data.name}
              </option>
            ))}
          </select>
        </div>

        {/* Model Selection */}
        <div className="cost-input-group">
          <label htmlFor="cost-model">Model</label>
          <select
            id="cost-model"
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="cost-select"
          >
            {Object.entries(providerData.models).map(([key, model]) => (
              <option key={key} value={key}>
                {model.name} {model.recommended && '⭐'}
              </option>
            ))}
          </select>
        </div>

        {/* Usage Inputs */}
        <div className="cost-input-group">
          <label htmlFor="cost-conversations">Conversations per month</label>
          <input
            id="cost-conversations"
            type="number"
            value={conversationsPerMonth}
            onChange={e => setConversationsPerMonth(Number(e.target.value))}
            min="1"
            max="10000"
            className="cost-input"
          />
        </div>

        <div className="cost-input-group">
          <label htmlFor="cost-turns">Turns per conversation</label>
          <input
            id="cost-turns"
            type="number"
            value={turnsPerConversation}
            onChange={e => setTurnsPerConversation(Number(e.target.value))}
            min="1"
            max="100"
            className="cost-input"
          />
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="cost-breakdown">
        <h4>Estimated Monthly Cost</h4>

        <div className="cost-breakdown-row">
          <span>Total turns:</span>
          <span className="cost-value">{totalTurns.toLocaleString()}</span>
        </div>

        <div className="cost-breakdown-row">
          <span>Input tokens:</span>
          <span className="cost-value">{inputTokens.toLocaleString()}</span>
        </div>

        <div className="cost-breakdown-row">
          <span>Output tokens:</span>
          <span className="cost-value">{outputTokens.toLocaleString()}</span>
        </div>

        <div className="cost-breakdown-divider" />

        <div className="cost-breakdown-row">
          <span>Input cost:</span>
          <span className="cost-value">${totalInputCost.toFixed(4)}</span>
        </div>

        <div className="cost-breakdown-row">
          <span>Output cost:</span>
          <span className="cost-value">${totalOutputCost.toFixed(4)}</span>
        </div>

        <div className="cost-breakdown-divider" />

        <div className="cost-breakdown-row cost-total">
          <span>Total:</span>
          <span className="cost-value-total">
            ${totalCost.toFixed(2)}
            {selectedProvider === 'ollama' && ' (FREE)'}
          </span>
        </div>
      </div>

      {/* Free Tier Info */}
      {selectedProvider === 'google' && selectedModel === 'gemini-2.0-flash' && (
        <div className="cost-info-box">
          <Info size={16} />
          <div>
            <strong>Free Tier Available</strong>
            <p>Gemini 2.0 Flash has generous free tier limits for developers.</p>
          </div>
        </div>
      )}

      {selectedProvider === 'ollama' && (
        <div className="cost-info-box">
          <Info size={16} />
          <div>
            <strong>Completely Free</strong>
            <p>
              Ollama runs models locally on your computer. No API costs, no usage limits, complete
              privacy.
            </p>
          </div>
        </div>
      )}

      {/* Pricing Info */}
      <div className="cost-pricing-details">
        <h4>Pricing Details</h4>
        <div className="cost-pricing-row">
          <span>Input:</span>
          <span>${inputCostPerMillion.toFixed(2)} per 1M tokens</span>
        </div>
        <div className="cost-pricing-row">
          <span>Output:</span>
          <span>${outputCostPerMillion.toFixed(2)} per 1M tokens</span>
        </div>
      </div>

      <p className="cost-disclaimer">
        <strong>Note:</strong> These are estimates based on typical conversation patterns. Actual
        costs may vary based on message length, context window usage, and provider pricing changes.
        Always check provider documentation for current pricing.
      </p>
    </div>
  );
}
