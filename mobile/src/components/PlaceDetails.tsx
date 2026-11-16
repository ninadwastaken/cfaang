import { Text, View } from 'react-native';
import { placeDetails } from '../data/place-details';
import { ui } from './ui';

export default function PlaceDetails({ properties }: { properties: Record<string, unknown> }) {
  const { address, hours } = placeDetails(properties);
  if (!address && !hours) return null;

  return <View style={{ gap: 8 }}>
    {address && <View>
      <Text style={ui.label}>Address</Text>
      <Text style={ui.body}>{address}</Text>
    </View>}
    {hours && <View>
      <Text style={ui.label}>Listed opening hours</Text>
      <Text style={ui.body}>{hours}</Text>
      <Text style={ui.body}>Confirm hours with the venue before heading out.</Text>
    </View>}
  </View>;
}
