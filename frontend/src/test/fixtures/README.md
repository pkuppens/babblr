# Test Fixtures

This directory contains test fixtures and mock data for use in tests.

## Purpose

Fixtures help keep tests maintainable by:
- Centralizing test data
- Making tests more readable
- Enabling reuse across multiple test files
- Making it easier to update test data when the data model changes

## Usage

Import fixtures in your test files:

```typescript
import { mockConversation, mockLanguage } from '../fixtures/conversationFixtures';

describe('ConversationComponent', () => {
  it('should render conversation data', () => {
    render(<ConversationComponent conversation={mockConversation} />);
    // ...
  });
});
```

## Organization

Organize fixtures by domain or feature:
- `conversationFixtures.ts` - Conversation-related test data
- `languageFixtures.ts` - Language and difficulty level data
- `messageFixtures.ts` - Message and chat data
- `settingsFixtures.ts` - Settings and configuration data
