import { describe, it, expect } from 'vitest';
import { formatDateTime, formatTime, formatDateAndTime } from './dateTime';
import type { TimeFormat } from '../services/settings';

describe('dateTime utilities', () => {
  describe('formatDateTime with UTC timestamps', () => {
    it('should handle ISO string with Z suffix (timezone-aware)', () => {
      const utcTimestamp = '2026-01-22T13:03:00Z';
      const result = formatDateTime(utcTimestamp, {
        timezone: 'Europe/Amsterdam',
        timeFormat: '24h',
        includeDate: true,
      });

      expect(result).toBeDefined();
      // Amsterdam is UTC+1 in January, so 13:03 UTC becomes 14:03 Amsterdam
      expect(result).toContain('14:03');
      expect(result).toContain('22');
    });

    it('should handle ISO string without Z suffix (old format)', () => {
      const naiveTimestamp = '2026-01-22T13:03:00';
      const result = formatDateTime(naiveTimestamp, {
        timezone: 'Europe/Amsterdam',
        timeFormat: '24h',
        includeDate: true,
      });

      expect(result).toBeDefined();
      // Frontend assumes missing Z means UTC, so same result
      expect(result).toContain('14:03');
      expect(result).toContain('22');
    });

    it('should handle ISO string with +00:00 offset (explicit UTC)', () => {
      const explicitUtc = '2026-01-22T13:03:00+00:00';
      const result = formatDateTime(explicitUtc, {
        timezone: 'Europe/Amsterdam',
        timeFormat: '24h',
        includeDate: true,
      });

      expect(result).toBeDefined();
      expect(result).toContain('14:03');
      expect(result).toContain('22');
    });

    it('should apply timezone conversion correctly', () => {
      const utcTimestamp = '2026-01-22T12:00:00Z';

      // UTC timezone
      const utcResult = formatDateTime(utcTimestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      expect(utcResult).toContain('12:00');

      // Amsterdam (+1 in January)
      const amstResult = formatDateTime(utcTimestamp, {
        timezone: 'Europe/Amsterdam',
        timeFormat: '24h',
      });
      expect(amstResult).toContain('13:00');

      // New York (-5 in January)
      const nyResult = formatDateTime(utcTimestamp, {
        timezone: 'America/New_York',
        timeFormat: '24h',
      });
      expect(nyResult).toContain('07:00');
    });

    it('should format time in 24-hour format', () => {
      const timestamp = '2026-01-22T14:03:00Z';
      const result = formatDateTime(timestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      expect(result).toContain('14:03');
    });

    it('should format time in 12-hour format', () => {
      const timestamp = '2026-01-22T14:03:00Z';
      const result = formatDateTime(timestamp, {
        timezone: 'UTC',
        timeFormat: '12h',
      });
      // Should be 2:03 PM
      expect(result).toMatch(/2:03|02:03/);
    });

    it('should include seconds when requested', () => {
      const timestamp = '2026-01-22T13:03:45Z';
      const result = formatDateTime(timestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
        includeSeconds: true,
      });
      expect(result).toContain('45');
    });

    it('should include date when requested', () => {
      const timestamp = '2026-01-22T13:03:00Z';
      const result = formatDateTime(timestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
        includeDate: true,
      });
      expect(result).toContain('22');
      expect(result).toContain('Jan');
    });

    it('should handle timestamps with whitespace', () => {
      const timestamp = '  2026-01-22T13:03:00Z  ';
      const result = formatDateTime(timestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      expect(result).toContain('13:03');
    });

    it('should return original string if datetime is invalid', () => {
      const invalidTimestamp = 'not-a-date';
      const result = formatDateTime(invalidTimestamp, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      expect(result).toBe(invalidTimestamp);
    });
  });

  describe('formatTime wrapper', () => {
    it('should format time without date', () => {
      const timestamp = '2026-01-22T13:03:00Z';
      const result = formatTime(timestamp, 'UTC', '24h');
      expect(result).toContain('13:03');
      expect(result).not.toContain('22');
      expect(result).not.toContain('Jan');
    });
  });

  describe('formatDateAndTime wrapper', () => {
    it('should format date and time together', () => {
      const timestamp = '2026-01-22T13:03:00Z';
      const result = formatDateAndTime(timestamp, 'UTC', '24h');
      expect(result).toContain('13:03');
      expect(result).toContain('22');
    });
  });

  describe('timezone conversion accuracy', () => {
    it('should correctly convert UTC to European timezones', () => {
      const midnightUtc = '2026-01-22T00:00:00Z';

      // Amsterdam is UTC+1 in January
      const amstResult = formatDateTime(midnightUtc, {
        timezone: 'Europe/Amsterdam',
        timeFormat: '24h',
      });
      expect(amstResult).toContain('01:00'); // Should be 1am

      // London is UTC in January (GMT, no DST)
      const lonResult = formatDateTime(midnightUtc, {
        timezone: 'Europe/London',
        timeFormat: '24h',
      });
      expect(lonResult).toContain('00:00'); // Should be midnight
    });

    it('should correctly convert UTC to Asian timezones', () => {
      const noonUtc = '2026-01-22T12:00:00Z';

      // Tokyo is UTC+9 year-round
      const tokyoResult = formatDateTime(noonUtc, {
        timezone: 'Asia/Tokyo',
        timeFormat: '24h',
      });
      expect(tokyoResult).toContain('21:00'); // Should be 9pm

      // Bangkok is UTC+7 year-round
      const bkkResult = formatDateTime(noonUtc, {
        timezone: 'Asia/Bangkok',
        timeFormat: '24h',
      });
      expect(bkkResult).toContain('19:00'); // Should be 7pm
    });

    it('should correctly convert UTC to American timezones', () => {
      const noonUtc = '2026-01-22T12:00:00Z';

      // New York is UTC-5 in January
      const nyResult = formatDateTime(noonUtc, {
        timezone: 'America/New_York',
        timeFormat: '24h',
      });
      expect(nyResult).toContain('07:00'); // Should be 7am

      // Los Angeles is UTC-8 in January
      const laResult = formatDateTime(noonUtc, {
        timezone: 'America/Los_Angeles',
        timeFormat: '24h',
      });
      expect(laResult).toContain('04:00'); // Should be 4am
    });
  });

  describe('backwards compatibility with old format', () => {
    it('should handle backend datetime without Z suffix', () => {
      // Old backend format (naive datetime)
      const oldFormat = '2026-01-22T13:03:00';
      const result = formatDateTime(oldFormat, {
        timezone: 'UTC',
        timeFormat: '24h',
      });

      // Should still work (frontend adds Z internally)
      expect(result).toContain('13:03');
    });

    it('should normalize datetime format consistency', () => {
      // All these should produce the same result
      const withZ = '2026-01-22T13:03:00Z';
      const withoutZ = '2026-01-22T13:03:00';
      const withOffset = '2026-01-22T13:03:00+00:00';

      const resultZ = formatDateTime(withZ, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      const resultNoZ = formatDateTime(withoutZ, {
        timezone: 'UTC',
        timeFormat: '24h',
      });
      const resultOffset = formatDateTime(withOffset, {
        timezone: 'UTC',
        timeFormat: '24h',
      });

      // All should produce times that match 13:03
      expect(resultZ).toContain('13:03');
      expect(resultNoZ).toContain('13:03');
      expect(resultOffset).toContain('13:03');
    });
  });
});
