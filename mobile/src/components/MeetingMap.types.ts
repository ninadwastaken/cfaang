import type { MeetingResponse, Point } from '../../api';
export interface MeetingMapProps {
  person1: Point & { name: string };
  person2: Point & { name: string };
  data: MeetingResponse;
  selected: number;
  onSelect: (index: number) => void;
}
