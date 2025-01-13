import React from "react";
import { FormProvider, FormConfig } from "./FormContext";
import { cn } from "@/lib/utils";

interface FormProps extends FormConfig {
  children: React.ReactNode;
  className?: string;
  id?: string;
}

export function Form({
  children,
  className,
  id,
  onSubmit,
  onError,
  initialValues,
  validateOnChange = true,
  validateOnBlur = true,
}: FormProps) {
  return (
    <FormProvider
      config={{
        onSubmit,
        onError,
        initialValues,
        validateOnChange,
        validateOnBlur,
      }}
    >
      {({ handleSubmit }) => (
        <form
          id={id}
          onSubmit={handleSubmit}
          className={cn("space-y-4", className)}
          noValidate
        >
          {children}
        </form>
      )}
    </FormProvider>
  );
}
