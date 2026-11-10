import { useEffect, useState } from 'react';
import { router, useLocalSearchParams } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { categories, getMeetingSpots, MeetingResponse, MeetingSort } from '../../api';
import { colors, ui } from '../components/ui';
import { findLandmark } from '../data/landmarks';
import DirectionsButton from '../components/DirectionsButton';

type SearchState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'success'; data: MeetingResponse };

export default function Results() {
  const params = useLocalSearchParams<{ from?: string; to?: string; category?: string }>();
  return <MeetingResults key={`${params.from}:${params.to}:${params.category}`} params={params} />;
}

function MeetingResults({ params }: { params: { from?: string; to?: string; category?: string } }) {
  const person1 = findLandmark(params.from);
  const person2 = findLandmark(params.to);
  const category = categories.find(value => value === params.category);
  const [sort, setSort] = useState<MeetingSort>('fair');
  const [radius, setRadius] = useState(5000);
  const [attempt, setAttempt] = useState(0);
  const [searchState, setState] = useState<SearchState>({ status: 'loading' });
  const valid = !!person1 && !!person2 && !!category;
  const state: SearchState = valid ? searchState : { status: 'error', message: 'Choose two landmarks and a category to find meeting spots.' };
  const searchedRadius = state.status === 'success' ? state.data.radius : radius;
  const nextRadius = Math.min(searchedRadius * 3, 10000);
  useEffect(() => {
    if (!person1 || !person2 || !category) {
      return;
    }
    const controller = new AbortController();
    getMeetingSpots(person1, person2, category, radius, controller.signal, sort)
      .then(data => { if (!controller.signal.aborted) setState({ status: 'success', data }); })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setState({ status: 'error', message: error instanceof Error ? error.message : 'Could not load meeting spots.' });
      });
    return () => controller.abort();
  }, [person1, person2, category, radius, attempt, sort]);
  function edit() {
    if (router.canGoBack()) router.back();
    else router.replace('/');
  }
  return <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>
    <ScrollView contentContainerStyle={ui.content}>
      <Text style={ui.eyebrow}>MEETING SPOTS{category ? ` · ${category.toUpperCase()}` : ''}</Text>
      <Text style={ui.title}>Make time{'\n'}to meet.</Text>
      {valid && <Text style={ui.body}>{person1.name} ↔ {person2.name}</Text>}
      <View style={ui.notice}><Text style={ui.noticeText}>Places near your geographic midpoint. Distances and differences are straight-line estimates, not walking or transit times. Place details may be incomplete or outdated.</Text></View>
      {valid && <Text style={ui.body}>{state.status === 'success' ? 'Searched' : 'Starting search'} within {searchedRadius / 1000} km of your midpoint.</Text>}
      {valid && <View style={{ gap: 10 }}>
        <Text style={ui.label}>Sort recommendations</Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
          {([{ value: 'fair', label: 'Fairest' }, { value: 'closest', label: 'Closest to midpoint' }] as const).map(option =>
            <Pressable key={option.value} accessibilityRole="button" accessibilityState={{ selected: sort === option.value }}
              style={[ui.button, { flexGrow: 1, backgroundColor: sort === option.value ? colors.green : '#E5EBDD' }]}
              onPress={() => {
                if (sort === option.value) return;
                setState({ status: 'loading' });
                setSort(option.value);
              }}>
              <Text style={[ui.buttonText, { color: sort === option.value ? '#FFFFFF' : colors.green }]}>{option.label}</Text>
            </Pressable>)}
        </View>
        <Text style={ui.body}>
          {sort === 'fair'
            ? 'Fairest prioritizes a shorter straight-line distance for the person farther away. Ties favor a smaller distance difference.'
            : 'Closest to midpoint orders places by their straight-line distance from your geographic midpoint.'}
        </Text>
      </View>}
      <View accessibilityLiveRegion="polite" style={{ gap: 20 }}>
        {state.status === 'loading' && <View style={ui.card}><ActivityIndicator color={colors.green} /><Text style={ui.body}>Finding places for both of you…</Text></View>}
        {state.status === 'error' && <View style={ui.card}>
          <Text accessibilityRole="alert" style={ui.error}>{state.message}</Text>
          {valid && <Pressable accessibilityRole="button" style={ui.button} onPress={() => { setState({ status: 'loading' }); setAttempt(value => value + 1); }}><Text style={ui.buttonText}>Try again</Text></Pressable>}
        </View>}
        {state.status === 'success' && <>
          <Text style={ui.label}>{state.data.count} {state.data.count === 1 ? 'place' : 'places'} found</Text>
          {state.data.Spots.length === 0 && <View style={ui.card}>
            <Text style={ui.label}>No places found nearby</Text>
            <Text style={ui.body}>{searchedRadius < 10000 ? 'Try another category or expand the search around your midpoint.' : 'Try another category or change your starting locations.'}</Text>
            {searchedRadius < 10000 && <Pressable accessibilityRole="button" style={ui.button} onPress={() => { setState({ status: 'loading' }); setRadius(nextRadius); }}><Text style={ui.buttonText}>Search within {nextRadius / 1000} km</Text></Pressable>}
          </View>}
          {state.data.Spots.map((spot, index) => <View key={`${spot.lat}:${spot.lon}:${index}`} style={ui.card}>
            <Text style={ui.eyebrow}>OPTION {index + 1}</Text>
            <Text style={[ui.label, { fontSize: 22 }]}>{spot.name?.trim() || `Unnamed ${category === 'Cafés' ? 'café' : category === 'Parks' ? 'park' : 'museum'}`}</Text>
            <View style={{ flexDirection: 'row', gap: 24, flexWrap: 'wrap' }}>
              <View><Text style={ui.label}>{(spot.dist_1 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From your landmark</Text></View>
              <View><Text style={ui.label}>{(spot.dist_2 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From their landmark</Text></View>
            </View>
            <View style={{ backgroundColor: '#E5EBDD', borderRadius: 12, padding: 12, gap: 4 }}>
              <Text style={ui.label}>Distance difference · {spot.gap.toLocaleString()} m</Text>
              <Text style={ui.body}>
                {spot.gap === 0
                  ? 'Equal distance from both landmarks, rounded to meters.'
                  : `Farther from ${spot.dist_1 > spot.dist_2 ? 'your' : 'their'} starting landmark.`}
              </Text>
            </View>
            {person1 && <DirectionsButton origin={person1} destination={spot} person="your" />}
            {person2 && <DirectionsButton origin={person2} destination={spot} person="their" />}
          </View>)}
        </>}
      </View>
      <Pressable accessibilityRole="button" style={ui.button} onPress={edit}><Text style={ui.buttonText}>Edit starting locations</Text></Pressable>
    </ScrollView>
  </SafeAreaView>;
}
