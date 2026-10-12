import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>NYC</Text>
      </View>
      <Text style={styles.title}>Meet Me</Text>
      <Text style={styles.tagline}>Find a fair place to meet.</Text>
      <Text style={styles.description}>
        Pick a spot that works for everyone, wherever they are in the city.
      </Text>
      <StatusBar style="dark" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: '#F7F4EE',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  badge: {
    backgroundColor: '#226B4A',
    borderRadius: 24,
    marginBottom: 24,
    paddingHorizontal: 18,
    paddingVertical: 10,
  },
  badgeText: {
    color: '#F4B942',
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 2,
  },
  title: {
    color: '#18201B',
    fontSize: 48,
    fontWeight: '900',
    letterSpacing: -1.5,
  },
  tagline: {
    color: '#226B4A',
    fontSize: 20,
    fontWeight: '700',
    marginTop: 10,
    textAlign: 'center',
  },
  description: {
    color: '#657068',
    fontSize: 16,
    lineHeight: 24,
    marginTop: 16,
    maxWidth: 320,
    textAlign: 'center',
  },
});
