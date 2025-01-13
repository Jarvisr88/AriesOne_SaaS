import React, { useEffect, useState, useCallback } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { debounce } from "lodash";
import { MapPin, Eye, EyeOff } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

import {
  Address,
  AddressComponentProps,
  AddressSuggestion,
  addressSchema,
  US_STATES,
} from "@/types/address";
import { googleMapsService } from "@/lib/google-maps";
import { addressLocalization } from "@/lib/address-localization";
import { MapView } from "./MapView";
import { AddressPreview } from "./AddressPreview";

interface AddressFormProps extends AddressComponentProps {
  locale?: string;
}

export function AddressForm({
  value,
  onChange,
  onValidate,
  readOnly = false,
  className,
  locale = "en-US",
}: AddressFormProps) {
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [sessionToken, setSessionToken] = useState<google.maps.places.AutocompleteSessionToken>();
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const localization = new addressLocalization(locale);
  const labels = localization.getLabels();
  const placeholders = localization.getPlaceholders();

  const {
    register,
    control,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isValid },
  } = useForm<Address>({
    resolver: zodResolver(addressSchema),
    defaultValues: value,
  });

  const formValues = watch();

  useEffect(() => {
    onValidate?.(isValid);
  }, [isValid, onValidate]);

  useEffect(() => {
    setSessionToken(new google.maps.places.AutocompleteSessionToken());
  }, []);

  const debouncedFetchSuggestions = useCallback(
    debounce(async (input: string) => {
      if (!input || input.length < 3) {
        setSuggestions([]);
        return;
      }

      try {
        const results = await googleMapsService.getPlaceSuggestions(
          input,
          sessionToken!,
          localization.getCountryCode()
        );
        setSuggestions(results);
      } catch (error) {
        console.error("Error fetching suggestions:", error);
        setSuggestions([]);
      }
    }, 300),
    [sessionToken, localization]
  );

  const handleAddressSelect = async (suggestion: AddressSuggestion) => {
    try {
      const details = await googleMapsService.getPlaceDetails(
        suggestion.placeId,
        sessionToken!
      );

      Object.entries(details.address).forEach(([key, value]) => {
        setValue(key as keyof Address, value);
      });

      setSessionToken(new google.maps.places.AutocompleteSessionToken());
      setShowSuggestions(false);

      onChange(details.address);
    } catch (error) {
      console.error("Error fetching address details:", error);
    }
  };

  const handleFormSubmit = (data: Address) => {
    onChange(data);
  };

  return (
    <div className={cn("space-y-6", className)}>
      <form
        onSubmit={handleSubmit(handleFormSubmit)}
        className="space-y-4"
        onChange={() => handleSubmit(handleFormSubmit)()}
      >
        <div className="flex items-center justify-between">
          <Label>{labels.street1}</Label>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowPreview(!showPreview)}
            className="h-8"
          >
            {showPreview ? (
              <>
                <EyeOff className="h-4 w-4 mr-2" />
                Hide Preview
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-2" />
                Show Preview
              </>
            )}
          </Button>
        </div>

        <Popover open={showSuggestions} onOpenChange={setShowSuggestions}>
          <PopoverTrigger asChild>
            <Input
              placeholder={placeholders.street1}
              onChange={(e) => debouncedFetchSuggestions(e.target.value)}
              className="w-full"
              disabled={readOnly}
            />
          </PopoverTrigger>
          <PopoverContent className="p-0" align="start">
            <Command>
              <CommandInput placeholder={placeholders.street1} />
              <CommandEmpty>No address found.</CommandEmpty>
              <CommandGroup>
                {suggestions.map((suggestion) => (
                  <CommandItem
                    key={suggestion.placeId}
                    onSelect={() => handleAddressSelect(suggestion)}
                  >
                    <MapPin className="mr-2 h-4 w-4" />
                    <div>
                      <div className="font-medium">{suggestion.mainText}</div>
                      <div className="text-sm text-muted-foreground">
                        {suggestion.secondaryText}
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </Command>
          </PopoverContent>
        </Popover>

        <div className="space-y-2">
          <Label htmlFor="street2">{labels.street2}</Label>
          <Input
            id="street2"
            {...register("street2")}
            placeholder={placeholders.street2}
            disabled={readOnly}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="city">{labels.city}</Label>
            <Input
              id="city"
              {...register("city")}
              placeholder={placeholders.city}
              className={errors.city ? "border-red-500" : ""}
              disabled={readOnly}
            />
            {errors.city && (
              <p className="text-sm text-red-500">
                {localization.validateField("city", formValues.city || "")}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="state">{labels.state}</Label>
            <Controller
              name="state"
              control={control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={readOnly}
                >
                  <SelectTrigger
                    className={errors.state ? "border-red-500" : ""}
                  >
                    <SelectValue placeholder={placeholders.state} />
                  </SelectTrigger>
                  <SelectContent>
                    {US_STATES.map((state) => (
                      <SelectItem key={state.value} value={state.value}>
                        {state.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {errors.state && (
              <p className="text-sm text-red-500">
                {localization.validateField("state", formValues.state || "")}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="zipCode">{labels.zipCode}</Label>
            <Input
              id="zipCode"
              {...register("zipCode")}
              placeholder={placeholders.zipCode}
              className={errors.zipCode ? "border-red-500" : ""}
              disabled={readOnly}
            />
            {errors.zipCode && (
              <p className="text-sm text-red-500">
                {localization.validateField("zipCode", formValues.zipCode || "")}
              </p>
            )}
          </div>
        </div>
      </form>

      <Collapsible open={showPreview} onOpenChange={setShowPreview}>
        <CollapsibleContent className="space-y-4">
          <AddressPreview
            address={formValues}
            locale={locale}
            className="mt-4"
          />
        </CollapsibleContent>
      </Collapsible>

      {formValues.latitude && formValues.longitude && (
        <div className="h-64">
          <MapView
            center={{ lat: formValues.latitude, lng: formValues.longitude }}
            zoom={15}
            markers={[
              {
                position: {
                  lat: formValues.latitude,
                  lng: formValues.longitude,
                },
                title: localization.formatAddress(formValues),
              },
            ]}
            className="w-full h-full rounded-md"
          />
        </div>
      )}
    </div>
  );
}
