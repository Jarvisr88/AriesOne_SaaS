import { z } from "zod";

export const nameSchema = z.object({
  prefix: z.string().optional(),
  firstName: z.string().min(1, "First name is required"),
  middleName: z.string().optional(),
  lastName: z.string().min(1, "Last name is required"),
  suffix: z.string().optional(),
  preferredName: z.string().optional(),
  pronunciation: z.string().optional(),
  pronouns: z.string().optional(),
});

export type Name = z.infer<typeof nameSchema>;

export interface NameComponentProps {
  value: Partial<Name>;
  onChange: (name: Name) => void;
  onValidate?: (isValid: boolean) => void;
  readOnly?: boolean;
  className?: string;
  locale?: string;
}

export const NAME_PREFIXES = [
  { value: "Mr", label: "Mr." },
  { value: "Mrs", label: "Mrs." },
  { value: "Ms", label: "Ms." },
  { value: "Dr", label: "Dr." },
  { value: "Prof", label: "Prof." },
] as const;

export const NAME_SUFFIXES = [
  { value: "Jr", label: "Jr." },
  { value: "Sr", label: "Sr." },
  { value: "II", label: "II" },
  { value: "III", label: "III" },
  { value: "IV", label: "IV" },
] as const;

export const PRONOUNS = [
  { value: "he/him", label: "he/him" },
  { value: "she/her", label: "she/her" },
  { value: "they/them", label: "they/them" },
  { value: "custom", label: "Custom" },
] as const;

export type NamePrefix = typeof NAME_PREFIXES[number]["value"];
export type NameSuffix = typeof NAME_SUFFIXES[number]["value"];
export type Pronoun = typeof PRONOUNS[number]["value"];
