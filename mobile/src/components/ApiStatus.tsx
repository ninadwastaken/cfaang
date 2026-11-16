import { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { checkHealth, checkReadiness } from '../../api';
import { ui } from './ui';

type Connection = { api: 'checking' | 'ok' | 'error'; database: 'waiting' | 'checking' | 'ok' | 'error'; error?: string };
const initial: Connection = { api: 'checking', database: 'waiting' };
export default function ApiStatus() {
  const [attempt, setAttempt] = useState(0);
  const [connection, setConnection] = useState<Connection>(initial);
  useEffect(() => {
    const controller = new AbortController();
    checkHealth(controller.signal).then(async () => {
      if (controller.signal.aborted) return;
      setConnection({ api: 'ok', database: 'checking' });
      try {
        await checkReadiness(controller.signal);
        if (!controller.signal.aborted) setConnection({ api: 'ok', database: 'ok' });
      } catch (error) {
        if (!controller.signal.aborted) setConnection({ api: 'ok', database: 'error', error: error instanceof Error ? error.message : 'Could not reach the database.' });
      }
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setConnection({ api: 'error', database: 'waiting', error: error instanceof Error ? error.message : 'Could not reach the API.' });
    });
    return () => controller.abort();
  }, [attempt]);
  const checking = connection.api === 'checking' || connection.database === 'checking';
  return <View style={ui.card}>
    <Text style={ui.label}>Connection status</Text>
    <View style={{ gap: 8 }} accessibilityLiveRegion="polite">
      <Text style={ui.body}>API: {connection.api === 'ok' ? 'Connected' : connection.api === 'checking' ? 'Checking…' : 'Unavailable'}</Text>
      <Text style={ui.body}>Database: {connection.database === 'ok' ? 'Reachable' : connection.database === 'checking' ? 'Checking…' : connection.database === 'error' ? 'Unavailable' : 'Not checked'}</Text>
      {!!connection.error && <Text style={ui.error}>{connection.error}</Text>}
      {connection.database === 'ok' && <Text style={ui.body}>Database connectivity confirmed. This does not check whether places have been imported.</Text>}
    </View>
    <Pressable accessibilityRole="button" accessibilityState={{ disabled: checking }} disabled={checking} onPress={() => {
      setConnection(initial);
      setAttempt(value => value + 1);
    }} style={[ui.button, checking && { opacity: 0.6 }]}><Text style={ui.buttonText}>{checking ? 'Checking connection…' : 'Check again'}</Text></Pressable>
  </View>;
}
