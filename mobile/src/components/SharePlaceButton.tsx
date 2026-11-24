import { useRef, useState } from 'react';
import { findNodeHandle, Pressable, Share, Text, View } from 'react-native';
import type { MeetingSpot } from '../../api';
import { placeDetails } from '../data/place-details';
import { sharePlaceContent } from '../utils/sharePlace';
import { ui } from './ui';

export default function SharePlaceButton({ spot }: { spot: MeetingSpot }) {
  const anchor = useRef<View>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function share() {
    if (busy) return;
    setBusy(true);
    setError('');
    try {
      const node = findNodeHandle(anchor.current);
      await Share.share(sharePlaceContent(spot, placeDetails(spot.properties).address), {
        dialogTitle: 'Share meeting spot', anchor: node ?? undefined,
      });
    } catch {
      setError('Could not open sharing. Please try again.');
    } finally {
      setBusy(false);
    }
  }
  return <View ref={anchor} collapsable={false} style={{ gap: 8 }}>
    <Pressable accessibilityRole="button" accessibilityLabel={`Share ${spot.name?.trim() || 'meeting spot'}`} accessibilityState={{ disabled: busy }} disabled={busy} style={[ui.button, busy && { opacity: 0.6 }]} onPress={share}>
      <Text style={ui.buttonText}>{busy ? 'Opening share menu…' : 'Share this place'}</Text>
    </Pressable>
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </View>;
}
