import { injectable } from 'inversify';
import { ValidationError } from '../errors';

@injectable()
export class DateUtil {
  private readonly ISO8601_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:?\d{2})?$/;
  private readonly DATE_FORMATS = {
    ISO: 'ISO',
    RFC2822: 'RFC2822',
    UNIX: 'UNIX'
  } as const;

  parseDate(value: string | number | Date): Date {
    if (value instanceof Date) {
      if (isNaN(value.getTime())) {
        throw new ValidationError('Invalid Date object');
      }
      return value;
    }

    if (typeof value === 'number') {
      const date = new Date(value);
      if (isNaN(date.getTime())) {
        throw new ValidationError('Invalid timestamp');
      }
      return date;
    }

    // Try ISO 8601
    if (this.ISO8601_REGEX.test(value)) {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        return date;
      }
    }

    // Try RFC 2822
    const rfc2822Date = new Date(value);
    if (!isNaN(rfc2822Date.getTime())) {
      return rfc2822Date;
    }

    throw new ValidationError('Invalid date format');
  }

  format(date: Date, format: keyof typeof DateUtil.prototype.DATE_FORMATS = 'ISO'): string {
    if (!(date instanceof Date) || isNaN(date.getTime())) {
      throw new ValidationError('Invalid Date object');
    }

    switch (format) {
      case 'ISO':
        return date.toISOString();
      case 'RFC2822':
        return date.toUTCString();
      case 'UNIX':
        return Math.floor(date.getTime() / 1000).toString();
      default:
        throw new ValidationError(`Unsupported date format: ${format}`);
    }
  }

  addDays(date: Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  addMonths(date: Date, months: number): Date {
    const result = new Date(date);
    result.setMonth(result.getMonth() + months);
    return result;
  }

  addYears(date: Date, years: number): Date {
    const result = new Date(date);
    result.setFullYear(result.getFullYear() + years);
    return result;
  }

  startOfDay(date: Date): Date {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
  }

  endOfDay(date: Date): Date {
    const result = new Date(date);
    result.setHours(23, 59, 59, 999);
    return result;
  }

  startOfMonth(date: Date): Date {
    const result = new Date(date);
    result.setDate(1);
    result.setHours(0, 0, 0, 0);
    return result;
  }

  endOfMonth(date: Date): Date {
    const result = new Date(date);
    result.setMonth(result.getMonth() + 1, 0);
    result.setHours(23, 59, 59, 999);
    return result;
  }

  isSameDay(date1: Date, date2: Date): boolean {
    return (
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate()
    );
  }

  isBefore(date1: Date, date2: Date): boolean {
    return date1.getTime() < date2.getTime();
  }

  isAfter(date1: Date, date2: Date): boolean {
    return date1.getTime() > date2.getTime();
  }

  isBetween(date: Date, start: Date, end: Date, inclusive = true): boolean {
    const timestamp = date.getTime();
    return inclusive
      ? timestamp >= start.getTime() && timestamp <= end.getTime()
      : timestamp > start.getTime() && timestamp < end.getTime();
  }

  diffInDays(date1: Date, date2: Date): number {
    const utc1 = Date.UTC(
      date1.getFullYear(),
      date1.getMonth(),
      date1.getDate()
    );
    const utc2 = Date.UTC(
      date2.getFullYear(),
      date2.getMonth(),
      date2.getDate()
    );
    return Math.floor((utc2 - utc1) / (1000 * 60 * 60 * 24));
  }

  diffInMonths(date1: Date, date2: Date): number {
    return (
      (date2.getFullYear() - date1.getFullYear()) * 12 +
      (date2.getMonth() - date1.getMonth())
    );
  }

  diffInYears(date1: Date, date2: Date): number {
    return date2.getFullYear() - date1.getFullYear();
  }
}
