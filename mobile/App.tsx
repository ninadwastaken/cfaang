import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { checkHealth } from './api';

export default function App() {
  const [attempt, setAttempt] = useState(0);
  const [connection, setConnection] = useState<'loading' | 'connected' | 'error'>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    checkHealth()
      .then(() => {
        if (active) setConnection('connected');
      })
      .catch((cause: unknown) => {
        if (active) {
          setError(cause instanceof Error ? cause.message : 'Unable to reach the API.');
          setConnection('error');
        }
      });
    return () => { active = false; };
  }, [attempt]);

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
      <View style={styles.connection} accessibilityLiveRegion="polite">
        <Text style={styles.connectionText}>
          {connection === 'loading' ? 'Connecting to Meet Me…' :
            connection === 'connected' ? 'Connected to Meet Me' : 'Could not connect'}
        </Text>
        {connection === 'error' && (
          <>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable
              accessibilityRole="button"
              style={styles.retryButton}
              onPress={() => {
                setConnection('loading');
                setAttempt(value => value + 1);
              }}
            >
              <Text style={styles.retryText}>Try again</Text>
            </Pressable>
          </>
        )}
      </View>
      <StatusBar style="dark" />
    </View>
  );
}

const styles = StyleSheet.create({
  connection: {
    alignItems: 'center',
    marginTop: 32,
  },
  connectionText: {
    color: '#226B4A',
    fontSize: 14,
  },
  errorText: {
    color: '#92402D',
    marginTop: 8,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#226B4A',
    borderRadius: 12,
    marginTop: 12,
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  retryText: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
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
