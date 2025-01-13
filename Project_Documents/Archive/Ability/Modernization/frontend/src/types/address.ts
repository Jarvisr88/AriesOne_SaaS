import { z } from "zod";

export const addressSchema = z.object({
  street1: z.string().min(1, "Street address is required"),
  street2: z.string().optional(),
  city: z.string().min(1, "City is required"),
  state: z.string().min(2, "State is required"),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code format"),
  country: z.string().min(1, "Country is required"),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  placeId: z.string().optional(),
  formattedAddress: z.string().optional(),
});

export type Address = z.infer<typeof addressSchema>;

export interface AddressComponentProps {
  value: Partial<Address>;
  onChange: (address: Address) => void;
  onValidate?: (isValid: boolean) => void;
  readOnly?: boolean;
  className?: string;
}

export interface AddressSuggestion {
  placeId: string;
  mainText: string;
  secondaryText: string;
  fullText: string;
}

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface AddressDetails {
  address: Address;
  coordinates: Coordinates;
  placeId: string;
  formattedAddress: string;
}

export interface MapViewProps {
  center: Coordinates;
  zoom: number;
  markers?: Array<{
    position: Coordinates;
    title?: string;
    onClick?: () => void;
  }>;
  onMapClick?: (coordinates: Coordinates) => void;
  className?: string;
}

export const US_STATES = [
  { value: "AL", label: "Alabama" },
  { value: "AK", label: "Alaska" },
  // ... add all states
  { value: "WI", label: "Wisconsin" },
  { value: "WY", label: "Wyoming" },
] as const;

export type USState = typeof US_STATES[number]["value"];
