import { Container } from 'inversify';
import { DateUtil } from '../../../../src/core/utils/date.util';
import { ValidationError } from '../../../../src/core/errors';

describe('DateUtil', () => {
  let container: Container;
  let dateUtil: DateUtil;

  beforeEach(() => {
    container = new Container();
    container.bind(DateUtil).toSelf();
    dateUtil = container.get(DateUtil);
  });

  describe('parseDate', () => {
    it('should parse ISO 8601 date string', () => {
      const isoString = '2025-01-12T15:47:58-06:00';
      const result = dateUtil.parseDate(isoString);
      expect(result).toBeInstanceOf(Date);
      expect(result.toISOString()).toBe(new Date(isoString).toISOString());
    });

    it('should parse RFC 2822 date string', () => {
      const rfcString = 'Sun, 12 Jan 2025 15:47:58 -0600';
      const result = dateUtil.parseDate(rfcString);
      expect(result).toBeInstanceOf(Date);
      expect(result.toISOString()).toBe(new Date(rfcString).toISOString());
    });

    it('should parse timestamp number', () => {
      const timestamp = Date.now();
      const result = dateUtil.parseDate(timestamp);
      expect(result).toBeInstanceOf(Date);
      expect(result.getTime()).toBe(timestamp);
    });

    it('should handle Date object', () => {
      const date = new Date();
      const result = dateUtil.parseDate(date);
      expect(result).toBeInstanceOf(Date);
      expect(result.getTime()).toBe(date.getTime());
    });

    it('should throw ValidationError for invalid date string', () => {
      expect(() => dateUtil.parseDate('invalid-date'))
        .toThrow(ValidationError);
    });
  });

  describe('format', () => {
    const testDate = new Date('2025-01-12T15:47:58-06:00');

    it('should format date as ISO string', () => {
      const result = dateUtil.format(testDate, 'ISO');
      expect(result).toBe(testDate.toISOString());
    });

    it('should format date as RFC 2822 string', () => {
      const result = dateUtil.format(testDate, 'RFC2822');
      expect(result).toBe(testDate.toUTCString());
    });

    it('should format date as UNIX timestamp', () => {
      const result = dateUtil.format(testDate, 'UNIX');
      expect(result).toBe(Math.floor(testDate.getTime() / 1000).toString());
    });

    it('should throw ValidationError for invalid date', () => {
      expect(() => dateUtil.format(new Date('invalid')))
        .toThrow(ValidationError);
    });
  });

  describe('date manipulation', () => {
    const testDate = new Date('2025-01-12T15:47:58-06:00');

    it('should add days correctly', () => {
      const result = dateUtil.addDays(testDate, 5);
      expect(result.getDate()).toBe(testDate.getDate() + 5);
    });

    it('should add months correctly', () => {
      const result = dateUtil.addMonths(testDate, 2);
      expect(result.getMonth()).toBe(testDate.getMonth() + 2);
    });

    it('should add years correctly', () => {
      const result = dateUtil.addYears(testDate, 1);
      expect(result.getFullYear()).toBe(testDate.getFullYear() + 1);
    });

    it('should handle month rollover when adding days', () => {
      const endOfMonth = new Date('2025-01-31T15:47:58-06:00');
      const result = dateUtil.addDays(endOfMonth, 1);
      expect(result.getMonth()).toBe(1); // February
      expect(result.getDate()).toBe(1);
    });
  });

  describe('date comparison', () => {
    const date1 = new Date('2025-01-12T15:47:58-06:00');
    const date2 = new Date('2025-01-13T15:47:58-06:00');

    it('should compare dates correctly with isBefore', () => {
      expect(dateUtil.isBefore(date1, date2)).toBe(true);
      expect(dateUtil.isBefore(date2, date1)).toBe(false);
    });

    it('should compare dates correctly with isAfter', () => {
      expect(dateUtil.isAfter(date2, date1)).toBe(true);
      expect(dateUtil.isAfter(date1, date2)).toBe(false);
    });

    it('should check if dates are the same day', () => {
      const sameDay = new Date(date1);
      sameDay.setHours(date1.getHours() + 1);
      expect(dateUtil.isSameDay(date1, sameDay)).toBe(true);
      expect(dateUtil.isSameDay(date1, date2)).toBe(false);
    });

    it('should check if date is between range', () => {
      const middle = new Date('2025-01-12T16:47:58-06:00');
      expect(dateUtil.isBetween(middle, date1, date2)).toBe(true);
      expect(dateUtil.isBetween(date1, middle, date2)).toBe(false);
    });
  });

  describe('date differences', () => {
    const start = new Date('2025-01-12T15:47:58-06:00');
    const end = new Date('2026-03-15T15:47:58-06:00');

    it('should calculate difference in days', () => {
      const days = dateUtil.diffInDays(start, end);
      expect(days).toBe(427); // Actual difference in days
    });

    it('should calculate difference in months', () => {
      const months = dateUtil.diffInMonths(start, end);
      expect(months).toBe(14); // Jan 2025 to Mar 2026
    });

    it('should calculate difference in years', () => {
      const years = dateUtil.diffInYears(start, end);
      expect(years).toBe(1);
    });
  });
});
