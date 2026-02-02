# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2026-02-02] - Dependency Updates Review

### Changed

**GitHub Actions**
- Upgraded `actions/cache` from v4 to v5
- Upgraded `actions/setup-node` from v4 to v6

**Backend Dependencies**
- Upgraded `anthropic` from 0.39.0 to 0.77.0 (major API update)
- Upgraded `edge-tts` from 6.1.18 to 7.2.7 (major version update)

**Frontend Dependencies**
- Upgraded `@typescript-eslint/parser` from 8.53.1 to 8.54.0
- Upgraded `@typescript-eslint/eslint-plugin` from 8.53.1 to 8.54.0
- Upgraded `typescript-eslint` from 8.53.1 to 8.54.0
- Upgraded `electron-builder` from 26.6.0 to 26.7.0
- Upgraded `autoprefixer` from 10.4.23 to 10.4.24
- Upgraded `globals` from 17.1.0 to 17.3.0
- Upgraded `eslint-plugin-react-refresh` from 0.4.26 to 0.5.0
- Upgraded `axios` from 1.13.3 to 1.13.4

### Deferred

**React Updates (Testing Issues)**
- React 19.2.3 → 19.2.4 deferred due to test suite failures
- @types/react 19.2.9 → 19.2.10 deferred pending React update

### Notes
- All updates reviewed for breaking changes and security implications
- CI/CD pipeline passing for all merged updates
- Security scanning clean across all dependency updates
- Anthropic API upgrade required review of breaking changes in LLM provider integration
- Edge-TTS major version bump reviewed for TTS service compatibility
