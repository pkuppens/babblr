# Testing Guide

This directory contains the testing infrastructure and test files for the Babblr frontend.

## Test Setup

The test setup is configured in `setup.ts`, which:
- Configures Testing Library DOM matchers
- Mocks browser APIs (localStorage, console, clipboard, etc.)
- Sets up global test utilities

## BDD Naming Convention

We follow Behavior-Driven Development (BDD) naming conventions for test descriptions:

### Structure

```typescript
describe('ComponentName or FeatureName', () => {
  describe('when a specific condition or state exists', () => {
    it('should perform the expected behavior', () => {
      // test implementation
    });
  });
});
```

### Guidelines

1. **Use "should" for test descriptions**: Tests describe what the code should do
   ```typescript
   it('should render the component without errors', () => { ... });
   it('should display error message when API call fails', () => { ... });
   ```

2. **Use "when...should" for context-specific tests**: Group related tests with describe blocks
   ```typescript
   describe('when user is logged in', () => {
     it('should display user profile', () => { ... });
     it('should allow logout', () => { ... });
   });
   ```

3. **Be specific and descriptive**: Test names should clearly describe the expected behavior
   - Good: `it('should disable submit button when form is invalid', ...)`
   - Bad: `it('works', ...)`

4. **Group related tests**: Use nested `describe` blocks to organize tests by feature or state
   ```typescript
   describe('LanguageSelector', () => {
     describe('when no language is selected', () => {
       it('should show language options', () => { ... });
     });
     describe('when a language is selected', () => {
       it('should call onStart callback', () => { ... });
     });
   });
   ```

### Example

```typescript
describe('ErrorBoundary', () => {
  describe('when no error occurs', () => {
    it('should render children normally', () => {
      // test implementation
    });
  });

  describe('when an error is thrown', () => {
    it('should display error message', () => {
      // test implementation
    });

    it('should provide reset button', () => {
      // test implementation
    });
  });
});
```

## Running Tests

- `npm run test` - Run tests once
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage report

## Test Files Location

- Component tests: `src/components/ComponentName.test.tsx`
- Hook tests: `src/hooks/useHookName.test.ts`
- Service tests: `src/services/serviceName.test.ts`
- Utility tests: `src/utils/utilityName.test.ts`

## Fixtures

Test fixtures and mock data are located in `src/test/fixtures/`. See the fixtures README for more details.
