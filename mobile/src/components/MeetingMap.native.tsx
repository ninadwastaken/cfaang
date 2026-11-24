import { useRef } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { coordinate, mapRegion } from '../utils/mapRegion';
import { colors, ui } from './ui';
import type { MeetingMapProps } from './MeetingMap.types';

export default function MeetingMap({ person1, person2, data, selected, onSelect }: MeetingMapProps) {
  const map = useRef<MapView>(null);
  const points = [person1, person2, data.midpoint, ...data.Spots];
  function fit() {
    map.current?.fitToCoordinates(points.map(coordinate), {
      edgePadding: { top: 60, right: 50, bottom: 60, left: 50 }, animated: true,
    });
  }
  return <View style={{ gap: 12 }}>
    <Text style={ui.label}>Your meeting area</Text>
    <View style={{ height: 360, borderRadius: 16, overflow: 'hidden' }}>
      <MapView ref={map} style={StyleSheet.absoluteFill} initialRegion={mapRegion(points)} onMapReady={fit}
        accessibilityLabel="Map of both starting locations, midpoint, and meeting places" moveOnMarkerPress={false}>
        <Marker coordinate={coordinate(person1)} title="Your starting point" description={person1.name} pinColor="#2563EB" zIndex={2} />
        <Marker coordinate={coordinate(person2)} title="Their starting point" description={person2.name} pinColor="#B45309" zIndex={2} />
        <Marker coordinate={coordinate(data.midpoint)} title="Geographic midpoint" pinColor="#7C3AED" zIndex={3} />
        {data.Spots.map((spot, index) => <Marker key={`${spot.lat}:${spot.lon}:${index}`}
          coordinate={coordinate(spot)} title={`Option ${index + 1}: ${spot.name || 'Meeting place'}`}
          description="Details and directions appear below the map" pinColor={colors.green}
          opacity={index === selected ? 1 : 0.7} zIndex={index === selected ? 4 : 1}
          onPress={() => onSelect(index)} />)}
      </MapView>
    </View>
    <Text style={ui.body}>Blue: you · Brown: them · Purple: midpoint · Green: places</Text>
    <Text style={ui.body}>Tap a green pin to view that place below. Map pins follow the option numbers in the list.</Text>
    <Pressable accessibilityRole="button" style={ui.button} onPress={fit}><Text style={ui.buttonText}>Fit all places</Text></Pressable>
  </View>;
}
