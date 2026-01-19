import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../services/api';

export interface BackendErrorState {
  hasError: boolean;
  message: string;
  code: string;
  technicalDetails?: string;
  action?: string;
}

const POLL_INTERVAL_MS = 5000; // Check every 5 seconds when in error state
const HEALTH_CHECK_TIMEOUT = 3000; // 3 second timeout for health checks

/**
 * Hook for managing backend connection error state.
 *
 * Provides:
 * - Persistent error state that survives toast dismissals
 * - Automatic polling to detect when backend comes back online
 * - Clear error information for display
 */
export function useBackendError() {
  const [errorState, setErrorState] = useState<BackendErrorState>({
    hasError: false,
    message: '',
    code: '',
  });
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Check backend health by calling the /health endpoint.
   */
  const checkBackendHealth = useCallback(async (): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);

      const response = await api.get('/health', {
        signal: controller.signal,
        timeout: HEALTH_CHECK_TIMEOUT,
      });

      clearTimeout(timeoutId);

      // Backend is healthy if we get a successful response
      return response.status === 200;
    } catch {
      // Backend is not available
      return false;
    }
  }, []);

  /**
   * Set error state (called by error handler when backend errors occur).
   */
  const setError = useCallback(
    (error: { message: string; code: string; technicalDetails?: string; action?: string }) => {
      setErrorState({
        hasError: true,
        message: error.message,
        code: error.code,
        technicalDetails: error.technicalDetails,
        action: error.action,
      });
    },
    []
  );

  /**
   * Clear error state (called when backend is confirmed healthy).
   */
  const clearError = useCallback(() => {
    setErrorState({
      hasError: false,
      message: '',
      code: '',
    });
  }, []);

  /**
   * Start polling backend health when in error state.
   */
  useEffect(() => {
    if (errorState.hasError) {
      // Start polling to check if backend recovers
      pollingIntervalRef.current = setInterval(async () => {
        const isHealthy = await checkBackendHealth();
        if (isHealthy) {
          clearError();
          // Clear the interval - polling will stop automatically
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      }, POLL_INTERVAL_MS);
    } else {
      // Stop polling when error is cleared
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [errorState.hasError, checkBackendHealth, clearError]);

  return {
    errorState,
    setError,
    clearError,
    checkBackendHealth,
  };
}
