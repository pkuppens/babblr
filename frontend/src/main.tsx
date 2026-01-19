import React from 'react';
import ReactDOM from 'react-dom/client';
import { Toaster } from 'react-hot-toast';
import App from './App.tsx';
import ErrorBoundary from './components/ErrorBoundary';
import { BackendErrorProvider } from './contexts/BackendErrorContext';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BackendErrorProvider>
        <Toaster position="top-right" />
        <App />
      </BackendErrorProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
