import { useState } from 'react';
import { router } from 'expo-router';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ApiStatus from '../components/ApiStatus';
import { colors, ui } from '../components/ui';
import { categories } from '../../api';
import LandmarkSelector from '../components/LandmarkSelector';
import { useSearch } from '../state/SearchProvider';
import LocationPicker from '../components/LocationPicker';
import { inServiceArea } from '../utils/startingLocation';
import { findLandmark, landmarks } from '../data/landmarks';

export default function Home() {
  const { draft, setDraft, storageError, reset } = useSearch();
  const { person1, person2, category } = draft;
  const [error, setError] = useState('');
  function search() {
    if (!inServiceArea(person1) || !inServiceArea(person2)) {
      setError('Choose two starting points inside the NYC area.');
      return;
    }
    setError('');
    router.push({ pathname: '/results', params: { from: JSON.stringify(person1), to: JSON.stringify(person2), category } });
  }
  return (
    <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>

        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={ui.content}>
          <Text style={ui.eyebrow}>NYC · BETTER TOGETHER</Text>
          <Text style={ui.title}>A little closer{ '\n' }to both of you.</Text>
          <Text style={ui.body}>Two starting points. One place to catch up.</Text>
          <View style={ui.notice}>
            <Text style={ui.label}>Choose your starting points</Text>
            <Text style={ui.noticeText}>Pick any point in the NYC area on the map, or choose a landmark. Map points use coordinates rather than street addresses. We’ll find real places near the midpoint of your choices.</Text>
          </View>
          <View style={ui.card}>
            <LandmarkSelector label="Your starting location" selectedName={person1.name} value={landmarks.find(item => item.lat === person1.lat && item.lon === person1.lon)?.id ?? ''} onChange={id => { const point = findLandmark(id); if (point) setDraft(current => ({ ...current, person1: point })); }} />
            <LocationPicker label="Your starting location" value={person1} onChange={point => setDraft(current => ({ ...current, person1: point }))} />
            <LandmarkSelector label="Their starting location" selectedName={person2.name} value={landmarks.find(item => item.lat === person2.lat && item.lon === person2.lon)?.id ?? ''} onChange={id => { const point = findLandmark(id); if (point) setDraft(current => ({ ...current, person2: point })); }} />
            <LocationPicker label="Their starting location" value={person2} onChange={point => setDraft(current => ({ ...current, person2: point }))} />
          </View>
          <Text style={ui.label}>What are you in the mood for?</Text>
          <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
            {categories.map(value => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: category === value }} onPress={() => setDraft(current => ({ ...current, category: value }))} style={[ui.button, { backgroundColor: category === value ? colors.green : '#E5EBDD', flexGrow: 1 }]}>
              <Text style={[ui.buttonText, { color: category === value ? '#FFFFFF' : colors.green }]}>{value}</Text>
            </Pressable>)}
          </View>
          {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
          <Pressable accessibilityRole="button" style={ui.button} onPress={search}><Text style={ui.buttonText}>Find meeting spots →</Text></Pressable>
          <Text style={ui.body}>Starting points, category, and sort preference are saved on this device.</Text>
          {!!storageError && <Text accessibilityRole="alert" style={ui.error}>{storageError}</Text>}
          <Pressable accessibilityRole="button" style={ui.button} onPress={() => { reset(); setError(''); }}><Text style={ui.buttonText}>Reset saved search</Text></Pressable>
          <ApiStatus />
        </ScrollView>

    </SafeAreaView>
  );
}
