# Section 5-6: Frontend and E2E Manual Test Procedures

## Overview

This document contains detailed, step-by-step manual test procedures for:
- **Section 5:** Frontend UI Validation
- **Section 6:** End-to-End Conversation Testing

Each test includes:
- Detailed setup steps
- Specific actions to perform
- **Explicit expected results** (not just "works")
- Success criteria
- Screenshots/indicators to look for

---

## Prerequisites

- Backend running at `http://localhost:8000`
- Frontend running at `http://localhost:3000` or `http://localhost:5173`
- Ollama running (or other LLM provider configured)
- Modern browser (Chrome/Firefox/Edge)

---

## Section 5: Frontend UI Validation

### Test 5.1: Home Screen - Language Selection

**Objective:** Verify language selection works correctly and persists in the UI

**Steps:**
1. Open the frontend application
2. Navigate to the **Home** screen (tab at bottom)
3. Locate the **Language Selector** dropdown (typically labeled "Select Language" or has flag icon)
4. Click on the language selector
5. Select **"Spanish"** from the dropdown

**Expected Results:**
- ✓ Dropdown opens and shows all 6 languages: Spanish, Italian, German, French, Dutch, English
- ✓ Spanish is highlighted when selected
- ✓ Language selector now displays "Spanish" (or Spanish flag icon)
- ✓ Any subsequent text on the home screen reflects Spanish labels/placeholders
- ✓ Selected language persists when navigating to other tabs and back

**Success Criteria:**
- Language change is immediately reflected in UI
- No error messages appear
- Selection is consistent across page reloads

---

### Test 5.2: Home Screen - CEFR Level Selection

**Objective:** Verify CEFR proficiency level selection works correctly

**Steps:**
1. From Home screen with Spanish selected
2. Locate the **CEFR Level Selector** (typically shows "Beginner", "A1", "B2", etc.)
3. Click on the CEFR level selector
4. Select **"A1"** (absolute beginner)

**Expected Results:**
- ✓ Dropdown opens showing all levels: A1, A2, B1, B2, C1, C2
- ✓ A1 is now highlighted/selected
- ✓ UI displays "A1" or "Beginner" in the level selector
- ✓ Description updates to show what A1 means (if applicable)
- ✓ Selected level persists when navigating away and back

**Success Criteria:**
- Level is properly stored
- No validation errors
- Level persists across navigation

**Test 5.3 (Variation):** Select **"B2"** (upper intermediate)
- Same expected results but with B2 level
- Description should indicate intermediate-advanced level

---

### Test 5.3: Home Screen - Topic Selection

**Objective:** Verify topic selection displays correct topics and descriptions

**Steps:**
1. From Home screen with Spanish (A1) selected
2. Locate the **Topic Selector** section (list of conversation topics)
3. Topics should display as cards/buttons with titles and descriptions
4. Click on the **"Greetings"** or **"Introductions"** topic

**Expected Results:**
- ✓ Topic list displays 5+ different topics
- ✓ Each topic shows:
  - Title in Spanish (since Spanish is selected)
  - Description in Spanish
  - Icon or visual indicator
- ✓ Topic title and description change language if you switch languages
- ✓ Selected topic is highlighted/indicated visually
- ✓ "Start Conversation" button becomes active/enabled

**Success Criteria:**
- Topic names appear in the selected language
- Descriptions are grammatically correct
- Visual feedback shows which topic is selected

---

### Test 5.4: Home Screen - Start Conversation Flow

**Objective:** Verify conversation can be started from Home screen

**Steps:**
1. From Home screen with:
   - Language: Spanish
   - Level: A1
   - Topic: Greetings
2. Click the **"Start Conversation"** or **"Begin"** button
3. Wait for page transition (should take 2-5 seconds)

**Expected Results:**
- ✓ Button shows loading state (spinner or "Loading..." text)
- ✓ No error messages appear
- ✓ Page transitions to **Conversation Screen** (or Chat screen)
- ✓ Conversation screen shows:
  - Language: "Spanish"
  - Level: "A1"
  - Topic: "Greetings" (or conversation starter related to greetings)
  - Initial tutor message in Spanish (greeting-related)
  - Message input box for user to type/speak

**Success Criteria:**
- Transition is smooth and takes <5 seconds
- Initial message appears in Spanish
- All conversation details are correctly reflected

---

### Test 5.5: Conversation Screen - Message Display

**Objective:** Verify messages display correctly with proper speaker identification

**Steps:**
1. In active conversation (from Test 5.4)
2. Locate the **Message Area** (chat/message display region)
3. Observe the initial tutor message

**Expected Results:**
- ✓ Tutor message is displayed clearly
- ✓ Message is labeled as "Tutor" or from "AI" (visual distinction)
- ✓ Message appears on the left side or has distinct styling
- ✓ Message text is in Spanish
- ✓ Message is fully readable without truncation
- ✓ Timestamp is shown (optional but good to have)

**Success Criteria:**
- Speaker is clearly identified (not ambiguous)
- Message is complete and readable
- Styling/colors make it easy to distinguish tutor vs user

---

### Test 5.6: Conversation Screen - Voice Input

**Objective:** Verify voice recording and input works (if microphone available)

**Steps:**
1. In active conversation
2. Locate the **Voice Input Button** (microphone icon or "Speak" button)
3. Ensure microphone is enabled in browser permissions
4. Click the voice button
5. Speak clearly: **"Hola, me llamo María"** (in Spanish)
6. Wait for STT processing (typically 1-3 seconds)

**Expected Results:**
- ✓ Voice button shows recording state (red indicator or "Recording..." text)
- ✓ Browser asks for microphone permission (if first time)
- ✓ User speech is clearly captured (you hear echo or sound level indicator)
- ✓ After speaking, button returns to normal state
- ✓ Message input field populates with transcribed text in Spanish
- ✓ Transcribed text is accurate or very close to what was spoken
- ✓ Text can be edited before sending

**Success Criteria:**
- Voice input is processed without errors
- Transcription is reasonably accurate (>90% for clear speech)
- User can proceed to send the message

**Fallback (if microphone unavailable):**
- ✓ Voice button should show as disabled or display helpful message
- ✓ Text input box remains functional as alternative

---

### Test 5.7: Conversation Screen - TTS Playback

**Objective:** Verify text-to-speech playback works

**Steps:**
1. In active conversation with tutor message visible
2. Locate the **Speaker Icon** or **"Speak"** button near the tutor message
3. Click the speaker button

**Expected Results:**
- ✓ Button shows playing state (animated icon or "Playing..." indicator)
- ✓ Audio begins playing from browser speaker
- ✓ Audio is in Spanish with clear pronunciation
- ✓ Audio matches the text message
- ✓ Playback completes without interruption
- ✓ Button returns to normal state after playback ends
- ✓ Volume level is comfortable (not too loud/quiet)

**Success Criteria:**
- Audio plays immediately (no long delays)
- Pronunciation sounds natural
- Audio is in correct language (Spanish)

**Verification:**
- Listen to tutor message: "¿Hola! ¿Cómo estás?" should sound like natural Spanish speaker
- Not robotic or unintelligible

---

### Test 5.8: Conversation Screen - Text Input

**Objective:** Verify user can type message and send

**Steps:**
1. In active conversation
2. Click on the **Message Input Box** (text field at bottom)
3. Type: **"Hola, estoy muy bien, gracias."**
4. Click **"Send"** button (or press Enter)

**Expected Results:**
- ✓ Input box accepts text input without errors
- ✓ Text appears in input box as typed
- ✓ Text is in Spanish characters (accents, etc.)
- ✓ Send button becomes active/enabled when text is present
- ✓ Message is submitted and input box clears
- ✓ User message appears in message area
- ✓ User message shows distinct styling (different from tutor)
- ✓ User message is labeled clearly (e.g., "You" or on right side)

**Success Criteria:**
- Message sends without errors
- Message appears in conversation
- Input box resets for next message

---

### Test 5.9: Conversation Screen - Multi-turn Exchange

**Objective:** Verify conversation continues with multiple exchanges

**Steps:**
1. After sending a message (from Test 5.8)
2. Wait 3-5 seconds for tutor to generate response
3. Observe new tutor message appears
4. Send another user message: **"¿De dónde eres?"**

**Expected Results:**
- ✓ Tutor response appears automatically (no manual action needed)
- ✓ Response is in Spanish
- ✓ Response is contextually relevant to previous messages
- ✓ Response demonstrates correct Spanish grammar for A1 level
- ✓ Conversation history shows all messages in order
- ✓ Messages don't get mixed up or overwritten
- ✓ Each message stays in correct position
- ✓ New message exchange works smoothly

**Success Criteria:**
- Conversation flows naturally
- Context is maintained
- No message loss or duplication

---

### Test 5.10: Configuration Screen - Settings Persistence

**Objective:** Verify settings can be saved and persist across sessions

**Steps:**
1. Navigate to **Configuration** screen
2. Change settings:
   - TTS Volume: 75%
   - STT Language Hint: Spanish
   - Theme: Dark mode (if available)
3. Click **"Save Settings"** (if button exists) or settings auto-save
4. Navigate to another screen
5. Go back to Configuration screen
6. Navigate away and close browser

**Expected Results:**
- ✓ Settings page displays all available options
- ✓ Changes are applied immediately or after saving
- ✓ No error messages
- ✓ All changed settings retain their values
- ✓ When you return to Configuration screen, settings are unchanged
- ✓ Settings persist even after closing and reopening browser

**Success Criteria:**
- Settings are properly saved
- Settings are retrieved correctly on reload
- No loss of configuration

---

## Section 6: End-to-End Conversation Testing

### Test 6.1: Complete Spanish Conversation Flow

**Objective:** Verify full conversation in Spanish A1 level works end-to-end

**Setup:**
- Language: Spanish
- Level: A1
- Topic: Greetings

**Steps:**
1. Start new conversation
2. Read initial tutor message (e.g., "¡Hola! ¿Cómo te llamas?")
3. Send user message: **"Me llamo Alex"**
4. Wait for tutor response (~3-5 seconds)
5. Send: **"¿Y tú, cómo te llamas?"**
6. Wait for tutor response
7. Send: **"Mucho gusto"**
8. Wait for tutor response
9. Send: **"¿De dónde eres?"**
10. Wait for tutor response

**Expected Results:**
- ✓ Conversation continues for 5+ message exchanges
- ✓ All tutor messages are in Spanish
- ✓ All messages follow A1 grammar rules (simple, present tense, basic vocabulary)
- ✓ Tutor responses are contextually relevant
- ✓ No error messages at any point
- ✓ Message flow is smooth and natural
- ✓ Conversation stays focused on greetings/introductions (topic-specific)
- ✓ Response time is consistent (3-5 seconds)

**Success Criteria:**
- Complete conversation with 5+ exchanges
- All A1 level requirements met
- Topic relevance maintained throughout

---

### Test 6.2: Cross-Language Conversation - French B1

**Objective:** Verify conversation works with different language and level

**Setup:**
- Language: French
- Level: B1 (Intermediate)
- Topic: Work/Careers

**Steps:**
1. Select French and B1 level from Home screen
2. Select "Work" or "Careers" topic
3. Start conversation
4. Read initial message (should be in French, B1 complexity)
5. Send: **"Je travaille comme développeur"** (appropriate B1 response)
6. Continue conversation with 5+ exchanges
7. Topics should include work, job responsibilities, interests, etc.

**Expected Results:**
- ✓ UI language switches to French (labels, placeholders)
- ✓ Initial message uses B1 vocabulary (not too simple, not too complex)
- ✓ Tutor responses use past/future tenses (not just present)
- ✓ Vocabulary is more sophisticated than A1 level
- ✓ Conversations is about work-related topics
- ✓ Grammar corrections or suggestions appear if user makes mistakes (if feature exists)
- ✓ Conversation is smooth without errors

**Success Criteria:**
- Language change is complete and consistent
- Level-appropriate complexity throughout
- Topic focus maintained

**Variation Tests:**
- Repeat with German (C1 level) - should be advanced vocabulary and complex structures
- Repeat with Italian (A2 level) - should be slightly beyond absolute beginner

---

### Test 6.3: Voice Input and TTS in Conversation

**Objective:** Verify voice interaction throughout a conversation

**Setup:**
- Language: Spanish
- Level: A1
- Topic: Food

**Steps:**
1. Start conversation
2. Wait for initial tutor message (Spanish)
3. Click speaker icon to hear tutor message (TTS)
4. Wait for audio to complete
5. Click microphone to speak: **"Me gusta la pizza"**
6. Wait for STT processing
7. Verify transcribed text is correct
8. Send the message
9. Wait for tutor response
10. Play tutor response with TTS
11. Speak response: **"¿Cuál es tu comida favorita?"**
12. Continue for 3+ complete voice-based exchanges

**Expected Results:**
- ✓ Tutor TTS plays correctly for each message
- ✓ Audio quality is clear and understandable
- ✓ Pronunciation is correct for Spanish
- ✓ Voice input captures user speech accurately (>85% accuracy)
- ✓ Transcribed text matches what was spoken
- ✓ No audio delays or glitches
- ✓ Entire conversation works smoothly with voice interaction
- ✓ Transition between listening, speaking, and processing is seamless

**Success Criteria:**
- Full conversation with 3+ voice exchanges
- STT accuracy >85%
- TTS quality sounds natural
- No technical issues

---

### Test 6.4: Multi-language Skill Testing

**Objective:** Verify conversation quality across multiple languages

**Languages to test:**
1. Spanish (Topic: Weather) - A2 level
2. French (Topic: Hobbies) - B1 level
3. German (Topic: Shopping) - A1 level

**Steps (repeat for each language):**
1. Select language/level/topic from Home
2. Start conversation
3. Complete 5-7 message exchanges
4. Use mix of text and voice input
5. Use TTS for listening
6. Note any differences in quality

**Expected Results for Each Language:**
- ✓ Tutor messages are in correct language
- ✓ Grammar and vocabulary match the selected level
- ✓ Topic is consistently addressed
- ✓ Pronunciation/TTS sounds natural
- ✓ STT recognizes language correctly
- ✓ Response quality is comparable across languages

**Success Criteria:**
- All 3 languages work without major issues
- Quality is consistent
- No language-specific bugs

---

### Test 6.5: CEFR Level Adaptation Verification

**Objective:** Verify vocabulary and grammar match CEFR levels

**Setup - A1 Level (Absolute Beginner):**
- Select Spanish A1
- Topic: Family

**Expected Language Characteristics:**
- Simple present tense only
- Very basic vocabulary (common nouns, verbs)
- Short sentences (5-10 words max)
- Common phrases and expressions
- Example: "Tengo una hermana. Se llama María. Tiene diez años."

**Observation Points:**
- ✓ No complex verb conjugations
- ✓ No subjunctive mood
- ✓ No advanced vocabulary
- ✓ Sentences are short and simple

---

**Setup - B2 Level (Upper Intermediate):**
- Select Spanish B2
- Topic: Culture/Travel

**Expected Language Characteristics:**
- Mix of tenses (present, past, future, conditional)
- Advanced vocabulary
- Complex sentence structures
- Subordinate clauses
- Example: "Si tuviera la oportunidad de viajar, visitaría los museos del Prado. Aunque sea muy caro, creo que valdría la pena."

**Observation Points:**
- ✓ Uses past perfect and future conditional
- ✓ Advanced vocabulary (subjunctive mood appears)
- ✓ Complex sentence structure
- ✓ Shows nuance and detail

**Comparison:**
- Side-by-side comparison shows clear difference in complexity
- A1 messages are simpler and shorter
- B2 messages are more elaborate and sophisticated

**Success Criteria:**
- A1 and B2 conversations show clearly different complexity levels
- Vocabulary and grammar match CEFR levels accurately

---

### Test 6.6: Conversation Persistence

**Objective:** Verify conversation is saved and can be retrieved

**Steps:**
1. Start a conversation with Spanish A1
2. Send 3-5 messages (mix of user and tutor)
3. Note the conversation ID or title
4. Leave conversation (go to Home or other screen)
5. Navigate back to **Conversations History** (if available)
6. Find the conversation you just had
7. Click to reopen it

**Expected Results:**
- ✓ Conversation appears in history with:
  - Language and level (Spanish A1)
  - Topic (Greetings)
  - Date/time created
  - Preview of last message or first message
  - Message count (e.g., "5 messages")
- ✓ When reopened, all messages are preserved:
  - Exact same messages you sent
  - Exact same tutor responses
  - Same order
  - All metadata intact
- ✓ Can continue conversation from where it left off
- ✓ New messages are added to existing conversation

**Success Criteria:**
- Conversation is saved to database
- All information is preserved
- Conversation can be reopened and continued

---

### Test 6.7: Error Handling and Recovery

**Objective:** Verify app handles errors gracefully

**Scenarios to test:**

**Scenario A: Network Interruption**
- In active conversation, temporarily disconnect network
- Try to send a message

**Expected Results:**
- ✓ Error message appears (not a crash)
- ✓ Message shows: "Connection lost" or "Please check your internet"
- ✓ User can retry or navigate to home
- ✓ App remains functional after reconnect

**Scenario B: Invalid Input**
- In text input, try very long message (>1000 characters)
- Try special characters or emojis

**Expected Results:**
- ✓ App handles input without crashing
- ✓ Either rejects gracefully or truncates
- ✓ User gets feedback about the issue

**Scenario C: LLM Response Timeout**
- Wait 30+ seconds for LLM response
- Backend may time out

**Expected Results:**
- ✓ App shows "Tutor is thinking..." or loading indicator
- ✓ Timeout after 30 seconds with user-friendly message
- ✓ User can retry or start new conversation
- ✓ App doesn't freeze

**Success Criteria:**
- All errors are handled gracefully
- User can recover from errors
- No crashes or data loss

---

## Test Completion Checklist

After all tests are complete, verify:

- [ ] Section 5.1 - Language selection works
- [ ] Section 5.2 - CEFR level selection works
- [ ] Section 5.3 - Topic selection works
- [ ] Section 5.4 - Start conversation works
- [ ] Section 5.5 - Message display is correct
- [ ] Section 5.6 - Voice input works
- [ ] Section 5.7 - TTS playback works
- [ ] Section 5.8 - Text input works
- [ ] Section 5.9 - Multi-turn exchange works
- [ ] Section 5.10 - Settings persist
- [ ] Section 6.1 - Spanish A1 conversation works
- [ ] Section 6.2 - Cross-language B1 conversation works
- [ ] Section 6.3 - Voice I/O in conversation works
- [ ] Section 6.4 - Multiple languages work
- [ ] Section 6.5 - CEFR levels show different complexity
- [ ] Section 6.6 - Conversations are saved and persistent
- [ ] Section 6.7 - Error handling works

## Summary

- **Total Manual Tests:** 17 detailed test cases
- **Estimated Time:** 60-90 minutes
- **Key Metrics:**
  - Message accuracy: >95%
  - Response time: <5 seconds
  - Voice accuracy: >85%
  - No crashes or data loss

All tests should pass before marking Section 5-6 as complete.
