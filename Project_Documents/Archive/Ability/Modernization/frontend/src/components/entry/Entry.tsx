import React, { useId, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { EntryConfig } from "@/types/entry";
import { useEntry } from "@/hooks/useEntry";
import { useForm } from "@/components/form/FormContext";

interface EntryProps<T> extends Omit<EntryConfig<T>, "onChange" | "onValidate"> {
  name: string;
  tooltip?: string;
  type?: string;
}

export function Entry<T>({
  name,
  initialValue,
  placeholder,
  label,
  required,
  disabled,
  readOnly,
  autoFocus,
  className,
  validation,
  formatter,
  schema,
  tooltip,
  type = "text",
}: EntryProps<T>) {
  const id = useId();
  const {
    registerField,
    unregisterField,
    getFieldValue,
    setFieldValue,
    validateField,
    state: { fields },
  } = useForm();

  const field = fields[name];

  const {
    displayValue,
    isValid,
    isDirty,
    isTouched,
    error,
    handleChange,
    handleBlur,
  } = useEntry<T>({
    initialValue: field?.value ?? initialValue,
    validation,
    formatter,
    schema,
    onChange: (value) => setFieldValue(name, value),
    onValidate: () => validateField(name),
  });

  useEffect(() => {
    registerField(name, {
      initialValue,
      validation,
      schema,
      required,
    });

    return () => {
      unregisterField(name);
    };
  }, [name, initialValue, validation, schema, required, registerField, unregisterField]);

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <div className="flex items-center gap-2">
          <Label
            htmlFor={id}
            className={cn(
              required && "after:content-['*'] after:ml-0.5 after:text-red-500"
            )}
          >
            {label}
          </Label>
          {tooltip && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{tooltip}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      )}

      <Input
        id={id}
        name={name}
        type={type}
        value={displayValue}
        onChange={(e) => handleChange(e.target.value)}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={disabled}
        readOnly={readOnly}
        autoFocus={autoFocus}
        className={cn(
          !isValid && isDirty && "border-red-500",
          !isValid && isTouched && "border-red-500"
        )}
        aria-invalid={!isValid}
        aria-errormessage={error ? `${id}-error` : undefined}
        aria-required={required}
      />

      {error && isDirty && (
        <p
          id={`${id}-error`}
          className="text-sm text-red-500"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
