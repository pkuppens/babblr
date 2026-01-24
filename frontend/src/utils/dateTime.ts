/**
 * DateTime utilities with timezone and locale support
 */

// Common timezones grouped by region
export const TIMEZONE_OPTIONS = [
  // UTC
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)', group: 'UTC' },

  // Europe
  { value: 'Europe/Amsterdam', label: 'Amsterdam (CET/CEST)', group: 'Europe' },
  { value: 'Europe/London', label: 'London (GMT/BST)', group: 'Europe' },
  { value: 'Europe/Paris', label: 'Paris (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Berlin', label: 'Berlin (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Madrid', label: 'Madrid (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Rome', label: 'Rome (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Brussels', label: 'Brussels (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Vienna', label: 'Vienna (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Stockholm', label: 'Stockholm (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Oslo', label: 'Oslo (CET/CEST)', group: 'Europe' },
  { value: 'Europe/Helsinki', label: 'Helsinki (EET/EEST)', group: 'Europe' },
  { value: 'Europe/Athens', label: 'Athens (EET/EEST)', group: 'Europe' },
  { value: 'Europe/Moscow', label: 'Moscow (MSK)', group: 'Europe' },

  // Americas
  { value: 'America/New_York', label: 'New York (EST/EDT)', group: 'Americas' },
  { value: 'America/Chicago', label: 'Chicago (CST/CDT)', group: 'Americas' },
  { value: 'America/Denver', label: 'Denver (MST/MDT)', group: 'Americas' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (PST/PDT)', group: 'Americas' },
  { value: 'America/Toronto', label: 'Toronto (EST/EDT)', group: 'Americas' },
  { value: 'America/Vancouver', label: 'Vancouver (PST/PDT)', group: 'Americas' },
  { value: 'America/Mexico_City', label: 'Mexico City (CST/CDT)', group: 'Americas' },
  { value: 'America/Sao_Paulo', label: 'Sao Paulo (BRT)', group: 'Americas' },
  { value: 'America/Buenos_Aires', label: 'Buenos Aires (ART)', group: 'Americas' },

  // Asia
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)', group: 'Asia' },
  { value: 'Asia/Shanghai', label: 'Shanghai (CST)', group: 'Asia' },
  { value: 'Asia/Hong_Kong', label: 'Hong Kong (HKT)', group: 'Asia' },
  { value: 'Asia/Singapore', label: 'Singapore (SGT)', group: 'Asia' },
  { value: 'Asia/Seoul', label: 'Seoul (KST)', group: 'Asia' },
  { value: 'Asia/Mumbai', label: 'Mumbai (IST)', group: 'Asia' },
  { value: 'Asia/Dubai', label: 'Dubai (GST)', group: 'Asia' },
  { value: 'Asia/Bangkok', label: 'Bangkok (ICT)', group: 'Asia' },
  { value: 'Asia/Jakarta', label: 'Jakarta (WIB)', group: 'Asia' },

  // Oceania
  { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)', group: 'Oceania' },
  { value: 'Australia/Melbourne', label: 'Melbourne (AEST/AEDT)', group: 'Oceania' },
  { value: 'Australia/Perth', label: 'Perth (AWST)', group: 'Oceania' },
  { value: 'Pacific/Auckland', label: 'Auckland (NZST/NZDT)', group: 'Oceania' },

  // Africa
  { value: 'Africa/Cairo', label: 'Cairo (EET)', group: 'Africa' },
  { value: 'Africa/Johannesburg', label: 'Johannesburg (SAST)', group: 'Africa' },
  { value: 'Africa/Lagos', label: 'Lagos (WAT)', group: 'Africa' },
];

export type TimeFormat = '24h' | '12h';

export const TIME_FORMAT_OPTIONS: { value: TimeFormat; label: string }[] = [
  { value: '24h', label: '24-hour (14:30)' },
  { value: '12h', label: '12-hour (2:30 PM)' },
];

/**
 * Detect the user's timezone from browser settings
 */
export function detectUserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return 'Europe/Amsterdam'; // Default fallback
  }
}

/**
 * Detect if user prefers 24h or 12h format based on locale
 */
export function detectTimeFormat(): TimeFormat {
  try {
    // Format a sample time and check if it contains AM/PM
    const formatted = new Date(2000, 0, 1, 14, 0).toLocaleTimeString(undefined, {
      hour: 'numeric',
    });
    // If it contains AM, PM, or locale equivalents, it's 12h format
    return /[APap][Mm]/.test(formatted) ? '12h' : '24h';
  } catch {
    return '24h'; // Default to 24h
  }
}

/**
 * Format a date/time string for display
 */
export function formatDateTime(
  dateString: string,
  options: {
    timezone: string;
    timeFormat: TimeFormat;
    includeDate?: boolean;
    includeSeconds?: boolean;
  }
): string {
  const { timezone, timeFormat, includeDate = false, includeSeconds = false } = options;

  try {
    // Ensure the date string is treated as UTC if it doesn't have a timezone indicator
    // Backend returns UTC timestamps (now with Z suffix as of timezone-aware datetimes)
    // But handle both old format (without Z) and new format (with Z) for backwards compatibility
    let normalizedDateString = dateString.trim();

    // Check if already has timezone indicator (Z or +/-HH:MM)
    const hasTimezoneIndicator =
      normalizedDateString.endsWith('Z') || normalizedDateString.match(/[+-]\d{2}:?\d{2}$/);

    // If no timezone indicator, assume UTC and add Z
    if (!hasTimezoneIndicator) {
      // Only add Z if it looks like a valid ISO datetime string
      if (normalizedDateString.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
        normalizedDateString = normalizedDateString + 'Z';
      }
    }

    const date = new Date(normalizedDateString);
    if (isNaN(date.getTime())) {
      return dateString; // Return original if invalid
    }

    const formatOptions: Intl.DateTimeFormatOptions = {
      timeZone: timezone,
      hour: '2-digit',
      minute: '2-digit',
      hour12: timeFormat === '12h',
    };

    if (includeSeconds) {
      formatOptions.second = '2-digit';
    }

    if (includeDate) {
      formatOptions.year = 'numeric';
      formatOptions.month = 'short';
      formatOptions.day = 'numeric';
    }

    // Use a neutral locale for consistent formatting
    const locale = timeFormat === '24h' ? 'en-GB' : 'en-US';
    return date.toLocaleString(locale, formatOptions);
  } catch {
    return dateString; // Return original on error
  }
}

/**
 * Format time only (for message bubbles)
 */
export function formatTime(dateString: string, timezone: string, timeFormat: TimeFormat): string {
  return formatDateTime(dateString, { timezone, timeFormat, includeDate: false });
}

/**
 * Format date and time (for conversation list)
 */
export function formatDateAndTime(
  dateString: string,
  timezone: string,
  timeFormat: TimeFormat
): string {
  return formatDateTime(dateString, { timezone, timeFormat, includeDate: true });
}

/**
 * Get current time in specified timezone
 */
export function getCurrentTime(timezone: string, timeFormat: TimeFormat): string {
  return formatDateTime(new Date().toISOString(), { timezone, timeFormat });
}

/**
 * Filter timezone options by search query
 */
export function filterTimezones(query: string): typeof TIMEZONE_OPTIONS {
  if (!query.trim()) return TIMEZONE_OPTIONS;

  const lowerQuery = query.toLowerCase();
  return TIMEZONE_OPTIONS.filter(
    tz =>
      tz.value.toLowerCase().includes(lowerQuery) ||
      tz.label.toLowerCase().includes(lowerQuery) ||
      tz.group.toLowerCase().includes(lowerQuery)
  );
}
