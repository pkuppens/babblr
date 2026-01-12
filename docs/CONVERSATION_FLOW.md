# Conversation Flow

This document describes how Babblr handles conversation initialization and the roleplay tutor system.

It is written to stay correct even as the app evolves into a multi-tab learning platform (Home, Vocabulary, Grammar, Conversations, Assessments, Configuration).

## Overview

Babblr supports two conversation modes:
1. **Topic-Based Roleplay**: User selects a topic (e.g., Restaurant) and the AI adopts a character
2. **General Practice**: Free-form conversation with a generic tutor greeting

### Where conversations live in the app

Conversations are a dedicated area (typically the **Conversations** tab) inside a larger app shell.

Key expectation for the platform:
- **Conversation behavior must not change** when tabs/navigation are introduced.
- **Switching tabs must not lose conversation state** (e.g., the selected conversation and its messages remain available).

## Topic-Based Roleplay Flow

When a user selects a topic and clicks a starter phrase:

```
1. User selects language + difficulty (e.g., Spanish A1)
2. User selects topic (e.g., Restaurant)
3. User clicks starter phrase (e.g., "Do you have a table for two?") (3.1) OR a starting context (3.2)
3.1 Conversation starts DIRECTLY with user's message, tutor/roleplayer responds from context
3.2 Roleplaying tutor starts the conversation from the context (e.g. "Do you have a reservation?")
4. AI responds in-character as the roleplay persona (e.g., waiter)
5. Conversation continues naturally in roleplay context - with helpful tutor sidenote/grammar corrections separated.
```

### Key Principles

- **No Generic Greetings**: When a topic is selected, skip the "Soy tu tutor" message
- **User Initiates**: The user's starter phrase is the conversation opener
- **AI Stays In-Character**: The AI responds AS the character, not as a tutor
- **Corrections as Side Notes**: Grammar corrections appear separately, not interrupting flow
- **Context Persistence**: The roleplay context persists throughout the conversation

### Data Flow

```
TopicSelector
    |
    v
ConversationStarters (user clicks starter phrase)
    |
    v
Frontend conversation controller (e.g., Conversations screen): handleTopicStarterSelected(topic, starter)
    |
    v
+----------------------------------------------------+
| 1. conversationService.create(lang, level, topic.id) |
| 2. chatService.sendMessage(..., topic.id)            |
+----------------------------------------------------+
    |
    v
Backend: chat.py
- Looks up topic by topic_id
- Extracts roleplayContext for language
- Passes to conversation_service
    |
    v
ConversationService.generate_response(topic_context=...)
- System prompt includes: "Eres un camarero amable..."
- AI generates in-character response
    |
    v
Response saved to database
    |
    v
Frontend: ConversationInterface
- topic_id exists -> NO virtual starterMessage
- Loads messages from API
- Displays conversation naturally
```

## General Practice Flow

When no topic is selected (direct conversation start):

```
1. User selects language + difficulty
2. Conversation starts with generic tutor greeting
3. User responds to greeting
4. Standard tutoring conversation
```

The generic greeting is language and level-appropriate (defined in `starterMessages.ts`).

### Important note about persistence

The generic tutor greeting is a **UI-only starter** shown when there are no stored messages yet and the conversation has **no** `topic_id`.

This keeps the database clean (messages are only stored once the user actually sends a message), while still giving beginners a friendly start.

## Roleplay Context Structure

Each topic in `backend/app/static/topics.json` defines roleplay context per language:

```json
{
  "id": "restaurant",
  "roleplayContext": {
    "spanish": "Eres un camarero amable en un restaurante. El estudiante es un cliente que quiere pedir comida. Responde de forma natural y mantenga la conversacion fluida.",
    "italian": "Sei un cameriere gentile in un ristorante. Lo studente e un cliente che vuole ordinare. Rispondi in modo naturale e mantieni la conversazione fluida."
  }
}
```

The roleplay context:
- Defines the AI's character/role
- Sets the scenario
- Instructs the AI to keep conversation flowing naturally

## Adding New Topics

To add a new topic with roleplay support:

1. Add topic entry to `backend/app/static/topics.json`:
   ```json
   {
     "id": "my-topic",
     "icon": "emoji",
     "level": "A1",
     "names": { "spanish": "Mi Tema", ... },
     "descriptions": { "spanish": "Descripcion...", ... },
     "starters": { "spanish": ["Frase 1", "Frase 2"], ... },
     "startersEnglish": ["Phrase 1", "Phrase 2"],
     "roleplayContext": {
       "spanish": "Eres un [personaje]. El estudiante es [su rol]. [Instrucciones adicionales].",
       ...
     }
   }
   ```

2. Ensure each language has a corresponding roleplayContext entry

3. The starters should be natural conversation openers for the roleplay scenario

### Optional: starter translations and localization

As the product grows, we may want to show starter translations in the user's UI language.
If/when we add this, prefer stable localization keys (e.g., `i18nKey`) over hardcoded English strings.

`startersEnglish` is a pragmatic placeholder some datasets may use, but it should not become the long-term localization strategy.

## Frontend Implementation Details

The logic in `ConversationInterface.tsx` handles both modes:

```typescript
// Message display
{messages.length === 0 && !conversation.topic_id ? (
  // No topic: show generic tutor greeting
  <MessageBubble message={starterMessage} ... />
) : messages.length === 0 ? (
  // Topic selected but messages loading: show loading indicator
  <LoadingIndicator />
) : (
  // Normal: show all messages from database
  messages.map(message => <MessageBubble ... />)
)}
```

## Platform alignment (tabs, lessons, assessments)

Conversations are one learning mode among others (Vocabulary, Grammar, Assessments). The platform should treat the following as shared primitives:

- **Selected language**: chosen by the user and reused across modules.
- **Selected CEFR level**: chosen by the user as a starting point; assessments may recommend a change and the user can confirm updating their default level.
- **Persisted conversation identity**: conversations are stored and can be resumed; tab switching must not reset the current conversation selection.

This document intentionally avoids prescribing a specific state management library. It only defines the behavioral invariants that UI and API must preserve.

## Related Files

- `backend/app/static/topics.json` - Topic definitions with roleplay contexts
- `backend/app/routes/chat.py` - Chat endpoint, topic lookup, context injection
- `backend/app/services/conversation_service.py` - Prompt building with topic context
- `frontend/src/components/ConversationInterface.tsx` - Message rendering logic
- `frontend/src/utils/starterMessages.ts` - Generic tutor greetings
