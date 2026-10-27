import { StyleSheet } from 'react-native';

export const colors = { background: '#F7F4EE', green: '#226B4A', ink: '#18201B', muted: '#657068' };
export const ui = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, gap: 20, width: '100%', maxWidth: 600, alignSelf: 'center' },
  eyebrow: { color: colors.green, fontSize: 12, fontWeight: '800', letterSpacing: 2 },
  title: { color: colors.ink, fontSize: 38, fontWeight: '900', letterSpacing: -1 },
  body: { color: colors.muted, fontSize: 16, lineHeight: 24 },
  label: { color: colors.ink, fontSize: 16, fontWeight: '700' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 20, padding: 20, gap: 12, borderWidth: 1, borderColor: '#E4E7DE' },
  input: { borderWidth: 1, borderColor: '#A6B5AA', borderRadius: 12, backgroundColor: '#FFFFFF', padding: 16, color: colors.ink, fontSize: 16, minHeight: 54 },
  button: { backgroundColor: colors.green, borderRadius: 14, padding: 18, alignItems: 'center', minHeight: 54 },
  buttonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '700' },
  notice: { backgroundColor: '#F4E8C8', padding: 16, borderRadius: 14, gap: 6 },
  noticeText: { color: '#665018', fontSize: 14, lineHeight: 21 },
  error: { color: '#92402D', fontSize: 14, lineHeight: 21 },
});
