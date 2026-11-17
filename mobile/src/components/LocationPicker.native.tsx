import { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MapView, { Marker } from 'react-native-maps';
import { coordinate } from '../utils/mapRegion';
import { inServiceArea, pickedLocation, StartingLocation } from '../utils/startingLocation';
import { colors, ui } from './ui';
import type { LocationPickerProps } from './LocationPicker.types';

export default function LocationPicker({ label, value, onChange }: LocationPickerProps) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<StartingLocation>(value);
  const [error, setError] = useState('');
  function pick(point: { latitude: number; longitude: number }) {
    const location = pickedLocation({ lat: point.latitude, lon: point.longitude });
    setDraft(location);
    setError(inServiceArea(location) ? '' : 'Choose a point inside the NYC service area.');
  }
  return <>
    <Pressable accessibilityRole="button" accessibilityLabel={`Pick ${label.toLowerCase()} on map`} style={ui.button} onPress={() => { setDraft(value); setError(''); setOpen(true); }}><Text style={ui.buttonText}>Pick on map</Text></Pressable>
    <Modal visible={open} animationType="slide" onRequestClose={() => setOpen(false)}>
      <SafeAreaView style={ui.screen}>
        <View style={{ padding: 20, gap: 8 }}>
          <Text style={ui.label}>{label}</Text>
          <Text style={ui.body}>Tap the map or drag the pin. Choose a point in the NYC area.</Text>
        </View>
        <View style={{ flex: 1 }}>
          <MapView key={open ? 'open' : 'closed'} style={StyleSheet.absoluteFill} initialRegion={{ ...coordinate(value), latitudeDelta: 0.12, longitudeDelta: 0.12 }}
            onPress={event => pick(event.nativeEvent.coordinate)} accessibilityLabel={`Choose ${label.toLowerCase()} on map`}>
            <Marker coordinate={coordinate(draft)} draggable title="Selected starting point" pinColor={colors.green} onDragEnd={event => pick(event.nativeEvent.coordinate)} />
          </MapView>
        </View>
        <View style={{ padding: 20, gap: 12 }}>
          <Text style={ui.body}>{draft.lat.toFixed(5)}, {draft.lon.toFixed(5)}</Text>
          {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
          <Pressable accessibilityRole="button" accessibilityState={{ disabled: !inServiceArea(draft) }} disabled={!inServiceArea(draft)} style={[ui.button, !inServiceArea(draft) && { opacity: 0.5 }]} onPress={() => { onChange(draft); setOpen(false); }}><Text style={ui.buttonText}>Use this starting point</Text></Pressable>
          <Pressable accessibilityRole="button" style={ui.button} onPress={() => setOpen(false)}><Text style={ui.buttonText}>Cancel</Text></Pressable>
        </View>
      </SafeAreaView>
    </Modal>
  </>;
}
