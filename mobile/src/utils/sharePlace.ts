import type { MeetingSpot } from '../../api';

export function sharePlaceContent(spot: Pick<MeetingSpot, 'name' | 'lat' | 'lon'>, address?: string | null) {
  const name = spot.name?.trim() || 'Meeting spot';
  const query = new URLSearchParams({ api: '1', destination: `${spot.lat},${spot.lon}` });
  const directions = `https://www.google.com/maps/dir/?${query}`;
  return {
    title: `${name} · Meet Me`,
    message: [`Let's meet at ${name}.`, address?.trim(), `Directions: ${directions}`].filter(Boolean).join('\n'),
  };
}
