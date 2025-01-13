import React, { createContext, useContext, useCallback, useReducer } from "react";
import { z } from "zod";

export interface FormField<T = any> {
  name: string;
  value: T;
  displayValue: string;
  isValid: boolean;
  isDirty: boolean;
  isTouched: boolean;
  error?: string;
}

export interface FormState {
  fields: Record<string, FormField>;
  isValid: boolean;
  isDirty: boolean;
  isSubmitting: boolean;
  submitCount: number;
  errors: Record<string, string>;
}

export type FormAction =
  | { type: "SET_FIELD"; payload: { name: string; field: FormField } }
  | { type: "SET_SUBMITTING"; payload: boolean }
  | { type: "INCREMENT_SUBMIT" }
  | { type: "RESET_FORM"; payload?: Partial<FormState> }
  | { type: "SET_ERRORS"; payload: Record<string, string> }
  | { type: "CLEAR_ERRORS" };

interface FormContextValue {
  state: FormState;
  dispatch: React.Dispatch<FormAction>;
  registerField: <T>(name: string, config: FormFieldConfig<T>) => void;
  unregisterField: (name: string) => void;
  getFieldValue: <T>(name: string) => T | undefined;
  setFieldValue: <T>(name: string, value: T) => void;
  validateField: (name: string) => boolean;
  validateForm: () => boolean;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  reset: () => void;
}

export interface FormFieldConfig<T> {
  initialValue?: T;
  validation?: Array<{
    validate: (value: T) => boolean;
    message: string;
  }>;
  schema?: z.ZodType<T>;
  required?: boolean;
  deps?: string[];
}

export interface FormConfig {
  onSubmit?: (values: Record<string, any>) => Promise<void> | void;
  onError?: (errors: Record<string, string>) => void;
  initialValues?: Record<string, any>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

const initialState: FormState = {
  fields: {},
  isValid: true,
  isDirty: false,
  isSubmitting: false,
  submitCount: 0,
  errors: {},
};

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case "SET_FIELD": {
      const { name, field } = action.payload;
      const newFields = {
        ...state.fields,
        [name]: field,
      };
      const isValid = Object.values(newFields).every((field) => field.isValid);
      const isDirty = Object.values(newFields).some((field) => field.isDirty);
      return {
        ...state,
        fields: newFields,
        isValid,
        isDirty,
      };
    }
    case "SET_SUBMITTING":
      return {
        ...state,
        isSubmitting: action.payload,
      };
    case "INCREMENT_SUBMIT":
      return {
        ...state,
        submitCount: state.submitCount + 1,
      };
    case "RESET_FORM":
      return {
        ...initialState,
        ...action.payload,
      };
    case "SET_ERRORS":
      return {
        ...state,
        errors: action.payload,
        isValid: Object.keys(action.payload).length === 0,
      };
    case "CLEAR_ERRORS":
      return {
        ...state,
        errors: {},
        isValid: true,
      };
    default:
      return state;
  }
}

const FormContext = createContext<FormContextValue | undefined>(undefined);

export function FormProvider({
  children,
  config,
}: {
  children: React.ReactNode;
  config: FormConfig;
}) {
  const [state, dispatch] = useReducer(formReducer, {
    ...initialState,
    fields: Object.entries(config.initialValues || {}).reduce(
      (acc, [name, value]) => ({
        ...acc,
        [name]: {
          name,
          value,
          displayValue: String(value),
          isValid: true,
          isDirty: false,
          isTouched: false,
        },
      }),
      {}
    ),
  });

  const fieldConfigs = React.useRef<Record<string, FormFieldConfig<any>>>({});

  const registerField = useCallback(<T,>(name: string, config: FormFieldConfig<T>) => {
    fieldConfigs.current[name] = config;
  }, []);

  const unregisterField = useCallback((name: string) => {
    delete fieldConfigs.current[name];
  }, []);

  const getFieldValue = useCallback(<T,>(name: string): T | undefined => {
    return state.fields[name]?.value;
  }, [state.fields]);

  const setFieldValue = useCallback(<T,>(name: string, value: T) => {
    const config = fieldConfigs.current[name];
    if (!config) return;

    const field: FormField<T> = {
      name,
      value,
      displayValue: String(value),
      isValid: true,
      isDirty: true,
      isTouched: true,
    };

    // Validate the field
    if (config.schema) {
      try {
        config.schema.parse(value);
      } catch (error) {
        if (error instanceof z.ZodError) {
          field.isValid = false;
          field.error = error.errors[0].message;
        }
      }
    }

    if (config.validation) {
      for (const validator of config.validation) {
        if (!validator.validate(value)) {
          field.isValid = false;
          field.error = validator.message;
          break;
        }
      }
    }

    dispatch({ type: "SET_FIELD", payload: { name, field } });
  }, []);

  const validateField = useCallback((name: string): boolean => {
    const field = state.fields[name];
    const config = fieldConfigs.current[name];
    if (!field || !config) return true;

    const value = field.value;
    let isValid = true;
    let error: string | undefined;

    if (config.schema) {
      try {
        config.schema.parse(value);
      } catch (e) {
        if (e instanceof z.ZodError) {
          isValid = false;
          error = e.errors[0].message;
        }
      }
    }

    if (isValid && config.validation) {
      for (const validator of config.validation) {
        if (!validator.validate(value)) {
          isValid = false;
          error = validator.message;
          break;
        }
      }
    }

    dispatch({
      type: "SET_FIELD",
      payload: {
        name,
        field: { ...field, isValid, error },
      },
    });

    return isValid;
  }, [state.fields]);

  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;

    Object.keys(state.fields).forEach((name) => {
      if (!validateField(name)) {
        isValid = false;
        errors[name] = state.fields[name].error || "Invalid field";
      }
    });

    dispatch({ type: "SET_ERRORS", payload: errors });
    return isValid;
  }, [state.fields, validateField]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      dispatch({ type: "INCREMENT_SUBMIT" });

      if (!validateForm()) {
        config.onError?.(state.errors);
        return;
      }

      dispatch({ type: "SET_SUBMITTING", payload: true });

      try {
        const values = Object.entries(state.fields).reduce(
          (acc, [name, field]) => ({
            ...acc,
            [name]: field.value,
          }),
          {}
        );

        await config.onSubmit?.(values);
      } catch (error) {
        console.error("Form submission error:", error);
      } finally {
        dispatch({ type: "SET_SUBMITTING", payload: false });
      }
    },
    [config, state.errors, state.fields, validateForm]
  );

  const reset = useCallback(() => {
    dispatch({
      type: "RESET_FORM",
      payload: {
        fields: Object.entries(config.initialValues || {}).reduce(
          (acc, [name, value]) => ({
            ...acc,
            [name]: {
              name,
              value,
              displayValue: String(value),
              isValid: true,
              isDirty: false,
              isTouched: false,
            },
          }),
          {}
        ),
      },
    });
  }, [config.initialValues]);

  return (
    <FormContext.Provider
      value={{
        state,
        dispatch,
        registerField,
        unregisterField,
        getFieldValue,
        setFieldValue,
        validateField,
        validateForm,
        handleSubmit,
        reset,
      }}
    >
      {children}
    </FormContext.Provider>
  );
}

export function useForm() {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error("useForm must be used within a FormProvider");
  }
  return context;
}
