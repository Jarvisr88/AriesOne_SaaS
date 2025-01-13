/**
 * Form types.
 * 
 * This module defines TypeScript types for forms.
 */

/**
 * Base form interface.
 */
export interface FormBase {
  name: string;
  description?: string;
  schema: Record<string, any>;
}

/**
 * Form creation data.
 */
export type FormCreate = FormBase;

/**
 * Form update data.
 */
export interface FormUpdate extends Partial<FormBase> {
  is_active?: boolean;
}

/**
 * Form response data.
 */
export interface Form extends FormBase {
  id: number;
  created_by: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Form submission data.
 */
export interface FormSubmission {
  id?: number;
  form_id: number;
  company_id: number;
  data: Record<string, any>;
  submitted_by?: number;
  submitted_at?: string;
}

/**
 * Form field type.
 */
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'date' | 'checkbox';
  required?: boolean;
  options?: string[];
  defaultValue?: any;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}

/**
 * Form schema type.
 */
export interface FormSchema {
  fields: FormField[];
  layout?: {
    columns?: number;
    sections?: {
      title: string;
      fields: string[];
    }[];
  };
  validation?: {
    dependencies?: Record<string, {
      field: string;
      value: any;
      action: 'show' | 'hide' | 'require';
    }>;
    custom?: Record<string, {
      condition: string;
      message: string;
    }>;
  };
}
