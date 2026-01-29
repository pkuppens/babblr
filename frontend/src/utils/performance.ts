/**
 * Performance monitoring utilities for debugging bottlenecks.
 *
 * Compatible with Chrome DevTools Performance tab and Console API.
 * Use Chrome DevTools -> Performance to record and analyze timing data.
 */

const PERF_ENABLED = import.meta.env.DEV || localStorage.getItem('babblr_perf_debug') === 'true';

export class PerformanceMonitor {
  /**
   * Start a performance measurement.
   * Creates a performance mark that appears in Chrome DevTools Performance tab.
   *
   * @param name - Unique identifier for this measurement
   */
  static start(name: string): void {
    if (!PERF_ENABLED) return;

    const markName = `${name}:start`;
    performance.mark(markName);
    console.time(`[PERF] ${name}`);
    console.debug(`[PERF] ${name} - START`);
  }

  /**
   * End a performance measurement and log the result.
   *
   * @param name - Must match the name used in start()
   */
  static end(name: string): number | undefined {
    if (!PERF_ENABLED) return undefined;

    const startMarkName = `${name}:start`;
    const endMarkName = `${name}:end`;
    const measureName = name;

    try {
      performance.mark(endMarkName);
      performance.measure(measureName, startMarkName, endMarkName);

      const measure = performance.getEntriesByName(measureName)[0];
      const durationMs = measure.duration;

      console.timeEnd(`[PERF] ${name}`);
      console.debug(`[PERF] ${name} - DONE in ${durationMs.toFixed(2)}ms`);

      // Clean up marks and measures to avoid memory buildup
      performance.clearMarks(startMarkName);
      performance.clearMarks(endMarkName);
      performance.clearMeasures(measureName);

      return durationMs;
    } catch (error) {
      console.warn(`[PERF] Failed to measure ${name}:`, error);
      console.timeEnd(`[PERF] ${name}`);
      return undefined;
    }
  }

  /**
   * Measure an async function execution time.
   *
   * @param name - Unique identifier for this measurement
   * @param fn - Async function to measure
   * @returns Promise resolving to the function's result
   */
  static async measure<T>(name: string, fn: () => Promise<T>): Promise<T> {
    PerformanceMonitor.start(name);
    try {
      return await fn();
    } finally {
      PerformanceMonitor.end(name);
    }
  }

  /**
   * Log a performance event with timestamp.
   * Useful for tracking user interactions and state changes.
   *
   * @param event - Event name
   * @param data - Optional event data
   */
  static logEvent(event: string, data?: any): void {
    if (!PERF_ENABLED) return;

    const timestamp = performance.now().toFixed(2);
    console.debug(`[PERF] EVENT @${timestamp}ms - ${event}`, data || '');
  }

  /**
   * Get all performance measures recorded so far.
   * Useful for debugging and analysis.
   *
   * @returns Array of performance entries
   */
  static getMeasures(): PerformanceEntry[] {
    return performance.getEntriesByType('measure');
  }

  /**
   * Clear all performance data.
   * Call this when starting a new profiling session.
   */
  static clear(): void {
    performance.clearMarks();
    performance.clearMeasures();
    console.debug('[PERF] Cleared all performance data');
  }

  /**
   * Enable performance debugging at runtime.
   * Persists across page reloads.
   */
  static enable(): void {
    localStorage.setItem('babblr_perf_debug', 'true');
    console.log('[PERF] Performance debugging enabled. Reload page to activate.');
  }

  /**
   * Disable performance debugging.
   */
  static disable(): void {
    localStorage.removeItem('babblr_perf_debug');
    console.log('[PERF] Performance debugging disabled. Reload page to deactivate.');
  }
}

/**
 * Decorator for measuring React component method timing.
 * Note: Only works with class components, not hooks.
 */
export function measureMethod(target: any, propertyName: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = async function (...args: any[]) {
    const name = `${target.constructor.name}.${propertyName}`;
    return await PerformanceMonitor.measure(name, () => originalMethod.apply(this, args));
  };

  return descriptor;
}

// Expose to window for Chrome DevTools Console access
if (typeof window !== 'undefined') {
  (window as any).BabblrPerf = PerformanceMonitor;
}

export default PerformanceMonitor;
