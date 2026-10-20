export const categories = ['Cafés', 'Parks', 'Museums'] as const;
export type Category = typeof categories[number];

export interface MeetingSpot {
  name: string;
  neighborhood: string;
  dist_1: number;
  dist_2: number;
}

// Deliberately fictional fixtures: replace this source with /meet when ready.
export const demoSpots: Record<Category, MeetingSpot[]> = {
  Cafés: [
    { name: 'Corner Cup · Sample café', neighborhood: 'A cozy place to catch up', dist_1: 1200, dist_2: 1400 },
    { name: 'Sunday Table · Sample café', neighborhood: 'Coffee and a little extra time', dist_1: 1700, dist_2: 1100 },
    { name: 'Greenhouse Coffee · Sample café', neighborhood: 'Room for a long conversation', dist_1: 1500, dist_2: 1900 },
  ],
  Parks: [
    { name: 'Garden Square · Sample park', neighborhood: 'Find a bench and take a break', dist_1: 900, dist_2: 1100 },
    { name: 'Riverside Lawn · Sample park', neighborhood: 'An open-air afternoon', dist_1: 1800, dist_2: 1500 },
  ],
  Museums: [
    { name: 'City Gallery · Sample museum', neighborhood: 'Something new to explore together', dist_1: 1400, dist_2: 1600 },
    { name: 'The History Room · Sample museum', neighborhood: 'Make a day of it', dist_1: 2100, dist_2: 1700 },
  ],
};
