import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { DmercFormType } from '../enums/dmerc-form-type.enum';

/**
 * Represents a field in a DMERC form
 */
export interface DmercField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'boolean' | 'select';
  required: boolean;
  options?: string[];
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
  };
  defaultValue?: any;
  helpText?: string;
}

/**
 * Represents a DMERC form template with its fields and validation rules
 */
@Entity('dmerc_forms')
export class DmercForm {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({
    type: 'enum',
    enum: DmercFormType,
    nullable: false
  })
  type: DmercFormType;

  @Column({ length: 10, nullable: false })
  version: string;

  @Column({ type: 'timestamp', nullable: false })
  validFrom: Date;

  @Column({ type: 'timestamp', nullable: true })
  validTo?: Date;

  @Column({ type: 'jsonb', nullable: false })
  fields: DmercField[];

  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, any>;

  @Column({ default: true })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  /**
   * Validates if the form is currently valid based on its validity period
   */
  isValid(): boolean {
    const now = new Date();
    return (
      now >= this.validFrom && 
      (!this.validTo || now <= this.validTo) &&
      this.isActive
    );
  }

  /**
   * Validates form data against the form's field definitions
   * @param data Form data to validate
   * @returns Array of validation errors, empty if valid
   */
  validateData(data: Record<string, any>): string[] {
    const errors: string[] = [];

    for (const field of this.fields) {
      const value = data[field.name];

      // Check required fields
      if (field.required && (value === undefined || value === null || value === '')) {
        errors.push(`${field.label} is required`);
        continue;
      }

      // Skip validation for optional empty fields
      if (!field.required && (value === undefined || value === null || value === '')) {
        continue;
      }

      // Validate based on field type
      switch (field.type) {
        case 'text':
          if (field.validation?.pattern) {
            const regex = new RegExp(field.validation.pattern);
            if (!regex.test(value)) {
              errors.push(`${field.label} does not match required format`);
            }
          }
          if (field.validation?.minLength && value.length < field.validation.minLength) {
            errors.push(`${field.label} must be at least ${field.validation.minLength} characters`);
          }
          if (field.validation?.maxLength && value.length > field.validation.maxLength) {
            errors.push(`${field.label} must be at most ${field.validation.maxLength} characters`);
          }
          break;

        case 'number':
          const num = Number(value);
          if (isNaN(num)) {
            errors.push(`${field.label} must be a number`);
          } else {
            if (field.validation?.min !== undefined && num < field.validation.min) {
              errors.push(`${field.label} must be at least ${field.validation.min}`);
            }
            if (field.validation?.max !== undefined && num > field.validation.max) {
              errors.push(`${field.label} must be at most ${field.validation.max}`);
            }
          }
          break;

        case 'date':
          const date = new Date(value);
          if (isNaN(date.getTime())) {
            errors.push(`${field.label} must be a valid date`);
          }
          break;

        case 'boolean':
          if (typeof value !== 'boolean') {
            errors.push(`${field.label} must be a boolean`);
          }
          break;

        case 'select':
          if (field.options && !field.options.includes(value)) {
            errors.push(`${field.label} must be one of: ${field.options.join(', ')}`);
          }
          break;
      }
    }

    return errors;
  }

  /**
   * Creates a new instance of a form with default values
   */
  static createEmpty(type: DmercFormType): DmercForm {
    const form = new DmercForm();
    form.type = type;
    form.version = '1.0.0';
    form.validFrom = new Date();
    form.fields = [];
    form.metadata = {};
    form.isActive = true;
    return form;
  }
}
