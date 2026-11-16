/** Format optional place tags without guessing missing address information. */
export function placeDetails(properties: Record<string, unknown>) {
  function text(key: string): string | null {
    const value = properties[key];
    return typeof value === 'string' ? value.trim() || null : null;
  }

  const street = text('addr:street');
  const streetAddress = street
    ? [text('addr:housenumber'), street].filter(Boolean).join(' ')
    : null;
  const address = text('addr:full') || (streetAddress
    ? [streetAddress, text('addr:city'), text('addr:postcode')].filter(Boolean).join(', ')
    : null);

  return { address, hours: text('opening_hours') };
}
