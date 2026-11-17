import { Text } from 'react-native';
import type { LocationPickerProps } from './LocationPicker.types';
import { ui } from './ui';
export default function LocationPicker(_props: LocationPickerProps) {
  return <Text style={ui.body}>Map picking is available in the iOS and Android app. You can choose a landmark here.</Text>;
}
