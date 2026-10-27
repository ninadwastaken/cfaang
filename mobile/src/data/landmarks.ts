// Approximate landmark coordinates, not live device locations or address results.
export const landmarks = [
  { id: 'union-square', name: 'Union Square, Manhattan', lat: 40.7359, lon: -73.9911 },
  { id: 'grand-central', name: 'Grand Central, Manhattan', lat: 40.7527, lon: -73.9772 },
  { id: 'penn-station', name: 'Penn Station, Manhattan', lat: 40.7506, lon: -73.9935 },
  { id: 'washington-square', name: 'Washington Square, Manhattan', lat: 40.7308, lon: -73.9973 },
  { id: 'borough-hall', name: 'Borough Hall, Brooklyn', lat: 40.6924, lon: -73.9903 },
  { id: 'atlantic-terminal', name: 'Atlantic Terminal, Brooklyn', lat: 40.6842, lon: -73.9776 },
] as const;
export function findLandmark(id: unknown) {
  return landmarks.find(landmark => landmark.id === id);
}
