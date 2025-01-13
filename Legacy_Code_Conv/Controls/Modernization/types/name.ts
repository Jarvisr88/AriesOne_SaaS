export type Courtesy = 'Mr.' | 'Mrs.' | 'Ms.' | 'Dr.' | 'Prof.';

export interface Name {
  courtesy?: Courtesy;
  first_name: string;
  middle_name?: string;
  last_name: string;
  suffix?: string;
}
