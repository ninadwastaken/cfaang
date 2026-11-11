import type { Point } from '../../api';

export function coordinate(point: Point) {
  return { latitude: point.lat, longitude: point.lon };
}
/** NYC-area bounds with breathing room; minimum span handles coincident pins. */
export function mapRegion(points: Point[]) {
  const latitudes = points.map(point => point.lat);
  const longitudes = points.map(point => point.lon);
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);
  const minLon = Math.min(...longitudes);
  const maxLon = Math.max(...longitudes);
  return {
    latitude: (minLat + maxLat) / 2,
    longitude: (minLon + maxLon) / 2,
    latitudeDelta: Math.max((maxLat - minLat) * 1.4, 0.012),
    longitudeDelta: Math.max((maxLon - minLon) * 1.4, 0.012),
  };
}
