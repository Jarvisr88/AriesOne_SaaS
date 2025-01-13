export interface ValidationRule {
  name: string;
  description?: string;
  validate: (value: any) => string | null;
}
