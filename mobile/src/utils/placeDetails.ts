/** Format only available OSM tags; never invent missing address components. */
export function placeDetails(properties: Record<string, string>) {
  const text = (key: string) => typeof properties[key] === 'string' ? properties[key].trim() : '';
  const street = [text('addr:housenumber'), text('addr:street')].filter(Boolean).join(' ');
  const locality = [text('addr:city'), text('addr:state'), text('addr:postcode')].filter(Boolean).join(', ');
  const address = text('addr:full') || [street, locality].filter(Boolean).join(', ');
  const category = ['amenity', 'leisure', 'tourism', 'historic', 'natural', 'shop']
    .map(text).find(Boolean)?.replace(/_/g, ' ');
  return { address: address || 'Address not listed', category: category || 'Category not listed' };
}
export function walkingEstimate(minutes: number | undefined) {
  return minutes === undefined ? 'Estimate unavailable' : minutes === 0 ? 'Under 1 min' : `About ${minutes} min`;
}
