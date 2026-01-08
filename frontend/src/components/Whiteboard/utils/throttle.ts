/**
 * Throttle utility for limiting function execution frequency
 */

export interface ThrottleOptions {
  leading?: boolean;
  trailing?: boolean;
}

/**
 * Throttles a function to execute at most once per specified interval.
 * 
 * @param func - Function to throttle
 * @param wait - Time in milliseconds to wait between executions
 * @param options - Throttle options
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  options: ThrottleOptions = {}
): (...args: Parameters<T>) => void {
  const { leading = true, trailing = true } = options;
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let previous = 0;
  let lastArgs: Parameters<T> | null = null;

  const throttled = (...args: Parameters<T>) => {
    const now = Date.now();
    const remaining = wait - (now - previous);

    lastArgs = args;

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      func(...args);
      lastArgs = null;
    } else if (!timeout && trailing) {
      timeout = setTimeout(() => {
        previous = leading ? Date.now() : 0;
        timeout = null;
        if (lastArgs) {
          func(...lastArgs);
          lastArgs = null;
        }
      }, remaining);
    }
  };

  throttled.cancel = () => {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
    previous = 0;
    lastArgs = null;
  };

  return throttled;
}

/**
 * Creates a throttled version of a function that batches arguments.
 * Useful for collecting multiple events and sending them together.
 * 
 * @param func - Function to batch throttle
 * @param wait - Time in milliseconds to wait between batches
 * @returns Batched throttled function
 */
export function batchThrottle<T>(
  func: (args: T[]) => void,
  wait: number
): (arg: T) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let batch: T[] = [];

  const throttled = (arg: T) => {
    batch.push(arg);

    if (!timeout) {
      timeout = setTimeout(() => {
        if (batch.length > 0) {
          func([...batch]);
          batch = [];
        }
        timeout = null;
      }, wait);
    }
  };

  throttled.flush = () => {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
    if (batch.length > 0) {
      func([...batch]);
      batch = [];
    }
  };

  throttled.cancel = () => {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
    batch = [];
  };

  return throttled;
}
