import toast from 'react-hot-toast';
import { AxiosError } from 'axios';

export interface BabblrErrorResponse {
  // FastAPI error envelope: { detail: ... }
  detail?: unknown;
  // Old backend error format (structured object)
  error?: {
    code: string;
    message: string;
    details?: string;
    retry?: boolean;
    action?: string;
  };
  // New backend error format (simple fields)
  message?: string;
  technical_details?: string;
  fix?: string;
  // Some endpoints include a simple string error in detail
  // e.g. { detail: "Transcription failed: ..." }
}

export interface ErrorDetails {
  message: string;
  code: string;
  retry: boolean;
  action?: string;
  technical_details?: string;
  status?: number;
}

type RecordLike = Record<string, unknown>;

// Global callback for setting persistent backend error state
let persistentErrorSetter:
  | ((error: { message: string; code: string; technicalDetails?: string; action?: string }) => void)
  | null = null;

/**
 * Register a callback to set persistent backend error state.
 * This allows the error handler to update persistent error indicators.
 */
export function registerPersistentErrorSetter(
  setter: (error: {
    message: string;
    code: string;
    technicalDetails?: string;
    action?: string;
  }) => void
) {
  persistentErrorSetter = setter;
}

/**
 * Unregister the persistent error setter (for cleanup).
 */
export function unregisterPersistentErrorSetter() {
  persistentErrorSetter = null;
}

function isRecordLike(value: unknown): value is RecordLike {
  return typeof value === 'object' && value !== null;
}

/**
 * Determine if an error should trigger persistent error state.
 * Only backend connection/availability errors should be persistent.
 */
function shouldPersistError(code: string, status?: number): boolean {
  return (
    code === 'BACKEND_NOT_RUNNING' ||
    code === 'NETWORK_ERROR' ||
    code === 'DATABASE_ERROR' ||
    (status === 503 && code === 'SERVICE_UNAVAILABLE')
  );
}

export const handleError = (error: unknown): ErrorDetails => {
  // Log full error details to console for developers
  console.group('🔴 Error Details');
  console.error('Full error object:', error);

  let message = 'An unexpected error occurred. Please try again.';
  let code = 'UNKNOWN_ERROR';
  let retry = false;
  let action: string | undefined;
  // Keep technical details for debugging, but avoid showing stack traces to end users.
  let technical_details: string | undefined;
  let status: number | undefined;

  if (error instanceof Error) {
    message = error.message;
  }

  // Handle Axios errors
  if (isAxiosError(error)) {
    status = error.response?.status;
    const data = error.response?.data as unknown;

    console.log('HTTP Status:', status);
    console.log('Response data:', data);

    const unwrapFastApiDetail = (payload: unknown): unknown => {
      if (isRecordLike(payload) && 'detail' in payload) {
        return (payload as BabblrErrorResponse).detail;
      }
      return payload;
    };

    const parseStructuredError = (payload: unknown) => {
      if (!payload) return;

      // String detail: "Transcription failed: ..."
      if (typeof payload === 'string') {
        technical_details = payload;
        return;
      }

      if (!isRecordLike(payload)) return;

      // New format: { message, technical_details, fix, error? }
      if ('message' in payload && typeof payload.message === 'string') {
        message = payload.message || message;
        if (typeof payload.technical_details === 'string') {
          technical_details = payload.technical_details;
        }
        if (typeof payload.fix === 'string') {
          action = payload.fix;
        }
        if (typeof payload.error === 'string') {
          code = String(payload.error).toUpperCase();
        }
        return;
      }

      // Old format: { error: { code, message, details, retry, action } }
      if ('error' in payload && isRecordLike(payload.error)) {
        const err = payload.error as RecordLike;
        if (typeof err.message === 'string') {
          message = err.message || message;
        }
        if (typeof err.code === 'string') {
          code = err.code;
        }
        retry = Boolean(err.retry);
        if (typeof err.action === 'string') {
          action = err.action;
        }
        if (typeof err.details === 'string') {
          technical_details = err.details;
        }
      }
    };

    // FastAPI wraps HTTPException(detail=...) as { detail: ... }
    const unwrapped = unwrapFastApiDetail(data);
    parseStructuredError(unwrapped);

    // Improve message based on known failure modes if backend didn't provide a good one.
    if (!error.response) {
      // Check if it's a connection error (backend not running)
      if (error.code === 'ECONNREFUSED' || error.message?.includes('ECONNREFUSED')) {
        message = 'Cannot connect to backend server. The backend may not be running.';
        code = 'BACKEND_NOT_RUNNING';
        retry = true;
        action =
          'Please start the backend server:\n' +
          '1. Open a terminal in the backend directory\n' +
          '2. Run: ./run-backend.sh (or run-backend.bat on Windows)\n' +
          '3. Wait for "Application startup complete" message';
        technical_details = 'Connection refused - backend server is not running or not accessible';
      } else {
        message = 'Network error. Cannot reach the server.';
        code = 'NETWORK_ERROR';
        retry = true;
        technical_details = technical_details ?? 'Server might be down or network connection lost';
      }
    }

    // Override with specific error messages based on status
    if (error.code === 'ECONNABORTED') {
      message = 'Request timed out. Please try again.';
      code = 'TIMEOUT';
      retry = true;
    } else if (status === 401) {
      code = 'AUTHENTICATION_ERROR';
      retry = false;
      // This app doesn't have end-user login; 401 usually means a backend upstream key issue.
      message =
        message === error.message
          ? 'The AI service is not configured on the server (missing/invalid API key).'
          : message;
      action =
        action ??
        "If you run the backend locally: set a valid ANTHROPIC_API_KEY or switch LLM_PROVIDER to 'ollama' or 'mock' in backend/.env.";
    } else if (status === 503) {
      code = 'SERVICE_UNAVAILABLE';
      retry = true;
      message =
        message === error.message
          ? 'A required service is temporarily unavailable. Please try again.'
          : message;
    } else if (status === 500) {
      // Common local setup issue: FFmpeg missing for Whisper audio decoding.
      if (
        typeof technical_details === 'string' &&
        (technical_details.toLowerCase().includes('ffmpeg') ||
          technical_details.toLowerCase().includes('ffprobe') ||
          technical_details.toLowerCase().includes('filenotfounderror') ||
          technical_details.toLowerCase().includes('winerror 2'))
      ) {
        code = 'STT_FFMPEG_MISSING';
        message = 'Speech transcription needs FFmpeg installed on this machine.';
        action =
          action ??
          "Install FFmpeg and ensure 'ffmpeg' and 'ffprobe' are available in PATH, then restart the backend.";
      }
      // Database initialization errors
      else if (
        typeof technical_details === 'string' &&
        (technical_details.toLowerCase().includes('database') ||
          technical_details.toLowerCase().includes('migration') ||
          technical_details.toLowerCase().includes('schema') ||
          technical_details.toLowerCase().includes('column') ||
          technical_details.toLowerCase().includes('table'))
      ) {
        code = 'DATABASE_ERROR';
        message =
          message === error.message
            ? 'Database initialization failed. The backend cannot start.'
            : message;
        action =
          action ??
          'This usually means:\n' +
            '1. Database file is corrupted or locked\n' +
            '2. Missing database migrations\n' +
            '3. Permission issues with the database file\n\n' +
            'Try: Delete the database file and restart the backend (it will be recreated automatically)';
      }
    }
  }

  console.log('Processed error:', { message, code, technical_details, status });
  console.groupEnd();

  // Create a detailed error message with technical details expandable
  const toastMessageParts: string[] = [message];
  if (action) toastMessageParts.push(`\nFix: ${action}`);
  if (technical_details) {
    toastMessageParts.push(
      `\n\n💡 Technical: ${technical_details.substring(0, 120)}${technical_details.length > 120 ? '...' : ''}`
    );
  }
  const toastMessage = toastMessageParts.join('');

  // Display toast with error
  toast.error(toastMessage, {
    duration: status === 401 ? 10000 : 5000, // Show auth errors longer
    id: code, // Prevent duplicate toasts
    style: {
      maxWidth: '600px',
    },
  });

  // Set persistent error state for backend connection issues
  if (persistentErrorSetter && shouldPersistError(code, status)) {
    persistentErrorSetter({
      message,
      code,
      technicalDetails: technical_details,
      action,
    });
  }

  return { message, code, retry, action, technical_details, status };
};

function isAxiosError(error: unknown): error is AxiosError {
  if (!isRecordLike(error)) return false;
  if (!('isAxiosError' in error)) return false;
  return (error as { isAxiosError?: boolean }).isAxiosError === true;
}
