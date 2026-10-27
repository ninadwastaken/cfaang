import { useState } from 'react';
import { router } from 'expo-router';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ApiStatus from '../components/ApiStatus';
import { colors, ui } from '../components/ui';
import { categories, Category } from '../../api';
import LandmarkSelector from '../components/LandmarkSelector';
import { findLandmark } from '../data/landmarks';

export default function Home() {
  const [person1, setPerson1] = useState('union-square');
  const [person2, setPerson2] = useState('grand-central');
  const [category, setCategory] = useState<Category>('Cafés');
  const [error, setError] = useState('');
  function search() {
    if (!findLandmark(person1) || !findLandmark(person2)) {
      setError('Choose a starting landmark for both people.');
      return;
    }
    setError('');
    router.push({ pathname: '/results', params: { person1: findLandmark(person1)!.name, person2: findLandmark(person2)!.name, from: person1, to: person2, category } });
  }
  return (
    <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>

        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={ui.content}>
          <Text style={ui.eyebrow}>NYC · BETTER TOGETHER</Text>
          <Text style={ui.title}>A little closer{ '\n' }to both of you.</Text>
          <Text style={ui.body}>Two starting points. One place to catch up.</Text>
          <View style={ui.notice}>
            <Text style={ui.label}>Start with a landmark</Text>
            <Text style={ui.noticeText}>Choose from NYC landmarks with approximate coordinates. Address search is coming later. We’ll find real places near the midpoint of your choices.</Text>
          </View>
          <View style={ui.card}>
            <LandmarkSelector label="Your starting location" value={person1} onChange={setPerson1} />
            <LandmarkSelector label="Their starting location" value={person2} onChange={setPerson2} />
          </View>
          <Text style={ui.label}>What are you in the mood for?</Text>
          <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
            {categories.map(value => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: category === value }} onPress={() => setCategory(value)} style={[ui.button, { backgroundColor: category === value ? colors.green : '#E5EBDD', flexGrow: 1 }]}>
              <Text style={[ui.buttonText, { color: category === value ? '#FFFFFF' : colors.green }]}>{value}</Text>
            </Pressable>)}
          </View>
          {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
          <Pressable accessibilityRole="button" style={ui.button} onPress={search}><Text style={ui.buttonText}>Find meeting spots →</Text></Pressable>
          <ApiStatus />
        </ScrollView>

    </SafeAreaView>
  );
}
