/**
 * Test setup file for Vitest.
 *
 * This file runs before all tests and configures:
 * - Testing Library DOM matchers (toBeInTheDocument, etc.)
 * - Common mocks for browser APIs (localStorage, console)
 * - Global test utilities
 */

import '@testing-library/jest-dom';
import { vi, beforeEach, afterEach } from 'vitest';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock console methods to reduce noise in test output
// Override in individual tests if you need to verify console calls
const originalError = console.error;
const originalWarn = console.warn;

beforeEach(() => {
  // Reset localStorage before each test
  localStorageMock.clear();

  // Suppress console.error and console.warn by default
  // Tests can override this if they need to verify console output
  console.error = vi.fn();
  console.warn = vi.fn();
});

afterEach(() => {
  // Restore original console methods after each test
  console.error = originalError;
  console.warn = originalWarn;

  // Clean up any timers
  vi.clearAllTimers();
});

// Mock window.location.reload
Object.defineProperty(window, 'location', {
  value: {
    ...window.location,
    reload: vi.fn(),
  },
  writable: true,
});

// Mock navigator.clipboard
// Use configurable: true to allow userEvent to override if needed
interface MockedClipboard extends Clipboard {
  __mocked?: boolean;
}
if (!navigator.clipboard || !(navigator.clipboard as MockedClipboard).__mocked) {
  Object.defineProperty(navigator, 'clipboard', {
    value: {
      writeText: vi.fn().mockResolvedValue(undefined),
      readText: vi.fn().mockResolvedValue(''),
      __mocked: true,
    },
    writable: true,
    configurable: true,
  });
}
