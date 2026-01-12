/**
 * Verification test to confirm the testing infrastructure is working.
 *
 * This test follows BDD (Behavior-Driven Development) naming conventions:
 * - Test descriptions use "should" or "when...should" format
 * - Tests are organized by feature/component
 * - Each test describes expected behavior clearly
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from '../components/ErrorBoundary';

describe('Testing Infrastructure Setup', () => {
  describe('when the test environment is configured', () => {
    it('should have vitest globals available', () => {
      expect(describe).toBeDefined();
      expect(it).toBeDefined();
      expect(expect).toBeDefined();
    });

    it('should have React Testing Library available', () => {
      expect(render).toBeDefined();
      expect(screen).toBeDefined();
    });

    it('should have jest-dom matchers available', () => {
      const element = document.createElement('div');
      element.textContent = 'Test';
      document.body.appendChild(element);

      expect(element).toBeInTheDocument();

      document.body.removeChild(element);
    });
  });

  describe('when localStorage is used', () => {
    beforeEach(() => {
      localStorage.clear();
    });

    it('should store and retrieve values', () => {
      localStorage.setItem('test-key', 'test-value');
      expect(localStorage.getItem('test-key')).toBe('test-value');
    });

    it('should clear all values when cleared', () => {
      localStorage.setItem('key1', 'value1');
      localStorage.setItem('key2', 'value2');
      localStorage.clear();
      expect(localStorage.getItem('key1')).toBeNull();
      expect(localStorage.getItem('key2')).toBeNull();
    });
  });

  describe('when rendering a React component', () => {
    it('should render ErrorBoundary without errors', () => {
      const { container } = render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );

      expect(container).toBeInTheDocument();
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });
  });
});
