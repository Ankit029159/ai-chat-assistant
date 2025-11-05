/**
 * Formats ISO timestamp string to readable local time string.
 * @param {string} isoString - ISO timestamp
 * @returns {string} formatted time string
 */
export function formatTimestamp(isoString) {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    if (isNaN(date)) return '';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

/**
 * Sanitizes text input by trimming and removing dangerous characters.
 * @param {string} text
 * @returns {string}
 */
export function sanitizeText(text) {
  if (typeof text !== 'string') return '';
  return text.trim();
}

/**
 * Generates a unique ID string.
 * @returns {string}
 */
export function generateUniqueId() {
  return `id_${Math.random().toString(36).substr(2, 9)}_${Date.now()}`;
}
