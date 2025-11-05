const BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Posts message payload to backend /chat endpoint.
 * Implements retry with exponential backoff for transient errors.
 * @param {Object} payload - message payload { message: string, attachments: [], conversationHistory: [] }
 * @returns {Promise<Object>} JSON response with bot reply and optional attachments
 */
export async function sendMessage(payload) {
  const maxRetries = 3;
  let attempt = 0;
  let lastError = null;

  while (attempt <= maxRetries) {
    try {
      const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error;
      attempt += 1;
      if (attempt > maxRetries) break;
      const backoff = 2 ** attempt * 500;
      await delay(backoff);
    }
  }

  throw lastError;
}

/**
 * Uploads files to backend /upload endpoint.
 * @param {File[]} files - Array of files to upload
 * @returns {Promise<Object[]>} Array of uploaded file info
 */
export async function uploadAttachments(files) {
  if (!files || files.length === 0) return [];

  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));

  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload error: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  return data; // should return array of uploaded files info
}
