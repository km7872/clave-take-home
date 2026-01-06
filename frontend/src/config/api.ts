// API configuration with environment variable support
// Uses VITE_API_BASE_URL from environment, defaults to localhost:8001 for development
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

/**
 * Get a full API URL for an endpoint
 * @param endpoint - API endpoint path (e.g., '/api/metrics/revenue' or 'api/metrics/revenue')
 * @returns Full URL including base URL and endpoint
 */
export const getApiUrl = (endpoint: string): string => {
  // Remove leading slash if present to avoid double slashes, then add it back
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
};

