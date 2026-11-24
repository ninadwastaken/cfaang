import { categories, meetingSorts } from '../../api';
import type { Category, MeetingSort } from '../../api';
import { parseLocation } from './startingLocation';
import type { StartingLocation } from './startingLocation';
export interface SearchDraft {
  person1: StartingLocation;
  person2: StartingLocation;
  category: Category;
  sort: MeetingSort;
}
export function decodeSearch(raw: string | null): SearchDraft | null {
  if (!raw) return null;
  try {
    const data = JSON.parse(raw);
    if (data?.version !== 1 || !categories.includes(data.category) || !meetingSorts.includes(data.sort)) return null;
    const person1 = parseLocation(JSON.stringify(data.person1));
    const person2 = parseLocation(JSON.stringify(data.person2));
    return person1 && person2 ? { person1, person2, category: data.category, sort: data.sort } : null;
  } catch { return null; }
}
export function encodeSearch(draft: SearchDraft) {
  return JSON.stringify({ version: 1, ...draft });
}
