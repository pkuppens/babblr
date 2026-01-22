# ADR-0001: Timezone Handling Strategy

## Status

**Accepted** - Implemented and validated with comprehensive tests.

## Problem

Timestamps displayed with 1-hour offset (e.g., showing 13:03 when actual time is 12:09) due to naive UTC datetimes being stored and interpreted inconsistently across backend/frontend.

## Decision

**UTC storage with timezone-aware display**: Store all timestamps as timezone-aware UTC, serialize with ISO 8601 `Z` suffix, convert to user timezone only on frontend for display.

## Implementation

| Layer | Approach |
|-------|----------|
| **Backend Storage** | `datetime.now(timezone.utc)` - timezone-aware UTC |
| **API Serialization** | ISO 8601 with `Z` suffix (e.g., `2026-01-22T13:03:00Z`) |
| **Frontend Display** | Convert UTC to user timezone using `Intl.DateTimeFormat` |
| **Database Migration** | Verify schema, no data migration needed (existing data already correct) |

## Code References

- Backend: `backend/app/models/models.py` (all `created_at`, `updated_at` columns)
- Frontend: `frontend/src/utils/dateTime.ts` (formatDateTime function)
- Tests: `backend/tests/test_timezone_handling.py`, `frontend/src/utils/dateTime.test.ts`
- Migration: `backend/app/database/db.py` (_migrate_ensure_timezone_aware_datetimes)

## Testing

✓ Backend: Timezone-aware UTC datetime creation and serialization
✓ Frontend: Timezone conversion for multiple zones and DST transitions
✓ Round-trip: UTC serialization → frontend parsing → timezone conversion

## Consequences

**Positive**: Single source of truth (UTC), no conversion errors, automatic DST handling
**Negative**: Frontend must handle timezone display logic, historical data unchanged if already UTC
