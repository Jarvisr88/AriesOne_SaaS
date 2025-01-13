import React, { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Info } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import {
  Name,
  NameComponentProps,
  nameSchema,
  NAME_PREFIXES,
  NAME_SUFFIXES,
  PRONOUNS,
} from "@/types/name";
import { nameLocalization } from "@/lib/name-localization";

export function NameForm({
  value,
  onChange,
  onValidate,
  readOnly = false,
  className,
  locale = "en-US",
}: NameComponentProps) {
  const localization = new nameLocalization(locale);
  const labels = localization.getLabels();
  const placeholders = localization.getPlaceholders();

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<Name>({
    resolver: zodResolver(nameSchema),
    defaultValues: value,
  });

  useEffect(() => {
    onValidate?.(isValid);
  }, [isValid, onValidate]);

  const handleFormSubmit = (data: Name) => {
    onChange(data);
  };

  const formValues = watch();
  const pronouns = watch("pronouns");

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      onChange={() => handleSubmit(handleFormSubmit)()}
      className={cn("space-y-4", className)}
    >
      {/* Title and First Name */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label htmlFor="prefix">{labels.prefix}</Label>
          <Controller
            name="prefix"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onValueChange={field.onChange}
                disabled={readOnly}
              >
                <SelectTrigger>
                  <SelectValue placeholder={placeholders.prefix} />
                </SelectTrigger>
                <SelectContent>
                  {NAME_PREFIXES.map((prefix) => (
                    <SelectItem key={prefix.value} value={prefix.value}>
                      {localization.getPrefixLabel(prefix.value)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>

        <div className="md:col-span-3 space-y-2">
          <Label htmlFor="firstName" className="flex items-center gap-2">
            {labels.firstName}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Enter your legal first name</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Label>
          <Input
            id="firstName"
            {...register("firstName")}
            placeholder={placeholders.firstName}
            className={errors.firstName ? "border-red-500" : ""}
            disabled={readOnly}
          />
          {errors.firstName && (
            <p className="text-sm text-red-500">
              {localization.validateField("firstName", formValues.firstName || "")}
            </p>
          )}
        </div>
      </div>

      {/* Middle and Last Name */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="middleName">{labels.middleName}</Label>
          <Input
            id="middleName"
            {...register("middleName")}
            placeholder={placeholders.middleName}
            className={errors.middleName ? "border-red-500" : ""}
            disabled={readOnly}
          />
          {errors.middleName && (
            <p className="text-sm text-red-500">
              {localization.validateField("middleName", formValues.middleName || "")}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="lastName">{labels.lastName}</Label>
          <Input
            id="lastName"
            {...register("lastName")}
            placeholder={placeholders.lastName}
            className={errors.lastName ? "border-red-500" : ""}
            disabled={readOnly}
          />
          {errors.lastName && (
            <p className="text-sm text-red-500">
              {localization.validateField("lastName", formValues.lastName || "")}
            </p>
          )}
        </div>
      </div>

      {/* Suffix and Preferred Name */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label htmlFor="suffix">{labels.suffix}</Label>
          <Controller
            name="suffix"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onValueChange={field.onChange}
                disabled={readOnly}
              >
                <SelectTrigger>
                  <SelectValue placeholder={placeholders.suffix} />
                </SelectTrigger>
                <SelectContent>
                  {NAME_SUFFIXES.map((suffix) => (
                    <SelectItem key={suffix.value} value={suffix.value}>
                      {localization.getSuffixLabel(suffix.value)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>

        <div className="md:col-span-3 space-y-2">
          <Label htmlFor="preferredName" className="flex items-center gap-2">
            {labels.preferredName}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>What would you like to be called?</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Label>
          <Input
            id="preferredName"
            {...register("preferredName")}
            placeholder={placeholders.preferredName}
            className={errors.preferredName ? "border-red-500" : ""}
            disabled={readOnly}
          />
          {errors.preferredName && (
            <p className="text-sm text-red-500">
              {localization.validateField("preferredName", formValues.preferredName || "")}
            </p>
          )}
        </div>
      </div>

      {/* Pronunciation and Pronouns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="pronunciation" className="flex items-center gap-2">
            {labels.pronunciation}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Help others pronounce your name correctly</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Label>
          <Input
            id="pronunciation"
            {...register("pronunciation")}
            placeholder={placeholders.pronunciation}
            disabled={readOnly}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pronouns">{labels.pronouns}</Label>
          <Controller
            name="pronouns"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onValueChange={field.onChange}
                disabled={readOnly}
              >
                <SelectTrigger>
                  <SelectValue placeholder={placeholders.pronouns} />
                </SelectTrigger>
                <SelectContent>
                  {PRONOUNS.map((pronoun) => (
                    <SelectItem key={pronoun.value} value={pronoun.value}>
                      {localization.getPronounLabel(pronoun.value)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
          {pronouns === "custom" && (
            <Input
              {...register("pronouns")}
              placeholder="Enter your pronouns"
              className="mt-2"
              disabled={readOnly}
            />
          )}
        </div>
      </div>
    </form>
  );
}
