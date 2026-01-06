import toast from "react-hot-toast";
import { AxiosError } from "axios";

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

export const handleError = (error: unknown): ErrorDetails => {
  // Log full error details to console for developers
  console.group("🔴 Error Details");
  console.error("Full error object:", error);

  let message = "An unexpected error occurred. Please try again.";
  let code = "UNKNOWN_ERROR";
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

    console.log("HTTP Status:", status);
    console.log("Response data:", data);

    const unwrapFastApiDetail = (payload: unknown): unknown => {
      if (payload && typeof payload === "object" && "detail" in payload) {
        return (payload as BabblrErrorResponse).detail;
      }
      return payload;
    };

    const parseStructuredError = (payload: unknown) => {
      if (!payload) return;

      // String detail: "Transcription failed: ..."
      if (typeof payload === "string") {
        technical_details = payload;
        return;
      }

      if (typeof payload !== "object") return;

      // New format: { message, technical_details, fix, error? }
      if ("message" in payload && typeof (payload as any).message === "string") {
        message = (payload as any).message || message;
        if (typeof (payload as any).technical_details === "string") {
          technical_details = (payload as any).technical_details;
        }
        if (typeof (payload as any).fix === "string") {
          action = (payload as any).fix;
        }
        if (typeof (payload as any).error === "string") {
          code = String((payload as any).error).toUpperCase();
        }
        return;
      }

      // Old format: { error: { code, message, details, retry, action } }
      if (
        "error" in payload &&
        typeof (payload as any).error === "object" &&
        (payload as any).error !== null &&
        typeof (payload as any).error.message === "string"
      ) {
        const err = (payload as any).error;
        message = err.message || message;
        code = typeof err.code === "string" ? err.code : code;
        retry = Boolean(err.retry);
        action = typeof err.action === "string" ? err.action : action;
        technical_details = typeof err.details === "string" ? err.details : technical_details;
      }
    };

    // FastAPI wraps HTTPException(detail=...) as { detail: ... }
    const unwrapped = unwrapFastApiDetail(data);
    parseStructuredError(unwrapped);

    // Improve message based on known failure modes if backend didn't provide a good one.
    if (!error.response) {
      message = "Network error. Cannot reach the server.";
      code = "NETWORK_ERROR";
      retry = true;
      technical_details = technical_details ?? "Server might be down or network connection lost";
    }

    // Override with specific error messages based on status
    if (error.code === "ECONNABORTED") {
      message = "Request timed out. Please try again.";
      code = "TIMEOUT";
      retry = true;
    } else if (status === 401) {
      code = "AUTHENTICATION_ERROR";
      retry = false;
      // This app doesn't have end-user login; 401 usually means a backend upstream key issue.
      message =
        message === error.message
          ? "The AI service is not configured on the server (missing/invalid API key)."
          : message;
      action =
        action ??
        "If you run the backend locally: set a valid ANTHROPIC_API_KEY or switch LLM_PROVIDER to 'ollama' or 'mock' in backend/.env.";
    } else if (status === 503) {
      code = "SERVICE_UNAVAILABLE";
      retry = true;
      message =
        message === error.message ? "A required service is temporarily unavailable. Please try again." : message;
    } else if (status === 500) {
      // Common local setup issue: FFmpeg missing for Whisper audio decoding.
      if (
        typeof technical_details === "string" &&
        (technical_details.toLowerCase().includes("ffmpeg") ||
          technical_details.toLowerCase().includes("ffprobe") ||
          technical_details.toLowerCase().includes("filenotfounderror") ||
          technical_details.toLowerCase().includes("winerror 2"))
      ) {
        code = "STT_FFMPEG_MISSING";
        message = "Speech transcription needs FFmpeg installed on this machine.";
        action =
          action ??
          "Install FFmpeg and ensure 'ffmpeg' and 'ffprobe' are available in PATH, then restart the backend.";
      }
    }
  }

  console.log("Processed error:", { message, code, technical_details, status });
  console.groupEnd();

  // Create a detailed error message with technical details expandable
  const toastMessageParts: string[] = [message];
  if (action) toastMessageParts.push(`\nFix: ${action}`);
  if (technical_details) {
    toastMessageParts.push(
      `\n\n💡 Technical: ${technical_details.substring(0, 120)}${technical_details.length > 120 ? "..." : ""}`
    );
  }
  const toastMessage = toastMessageParts.join("");

  // Display toast with error
  toast.error(toastMessage, {
    duration: status === 401 ? 10000 : 5000, // Show auth errors longer
    id: code, // Prevent duplicate toasts
    style: {
      maxWidth: '600px',
    },
  });

  return { message, code, retry, action, technical_details, status };
};

function isAxiosError(error: any): error is AxiosError {
  return error.isAxiosError === true;
}
