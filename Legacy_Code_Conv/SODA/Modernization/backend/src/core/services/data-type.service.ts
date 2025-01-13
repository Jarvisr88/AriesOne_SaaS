import { injectable } from 'inversify';
import { DataType } from '../../domain/enums/data-type.enum';
import { ValidationError } from '../errors';

@injectable()
export class DataTypeService {
  validateLocation(value: any): boolean {
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

  validatePhone(value: string): boolean {
    const phonePattern = /^\+?[\d\s-()]{10,}$/;
    return phonePattern.test(value);
  }

  validateUrl(value: string): boolean {
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  }

  formatValue(value: any, dataType: DataType): any {
    if (value === null || value === undefined) {
      return null;
    }

    switch (dataType) {
      case DataType.TEXT:
      case DataType.URL:
      case DataType.PHONE:
        return String(value);

      case DataType.NUMBER:
        const num = Number(value);
        if (isNaN(num)) {
          throw new ValidationError('Invalid number format');
        }
        return num;

      case DataType.BOOLEAN:
        if (typeof value === 'string') {
          const lower = value.toLowerCase();
          if (['true', '1', 'yes'].includes(lower)) return true;
          if (['false', '0', 'no'].includes(lower)) return false;
        }
        return Boolean(value);

      case DataType.DATE:
        const date = new Date(value);
        if (isNaN(date.getTime())) {
          throw new ValidationError('Invalid date format');
        }
        return date;

      case DataType.LOCATION:
        if (!this.validateLocation(value)) {
          throw new ValidationError('Invalid location format');
        }
        return value;

      case DataType.JSON:
        if (typeof value === 'string') {
          try {
            return JSON.parse(value);
          } catch {
            throw new ValidationError('Invalid JSON format');
          }
        }
        return value;

      default:
        return value;
    }
  }

  parseLocation(input: string): { latitude: number; longitude: number } {
    // Parse WKT format: 'POINT(longitude latitude)'
    const match = input.match(/POINT\s*\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s*\)/i);
    if (!match) {
      throw new ValidationError('Invalid location format. Expected: POINT(longitude latitude)');
    }

    const [, longitude, latitude] = match;
    const lat = Number(latitude);
    const lon = Number(longitude);

    if (lat < -90 || lat > 90) {
      throw new ValidationError('Latitude must be between -90 and 90');
    }

    if (lon < -180 || lon > 180) {
      throw new ValidationError('Longitude must be between -180 and 180');
    }

    return { latitude: lat, longitude: lon };
  }

  formatLocation(location: { latitude: number; longitude: number }): string {
    return `POINT(${location.longitude} ${location.latitude})`;
  }

  parsePhone(input: string): string {
    // Remove all non-digit characters except + for country code
    const cleaned = input.replace(/[^\d+]/g, '');
    if (!this.validatePhone(cleaned)) {
      throw new ValidationError('Invalid phone number format');
    }
    return cleaned;
  }

  formatPhone(phone: string): string {
    // Format: +X (XXX) XXX-XXXX
    const cleaned = this.parsePhone(phone);
    const hasCountryCode = cleaned.startsWith('+');
    const digits = hasCountryCode ? cleaned.slice(1) : cleaned;

    if (digits.length === 10) {
      return hasCountryCode
        ? `+1 (${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
        : `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }

    // Handle international numbers
    const countryCode = hasCountryCode ? cleaned.slice(0, cleaned.length - 10) : '+1';
    const national = cleaned.slice(-10);
    return `${countryCode} (${national.slice(0, 3)}) ${national.slice(3, 6)}-${national.slice(6)}`;
  }

  parseUrl(input: string): string {
    try {
      const url = new URL(input);
      return url.toString();
    } catch {
      throw new ValidationError('Invalid URL format');
    }
  }

  formatUrl(url: string): string {
    return this.parseUrl(url);
  }

  getDefaultValue(dataType: DataType): any {
    switch (dataType) {
      case DataType.TEXT:
      case DataType.URL:
      case DataType.PHONE:
        return '';
      case DataType.NUMBER:
        return 0;
      case DataType.BOOLEAN:
        return false;
      case DataType.DATE:
        return new Date();
      case DataType.LOCATION:
        return { latitude: 0, longitude: 0 };
      case DataType.JSON:
        return {};
      default:
        return null;
    }
  }

  getSampleValue(dataType: DataType): any {
    switch (dataType) {
      case DataType.TEXT:
        return 'Sample Text';
      case DataType.NUMBER:
        return 42;
      case DataType.BOOLEAN:
        return true;
      case DataType.DATE:
        return new Date();
      case DataType.LOCATION:
        return { latitude: 37.7749, longitude: -122.4194 };
      case DataType.PHONE:
        return '+1 (555) 123-4567';
      case DataType.URL:
        return 'https://example.com';
      case DataType.JSON:
        return { key: 'value' };
      default:
        return null;
    }
  }
}
