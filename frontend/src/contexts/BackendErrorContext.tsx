import React, { createContext, useContext, ReactNode } from 'react';
import { useBackendError, type BackendErrorState } from '../hooks/useBackendError';

interface BackendErrorContextType {
  errorState: BackendErrorState;
  setError: (error: {
    message: string;
    code: string;
    technicalDetails?: string;
    action?: string;
  }) => void;
  clearError: () => void;
  checkBackendHealth: () => Promise<boolean>;
}

const BackendErrorContext = createContext<BackendErrorContextType | undefined>(undefined);

export function BackendErrorProvider({ children }: { children: ReactNode }) {
  const backendError = useBackendError();

  return (
    <BackendErrorContext.Provider value={backendError}>{children}</BackendErrorContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useBackendErrorContext() {
  const context = useContext(BackendErrorContext);
  if (context === undefined) {
    throw new Error('useBackendErrorContext must be used within a BackendErrorProvider');
  }
  return context;
}
