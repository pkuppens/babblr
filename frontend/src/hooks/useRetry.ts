import { useState, useCallback, useRef } from 'react';

interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
}

type HttpErrorLike = {
  response?: {
    status?: number;
  };
};

function isHttpErrorLike(error: unknown): error is HttpErrorLike {
  return typeof error === 'object' && error !== null && 'response' in error;
}

function toError(error: unknown): Error {
  if (error instanceof Error) return error;
  return new Error(typeof error === 'string' ? error : 'Unknown error');
}

export const useRetry = <Args extends unknown[], Result>(
  operation: (...args: Args) => Promise<Result>,
  options: RetryOptions = {}
) => {
  const { maxRetries = 3, initialDelay = 1000, maxDelay = 10000 } = options;

  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const cancelRef = useRef(false);

  const execute = useCallback(
    async (...args: Args): Promise<Result> => {
      setError(null);
      cancelRef.current = false;
      let currentDelay = initialDelay;

      for (let i = 0; i <= maxRetries; i++) {
        try {
          if (cancelRef.current) break;

          setIsRetrying(i > 0);
          setRetryCount(i);

          const result = await operation(...args);
          setIsRetrying(false);
          return result;
        } catch (err: unknown) {
          setError(toError(err));

          if (i === maxRetries || !shouldRetry(err) || cancelRef.current) {
            setIsRetrying(false);
            throw err;
          }

          // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, currentDelay));
          currentDelay = Math.min(currentDelay * 2, maxDelay);
        }
      }
    },
    [operation, maxRetries, initialDelay, maxDelay]
  );

  const cancel = useCallback(() => {
    cancelRef.current = true;
    setIsRetrying(false);
  }, []);

  return { execute, isRetrying, retryCount, error, cancel };
};

function shouldRetry(error: unknown): boolean {
  // Retry on network errors or specific status codes (429, 503, 504)
  if (!isHttpErrorLike(error) || !error.response) return true;
  const status = error.response.status;
  return [429, 503, 504].includes(status);
}
