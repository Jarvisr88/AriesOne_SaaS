import { DataType } from '../enums/data-type.enum';
import { ValidationRule } from '../interfaces/validation-rule.interface';

export class Column {
  name: string;
  description?: string;
  dataType: DataType;
  isRequired: boolean;
  isPrimary: boolean;
  isUnique: boolean;
  defaultValue?: any;
  validationRules: ValidationRule[];
  format?: string;
  precision?: number;
  scale?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;

  constructor(data: Partial<Column>) {
    Object.assign(this, {
      isRequired: false,
      isPrimary: false,
      isUnique: false,
      validationRules: [],
      ...data
    });
  }

  validate(): string[] {
    const errors: string[] = [];

    if (!this.name) {
      errors.push('Column name is required');
    }

    if (!this.dataType) {
      errors.push('Data type is required');
    }

    if (this.precision !== undefined && this.precision < 0) {
      errors.push('Precision must be non-negative');
    }

    if (this.scale !== undefined && this.scale < 0) {
      errors.push('Scale must be non-negative');
    }

    if (this.minLength !== undefined && this.maxLength !== undefined) {
      if (this.minLength > this.maxLength) {
        errors.push('Minimum length cannot be greater than maximum length');
      }
    }

    return errors;
  }

  validateValue(value: any): string[] {
    const errors: string[] = [];

    if (this.isRequired && (value === undefined || value === null)) {
      errors.push(`${this.name} is required`);
      return errors;
    }

    if (value === undefined || value === null) {
      return errors;
    }

    switch (this.dataType) {
      case DataType.TEXT:
        if (typeof value !== 'string') {
          errors.push(`${this.name} must be a string`);
        } else {
          if (this.minLength !== undefined && value.length < this.minLength) {
            errors.push(`${this.name} must be at least ${this.minLength} characters`);
          }
          if (this.maxLength !== undefined && value.length > this.maxLength) {
            errors.push(`${this.name} must be at most ${this.maxLength} characters`);
          }
          if (this.pattern && !new RegExp(this.pattern).test(value)) {
            errors.push(`${this.name} must match pattern ${this.pattern}`);
          }
        }
        break;

      case DataType.NUMBER:
        if (typeof value !== 'number') {
          errors.push(`${this.name} must be a number`);
        } else {
          if (this.precision !== undefined) {
            const parts = value.toString().split('.');
            if (parts[0].length > this.precision - (this.scale || 0)) {
              errors.push(`${this.name} exceeds maximum precision`);
            }
            if (this.scale !== undefined && parts[1] && parts[1].length > this.scale) {
              errors.push(`${this.name} exceeds maximum scale`);
            }
          }
        }
        break;

      case DataType.BOOLEAN:
        if (typeof value !== 'boolean') {
          errors.push(`${this.name} must be a boolean`);
        }
        break;

      case DataType.DATE:
        if (!(value instanceof Date) && isNaN(Date.parse(value))) {
          errors.push(`${this.name} must be a valid date`);
        }
        break;

      case DataType.LOCATION:
        if (!this.validateLocation(value)) {
          errors.push(`${this.name} must be a valid location`);
        }
        break;

      case DataType.PHONE:
        if (!this.validatePhone(value)) {
          errors.push(`${this.name} must be a valid phone number`);
        }
        break;

      case DataType.URL:
        if (!this.validateUrl(value)) {
          errors.push(`${this.name} must be a valid URL`);
        }
        break;
    }

    // Apply custom validation rules
    this.validationRules.forEach(rule => {
      const error = rule.validate(value);
      if (error) {
        errors.push(error);
      }
    });

    return errors;
  }

  private validateLocation(value: any): boolean {
    if (typeof value !== 'object') return false;
    if (!('latitude' in value) || !('longitude' in value)) return false;
    const { latitude, longitude } = value;
    return (
      typeof latitude === 'number' &&
      typeof longitude === 'number' &&
      latitude >= -90 &&
      latitude <= 90 &&
      longitude >= -180 &&
      longitude <= 180
    );
  }

  private validatePhone(value: string): boolean {
    // Basic phone validation - can be enhanced based on requirements
    const phonePattern = /^\+?[\d\s-()]{10,}$/;
    return phonePattern.test(value);
  }

  private validateUrl(value: string): boolean {
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  }

  toJSON(): Record<string, any> {
    return {
      name: this.name,
      description: this.description,
      dataType: this.dataType,
      isRequired: this.isRequired,
      isPrimary: this.isPrimary,
      isUnique: this.isUnique,
      defaultValue: this.defaultValue,
      validationRules: this.validationRules,
      format: this.format,
      precision: this.precision,
      scale: this.scale,
      minLength: this.minLength,
      maxLength: this.maxLength,
      pattern: this.pattern
    };
  }

  update(data: Partial<Column>): void {
    Object.assign(this, data);
  }

  clone(): Column {
    return new Column(this.toJSON());
  }
}
