import toast from "react-hot-toast";
import { AxiosError } from "axios";

export interface BabblrErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    retry?: boolean;
    action?: string;
  };
}

export const handleError = (error: unknown) => {
  console.error("Error encountered:", error);

  let message = "An unexpected error occurred. Please try again.";
  let code = "UNKNOWN_ERROR";
  let retry = false;
  let action: string | undefined;

  if (error instanceof Error) {
    message = error.message;
  }

  // Handle Axios errors
  if (isAxiosError(error)) {
    const data = error.response?.data as BabblrErrorResponse;

    if (data?.error) {
      message = data.error.message;
      code = data.error.code;
      retry = data.error.retry || false;
      action = data.error.action;
    } else if (error.code === "ECONNABORTED") {
      message = "The request timed out. Please check your connection.";
      code = "TIMEOUT";
      retry = true;
    } else if (!error.response) {
      message = "Network error. Please check your internet connection.";
      code = "NETWORK_ERROR";
      retry = true;
    }
  }

  // Display toast
  toast.error(message, {
    duration: 5000,
    id: code, // Prevent duplicate toasts for same error type
  });

  return { message, code, retry, action };
};

function isAxiosError(error: any): error is AxiosError {
  return error.isAxiosError === true;
}
