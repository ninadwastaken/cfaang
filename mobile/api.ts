const API_URL = process.env.EXPO_PUBLIC_API_URL?.trim().replace(/\/+$/, '');

interface HealthResponse {
  status: string;
}

export async function checkHealth(): Promise<string> {
  if (!API_URL) {
    throw new Error('EXPO_PUBLIC_API_URL is not configured.');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(`${API_URL}/health`, {
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`API returned status ${response.status}.`);
    }

    const data: HealthResponse = await response.json();
    if (data.status !== 'ok') {
      throw new Error('The API returned an unexpected health response.');
    }
    return data.status;
  } catch (error) {
    if (controller.signal.aborted) {
      throw new Error('Connection timed out. Check the API address and server.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
