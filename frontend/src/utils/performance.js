/**
 * Returns a debounced version of the function.
 * @param {Function} func - function to debounce
 * @param {number} wait - milliseconds to wait
 * @returns {Function}
 */
export function debounce(func, wait) {
  let timeoutId;
  return function debounced(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), wait);
  };
}

/**
 * Memoizes a function with a single argument.
 * @param {Function} fn
 * @returns {Function}
 */
export function memoize(fn) {
  const cache = new Map();
  return function memoized(arg) {
    if (cache.has(arg)) return cache.get(arg);
    const result = fn(arg);
    cache.set(arg, result);
    return result;
  };
}
