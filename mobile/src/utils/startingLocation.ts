import type { Point } from '../../api';
export interface StartingLocation extends Point { name: string }
// Same broad NYC bounding box used by the backend (not a borough boundary).
export function inServiceArea(point: Point) {
  return Number.isFinite(point.lat) && Number.isFinite(point.lon) &&
    point.lat >= 40.47 && point.lat <= 40.93 && point.lon >= -74.27 && point.lon <= -73.69;
}
export function parseLocation(value: unknown): StartingLocation | null {
  if (typeof value !== 'string' || value.length > 1000) return null;
  try {
    const location = JSON.parse(value);
    return location && typeof location.name === 'string' && location.name.trim() && location.name.length <= 200 && inServiceArea(location)
      ? { name: location.name.trim(), lat: location.lat, lon: location.lon } : null;
  } catch { return null; }
}
export function pickedLocation(point: Point): StartingLocation {
  return { ...point, name: `Map point (${point.lat.toFixed(4)}, ${point.lon.toFixed(4)})` };
}
