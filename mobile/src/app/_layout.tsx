import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { colors } from '../components/ui';

export default function Layout() {
  return <>
    <StatusBar style="dark" />
    <Stack screenOptions={{ headerStyle: { backgroundColor: colors.background }, headerTintColor: colors.green, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="index" options={{ title: 'Meet Me' }} />
      <Stack.Screen name="results" options={{ title: 'Your meeting spots', headerBackTitle: 'Edit' }} />
    </Stack>
  </>;
}
