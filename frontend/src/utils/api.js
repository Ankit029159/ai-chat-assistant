const BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Posts message payload to backend /chat endpoint.
 * Implements retry with exponential backoff for transient errors.
 * Returns medical response with disclaimer and sources.
 * @param {Object} payload - message payload { message: string }
 * @returns {Promise<Object>} JSON response with reply, sources, and disclaimer
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
        body: JSON.stringify({ message: payload.message }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle safety filter blocks (400 status)
        if (response.status === 400) {
          return {
            reply: errorData.detail?.reply || "This type of request cannot be processed for safety reasons.",
            sources: [],
            disclaimer: "For medical concerns, please consult a licensed healthcare professional.",
            blocked: true,
          };
        }
        
        // Handle rate limiting (429 status)
        if (response.status === 429) {
          throw new Error("Too many requests. Please wait a moment before trying again.");
        }
        
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      // Ensure response includes disclaimer
      if (!data.disclaimer) {
        data.disclaimer = "This is general information and not a diagnosis. Consult a healthcare professional.";
      }
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
 * Uploads a PDF file to backend /ingest-pdf endpoint.
 * @param {File} file - PDF file to upload
 * @returns {Promise<Object>} Response with ingestion status
 */
export async function uploadMedicalPDF(file) {
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    throw new Error('Only PDF files are supported.');
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/ingest-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Uploads files to backend /upload endpoint (legacy).
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
