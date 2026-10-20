import { router, useLocalSearchParams } from 'expo-router';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ui } from '../components/ui';
import { categories, demoSpots } from '../data/demo';

export default function Results() {
  const params = useLocalSearchParams<{ person1?: string; person2?: string; category?: string }>();
  const category = categories.find(value => value === params.category) ?? 'Cafés';
  const person1 = typeof params.person1 === 'string' ? params.person1 : '';
  const person2 = typeof params.person2 === 'string' ? params.person2 : '';
  function edit() {
    if (router.canGoBack()) router.back();
    else router.replace('/');
  }
  return <SafeAreaView edges={['bottom', 'left', 'right']} style={ui.screen}>
    <ScrollView contentContainerStyle={ui.content}>
      <Text style={ui.eyebrow}>SAMPLE RESULTS · {category.toUpperCase()}</Text>
      <Text style={ui.title}>Make time{ '\n' }to meet.</Text>
      <Text style={ui.body}>{person1 && person2 ? `${person1} ↔ ${person2}` : 'Two starting points, one shared plan.'}</Text>
      <View style={ui.notice}>
        <Text style={ui.noticeText}>These fictional places and distances are examples, not recommendations calculated for your locations. Live matching and directions are coming later.</Text>
      </View>
      {demoSpots[category].map((spot, index) => <View key={spot.name} style={ui.card}>
        <Text style={ui.eyebrow}>OPTION {index + 1} · {category.toUpperCase()}</Text>
        <Text style={[ui.label, { fontSize: 22 }]}>{spot.name}</Text>
        <Text style={ui.body}>{spot.neighborhood}</Text>
        <View style={{ flexDirection: 'row', gap: 24, flexWrap: 'wrap' }}>
          <View><Text style={ui.label}>{(spot.dist_1 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From you · sample</Text></View>
          <View><Text style={ui.label}>{(spot.dist_2 / 1000).toFixed(1)} km</Text><Text style={ui.body}>From them · sample</Text></View>
        </View>
      </View>)}
      <Text style={ui.body}>Example straight-line distances, not travel times.</Text>
      <Pressable accessibilityRole="button" style={ui.button} onPress={edit}><Text style={ui.buttonText}>Edit starting locations</Text></Pressable>
    </ScrollView>
  </SafeAreaView>;
}
