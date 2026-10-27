const API_URL = process.env.EXPO_PUBLIC_API_URL?.trim().replace(/\/+$/, '');
export const categories = ['Cafés', 'Parks', 'Museums'] as const;
export type Category = typeof categories[number];
const filters: Record<Category, { category: string; type: string }> = {
  Cafés: { category: 'amenity', type: 'cafe' },
  Parks: { category: 'leisure', type: 'park' },
  Museums: { category: 'tourism', type: 'museum' },
};
export interface Point { lat: number; lon: number }
export interface MeetingSpot extends Point {
  name: string | null;
  dist_1: number;
  dist_2: number;
  dist_mid: number;
  properties: Record<string, string>;
}
export interface MeetingResponse { midpoint: Point; Spots: MeetingSpot[]; count: number }

async function request(path: string, signal?: AbortSignal): Promise<unknown> {
  if (!API_URL) throw new Error('EXPO_PUBLIC_API_URL is not configured.');
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) controller.abort();
  let timedOut = false;
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 10000);
  try {
    const response = await fetch(`${API_URL}${path}`, { signal: controller.signal });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body && typeof body.message === 'string' ? body.message : `API returned status ${response.status}.`);
    }
    return await response.json();
  } catch (error) {
    if (timedOut) throw new Error('Connection timed out. Check the API address and server.');
    if (signal?.aborted) throw error;
    if (error instanceof TypeError) throw new Error('Unable to reach Meet Me. Check your connection and the API server.');
    throw error;
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener('abort', abort);
  }
}
export async function checkHealth(): Promise<string> {
  const data = await request('/health') as { status?: unknown } | null;
  if (data?.status !== 'ok') throw new Error('The API returned an unexpected health response.');
  return data.status;
}
function isPoint(value: unknown): value is Point {
  if (!value || typeof value !== 'object') return false;
  const point = value as Point;
  return Number.isFinite(point.lat) && Math.abs(point.lat) <= 90 && Number.isFinite(point.lon) && Math.abs(point.lon) <= 180;
}
export async function getMeetingSpots(person1: Point, person2: Point, category: Category,
  radius = 1000, signal?: AbortSignal): Promise<MeetingResponse> {
  if (!isPoint(person1) || !isPoint(person2)) throw new Error('Choose two valid starting locations.');
  if (!Number.isFinite(radius) || radius <= 0 || radius > 10000) throw new Error('Search radius must be between 1 and 10000 meters.');
  const query = new URLSearchParams({ lat1: String(person1.lat), lon1: String(person1.lon),
    lat2: String(person2.lat), lon2: String(person2.lon), ...filters[category], radius: String(radius), limit: '50' });
  const data = await request(`/meet?${query}`, signal) as MeetingResponse | null;
  if (!data || !isPoint(data.midpoint) || !Array.isArray(data.Spots) || data.count !== data.Spots.length ||
      !data.Spots.every(spot => isPoint(spot) && (spot.name === null || typeof spot.name === 'string') &&
        [spot.dist_1, spot.dist_2, spot.dist_mid].every(distance => Number.isFinite(distance) && distance >= 0) &&
        spot.properties && typeof spot.properties === 'object')) {
    throw new Error('The API returned unexpected meeting results.');
  }
  return data;
}
