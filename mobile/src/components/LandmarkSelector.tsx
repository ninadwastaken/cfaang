import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { findLandmark, landmarks } from '../data/landmarks';
import { colors, ui } from './ui';

export default function LandmarkSelector({ label, value, onChange, selectedName }: {
  label: string; selectedName?: string; value: string; onChange: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  return <View style={{ gap: 10 }}>
    <Text style={ui.label}>{label}</Text>
    <Pressable style={ui.input} accessibilityRole="button" accessibilityLabel={`${label}: ${selectedName ?? findLandmark(value)?.name ?? 'Choose a landmark'}`} accessibilityState={{ expanded }} onPress={() => setExpanded(current => !current)}>
      <Text style={ui.body}>{selectedName ?? findLandmark(value)?.name ?? 'Choose a landmark'} {expanded ? '▴' : '▾'}</Text>
    </Pressable>
    {expanded && landmarks.map(landmark => <Pressable key={landmark.id} accessibilityRole="button" accessibilityState={{ selected: landmark.id === value }} style={[ui.button, { backgroundColor: landmark.id === value ? colors.green : '#E5EBDD' }]} onPress={() => { onChange(landmark.id); setExpanded(false); }}>
      <Text style={[ui.buttonText, { color: landmark.id === value ? '#FFFFFF' : colors.green }]}>{landmark.name}</Text>
    </Pressable>)}
  </View>;
}
