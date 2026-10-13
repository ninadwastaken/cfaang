const API_URL = process.env.EXPO_PUBLIC_API_URL;

interface HealthResponse {
  status: string;
}

export async function checkHealth(): Promise<string> {
  if (!API_URL) {
    throw new Error('EXPO_PUBLIC_API_URL is not configured.');
  }

  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`API returned status ${response.status}.`);
  }

  const data: HealthResponse = await response.json();
  return data.status;
}
