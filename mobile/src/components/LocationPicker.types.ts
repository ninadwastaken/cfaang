import type { StartingLocation } from '../utils/startingLocation';
export interface LocationPickerProps {
  label: string;
  value: StartingLocation;
  onChange: (point: StartingLocation) => void;
}
