# SRS — Demo Product v1.2.0

## Bug Fixes

**BUG-101** — Application crashes when saving a file with a name longer than 255 characters.
Severity: Major.
FR: FR-12 — File save validation.

**BUG-102** — Login screen accepts blank password on Safari only.
Severity: Critical.
FR: FR-03 — Authentication.

## New Features

**FR-20** — Add dark-mode toggle in user settings.
Description: Users can switch between light and dark themes. Preference persists across sessions.

## Enhancements

**FR-22** — Improve CSV export performance for files over 10,000 rows.
Description: Streaming writer replaces in-memory collection.
