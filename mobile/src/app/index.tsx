import { useState } from 'react';
import { router } from 'expo-router';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ApiStatus from '../components/ApiStatus';
import { colors, ui } from '../components/ui';
import { categories, Category } from '../data/demo';

export default function Home() {
  const [person1, setPerson1] = useState('Union Square, Manhattan');
  const [person2, setPerson2] = useState('Downtown Brooklyn');
  const [category, setCategory] = useState<Category>('Cafés');
  const [error, setError] = useState('');
  function preview() {
    if (!person1.trim() || !person2.trim()) {
      setError('Enter a starting location for both people.');
      return;
    }
    setError('');
    router.push({ pathname: '/results', params: { person1: person1.trim(), person2: person2.trim(), category } });
  }
  return (
    <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={100}>
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={ui.content}>
          <Text style={ui.eyebrow}>NYC · BETTER TOGETHER</Text>
          <Text style={ui.title}>A little closer{ '\n' }to both of you.</Text>
          <Text style={ui.body}>Two starting points. One place to catch up.</Text>
          <View style={ui.notice}>
            <Text style={ui.label}>Sample preview</Text>
            <Text style={ui.noticeText}>Try the flow with example places. Addresses aren’t looked up yet, and results won’t change based on your starting locations.</Text>
          </View>
          <View style={ui.card}>
            <Text style={ui.label}>Your starting location</Text>
            <TextInput accessibilityLabel="Your starting location" style={ui.input} value={person1} onChangeText={setPerson1} placeholder="Address or neighborhood" placeholderTextColor={colors.muted} maxLength={160} returnKeyType="next" />
            <Text style={ui.label}>Their starting location</Text>
            <TextInput accessibilityLabel="Their starting location" style={ui.input} value={person2} onChangeText={setPerson2} placeholder="Address or neighborhood" placeholderTextColor={colors.muted} maxLength={160} returnKeyType="done" onSubmitEditing={preview} />
          </View>
          <Text style={ui.label}>What are you in the mood for?</Text>
          <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
            {categories.map(value => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: category === value }} onPress={() => setCategory(value)} style={[ui.button, { backgroundColor: category === value ? colors.green : '#E5EBDD', flexGrow: 1 }]}>
              <Text style={[ui.buttonText, { color: category === value ? '#FFFFFF' : colors.green }]}>{value}</Text>
            </Pressable>)}
          </View>
          {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
          <Pressable accessibilityRole="button" style={ui.button} onPress={preview}><Text style={ui.buttonText}>Preview meeting spots →</Text></Pressable>
          <ApiStatus />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
