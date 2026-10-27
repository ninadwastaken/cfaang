import { useEffect, useState } from 'react';
import { router, useLocalSearchParams } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { categories, getMeetingSpots, MeetingResponse } from '../../api';
import { colors, ui } from '../components/ui';
import { findLandmark } from '../data/landmarks';

type SearchState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'success'; data: MeetingResponse };

export default function Results() {
  const params = useLocalSearchParams<{ from?: string; to?: string; category?: string }>();
  return <MeetingResults key={`${params.from}:${params.to}:${params.category}`} params={params} />;
}

function MeetingResults({ params }: { params: { from?: string; to?: string; category?: string } }) {
  const person1 = findLandmark(params.from);
  const person2 = findLandmark(params.to);
  const category = categories.find(value => value === params.category);
  const [radius, setRadius] = useState(1000);
  const [attempt, setAttempt] = useState(0);
  const [searchState, setState] = useState<SearchState>({ status: 'loading' });
  const valid = !!person1 && !!person2 && !!category;
  const state: SearchState = valid ? searchState : { status: 'error', message: 'Choose two landmarks and a category to find meeting spots.' };
  useEffect(() => {
    if (!person1 || !person2 || !category) {
      return;
    }
    const controller = new AbortController();
    getMeetingSpots(person1, person2, category, radius, controller.signal)
      .then(data => { if (!controller.signal.aborted) setState({ status: 'success', data }); })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setState({ status: 'error', message: error instanceof Error ? error.message : 'Could not load meeting spots.' });
      });
    return () => controller.abort();
  }, [person1, person2, category, radius, attempt]);
  function edit() {
    if (router.canGoBack()) router.back();
    else router.replace('/');
  }
  return <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>
    <ScrollView contentContainerStyle={ui.content}>
      <Text style={ui.eyebrow}>MEETING SPOTS{category ? ` · ${category.toUpperCase()}` : ''}</Text>
      <Text style={ui.title}>Make time{'\n'}to meet.</Text>
      {valid && <Text style={ui.body}>{person1.name} ↔ {person2.name}</Text>}
      <View style={ui.notice}><Text style={ui.noticeText}>Places near your geographic midpoint. Distances are straight-line distances, not walking or transit times. Place details may be incomplete or outdated.</Text></View>
      {valid && <Text style={ui.body}>Searching within {radius / 1000} km of your midpoint.</Text>}
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
            <Text style={ui.body}>Try another category or expand the search around your midpoint.</Text>
            {radius < 10000 && <Pressable accessibilityRole="button" style={ui.button} onPress={() => { setState({ status: 'loading' }); setRadius(value => Math.min(value * 3, 10000)); }}><Text style={ui.buttonText}>Search within {Math.min(radius * 3, 10000) / 1000} km</Text></Pressable>}
          </View>}
          {state.data.Spots.map((spot, index) => <View key={`${spot.lat}:${spot.lon}:${index}`} style={ui.card}>
            <Text style={ui.eyebrow}>OPTION {index + 1}</Text>
            <Text style={[ui.label, { fontSize: 22 }]}>{spot.name?.trim() || `Unnamed ${category === 'Cafés' ? 'café' : category === 'Parks' ? 'park' : 'museum'}`}</Text>
            <View style={{ flexDirection: 'row', gap: 24, flexWrap: 'wrap' }}>
              <View><Text style={ui.label}>{(spot.dist_1 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From your landmark</Text></View>
              <View><Text style={ui.label}>{(spot.dist_2 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From their landmark</Text></View>
            </View>
          </View>)}
        </>}
      </View>
      <Pressable accessibilityRole="button" style={ui.button} onPress={edit}><Text style={ui.buttonText}>Edit starting locations</Text></Pressable>
    </ScrollView>
  </SafeAreaView>;
}
