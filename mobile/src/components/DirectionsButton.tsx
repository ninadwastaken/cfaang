import { useState } from 'react';
import { Linking, Pressable, Text, View } from 'react-native';
import type { Point } from '../../api';
import { ui } from './ui';

export default function DirectionsButton({ origin, destination }: { origin: Point; destination: Point }) {
  const [error, setError] = useState('');
  async function open() {
    setError('');
    const query = new URLSearchParams({ api: '1', origin: `${origin.lat},${origin.lon}`, destination: `${destination.lat},${destination.lon}` });
    try {
      await Linking.openURL(`https://www.google.com/maps/dir/?${query}`);
    } catch {
      setError('Could not open maps. Please try again.');
    }
  }
  return <View style={{ gap: 8 }}>
    <Pressable accessibilityRole="link" accessibilityLabel="Directions from your landmark in Google Maps" style={ui.button} onPress={open}><Text style={ui.buttonText}>Directions from your landmark ↗</Text></Pressable>
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </View>;
}
