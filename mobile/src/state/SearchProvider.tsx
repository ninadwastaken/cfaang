import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, useContext, useEffect, useRef, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';
import { ActivityIndicator, Text, View } from 'react-native';
import { landmarks } from '../data/landmarks';
import { decodeSearch, encodeSearch, SearchDraft } from '../utils/savedSearch';
import { colors, ui } from '../components/ui';

const KEY = '@meet-me/last-search-v1';
const defaults: SearchDraft = { person1: landmarks[0], person2: landmarks[1], category: 'Cafés', sort: 'fair' };
const SearchContext = createContext<{
  draft: SearchDraft; setDraft: Dispatch<SetStateAction<SearchDraft>>; storageError: string; reset: () => void;
} | null>(null);

export function SearchProvider({ children }: { children: ReactNode }) {
  const [draft, setDraft] = useState<SearchDraft>(defaults);
  const [ready, setReady] = useState(false);
  const [restoreError, setRestoreError] = useState('');
  const [saveError, setSaveError] = useState('');
  const writes = useRef<Promise<void>>(Promise.resolve());
  useEffect(() => {
    let active = true;
    AsyncStorage.getItem(KEY).then(raw => {
      if (!active) return;
      const saved = decodeSearch(raw);
      if (saved) setDraft(saved);
      else if (raw) setRestoreError('Saved search was invalid. Starting with default locations.');
    }).catch(() => {
      if (active) setRestoreError('Could not restore the last search. Starting with defaults.');
    }).finally(() => { if (active) setReady(true); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!ready) return;
    let active = true;
    // Serialize writes so a slow earlier save cannot overwrite a newer selection.
    const raw = encodeSearch(draft);
    writes.current = writes.current.catch(() => {}).then(() => AsyncStorage.setItem(KEY, raw));
    writes.current.then(() => { if (active) setSaveError(''); }).catch(() => {
      if (active) setSaveError('Could not save this search. Your selections still work for this session.');
    });
    return () => { active = false; };
  }, [draft, ready]);
  if (!ready) return <View style={[ui.screen, { justifyContent: 'center', alignItems: 'center', gap: 12 }]}><ActivityIndicator color={colors.green} /><Text style={ui.body}>Restoring last search…</Text></View>;
  return <SearchContext.Provider value={{ draft, setDraft, storageError: saveError || restoreError, reset: () => { setRestoreError(''); setDraft({ ...defaults }); } }}>{children}</SearchContext.Provider>;
}
export function useSearch() {
  const search = useContext(SearchContext);
  if (!search) throw new Error('SearchProvider is required.');
  return search;
}
