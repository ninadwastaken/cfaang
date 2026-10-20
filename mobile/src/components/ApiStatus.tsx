import { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { checkHealth } from '../../api';
import { ui } from './ui';

export default function ApiStatus() {
  const [attempt, setAttempt] = useState(0);
  const [status, setStatus] = useState('Checking API connection…');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    checkHealth().then(() => {
      if (active) setStatus('Connected to Meet Me');
    }).catch(() => {
      if (active) {
        setStatus('API unavailable. The sample preview still works.');
        setFailed(true);
      }
    });
    return () => { active = false; };
  }, [attempt]);
  return (
    <View style={{ gap: 8 }} accessibilityLiveRegion="polite">
      <Text style={ui.body}>{status}</Text>
      {failed && <Pressable accessibilityRole="button" onPress={() => {
        setFailed(false);
        setStatus('Checking API connection…');
        setAttempt(value => value + 1);
      }} style={ui.button}><Text style={ui.buttonText}>Retry connection</Text></Pressable>}
    </View>
  );
}
