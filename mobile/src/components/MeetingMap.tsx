import { Text, View } from 'react-native';
import type { MeetingMapProps } from './MeetingMap.types';
import { ui } from './ui';

// Metro selects MeetingMap.native.tsx on iOS and Android.
export default function MeetingMap(_props: MeetingMapProps) {
  return <View style={ui.card}><Text style={ui.body}>The interactive map is available in the iOS and Android app. Switch to List to browse all meeting places here.</Text></View>;
}
