# Visual Guide

This guide shows what the Babblr app looks like and how to use it.

## Home Screen

When you first start Babblr, you'll see:

### Language Selection
- Choose from 5 languages: Spanish 🇪🇸, Italian 🇮🇹, German 🇩🇪, French 🇫🇷, Dutch 🇳🇱
- Large flag buttons for easy selection
- Highlighted in blue when selected

### Difficulty Level
- **Beginner**: "Just starting out" - Simple sentences, basic vocabulary
- **Intermediate**: "Building fluency" - More complex grammar and structures
- **Advanced**: "Refining skills" - Sophisticated vocabulary and nuance

### Recent Conversations
- Below the language selector
- Shows your previous learning sessions
- Each card displays:
  - Language flag
  - Language name
  - Difficulty level badge
  - Last updated time
  - Delete button (🗑️)

### Start Learning Button
- Large gradient button at bottom
- Starts a new conversation with selected language and difficulty

## Conversation Screen

After clicking "Start Learning":

### Header
- **Back button** (←) - Return to home screen
- **Language name** - Current learning language
- **Difficulty badge** - Your selected level

### Message Area
- **Empty state**: Friendly prompt to start conversation
  - "👋 Start your conversation!"
  - "Try introducing yourself or asking a question."

- **Messages**: Chat bubbles appear as you converse
  - **Your messages**: Blue bubbles on the right
  - **AI tutor messages**: White bubbles with border on the left
  - Each message shows timestamp

- **Loading indicator**: Three animated dots while AI is thinking

### Corrections Panel (appears when needed)
- Yellow/gold background banner
- Shows when you make mistakes
- Each correction shows:
  - **Type badge**: grammar/vocabulary/style
  - **Original text**: Struck through in red
  - **Corrected text**: In green with arrow
  - **Explanation**: Brief, encouraging explanation

### Input Area (bottom)
- **🎤 Voice button** (left): 
  - Green circular button
  - Click to start recording
  - Turns red with pulsing animation while recording
  - Click again to stop and transcribe

- **Text input** (center):
  - Type your message
  - Placeholder: "Type your message or use voice..."
  - Press Enter to send

- **Send button** (right):
  - Blue button
  - Sends your typed message
  - Disabled when input is empty

## Features in Action

### Voice Recording Flow
1. Click microphone button 🎤
2. Button turns red and pulses
3. Speak your message
4. Click again to stop
5. Audio is sent to Whisper for transcription
6. Transcribed text appears and is sent to AI
7. AI responds with audio playback

### Conversation Flow
1. User sends message (voice or text)
2. Message appears in chat
3. AI analyzes for errors
4. If errors found, corrections panel appears
5. AI responds naturally in target language
6. Response appears with automatic TTS playback
7. Continue conversation naturally

### Error Correction Example

**You type:** "Yo es feliz"

**Corrections panel shows:**
- Type: `grammar`
- Original: "Yo es" → Corrected: "Yo soy"
- Explanation: "The verb 'ser' is irregular. Use 'soy' for 'I am'."

**AI response:** "¡Me alegro de que estés feliz! ¿Qué te hace feliz hoy?"
(Naturally incorporating the correction without being preachy)

## Navigation

### Main Menu Flow
```
Home Screen
  ├─ New Conversation → Conversation Screen
  │                       └─ Back → Home Screen
  │
  └─ Recent Conversations → Conversation Screen
                             └─ Back → Home Screen
```

### Data Flow
```
Voice Input → Whisper → Text → Claude → Response → TTS → Audio Output
     ↓                            ↓
  Saved in DB              Error Correction
```

## Color Scheme

- **Primary Blue**: #4a90e2 - Main actions, user messages
- **Secondary Green**: #50c878 - Voice button, success states
- **Background**: #f5f7fa - Light gray backdrop
- **Surface**: #ffffff - White cards and panels
- **Text Primary**: #2c3e50 - Main text
- **Text Secondary**: #7f8c8d - Timestamps, labels
- **Corrections**: #fff3cd background, #ffc107 borders
- **Error**: #dc3545 - Original text
- **Success**: #28a745 - Corrected text

## Responsive Design

The app is designed for desktop:
- Default window: 1200x800 pixels
- Minimum comfortable size: 1024x600
- Scales gracefully on larger screens
- Components adapt to window size

## Accessibility

- Clear visual hierarchy
- High contrast text
- Large click targets (buttons)
- Keyboard navigation support (Enter to send)
- Screen reader friendly structure
- Clear loading states

## Tips for Best Experience

1. **Use headphones** to avoid audio feedback with TTS
2. **Good microphone** for accurate transcription
3. **Quiet environment** for better voice recognition
4. **Natural speaking** - don't over-enunciate
5. **Take corrections positively** - they're learning opportunities
6. **Practice regularly** - Short sessions daily beat long cramming
7. **Explore topics** - Talk about things that interest you

## Keyboard Shortcuts

- `Enter` - Send message
- `Esc` - Close corrections panel (if implemented)
- Click header title - Quick return to home

## Performance Notes

- First message may be slower (loading AI model)
- Voice transcription takes 2-5 seconds
- TTS generation is near-instant
- Responses typically arrive in 1-3 seconds
- Database operations are instant (SQLite)

## What to Expect

### Beginner Experience
- Simple greetings and basic questions
- Present tense focus
- Gentle corrections
- Encouraging responses
- Building confidence

### Intermediate Experience
- More varied conversations
- Past and future tenses
- Idioms and expressions
- Contextual corrections
- Expanding vocabulary

### Advanced Experience
- Nuanced discussions
- Complex grammar
- Subjunctive and conditional
- Cultural references
- Refined expression

## Example Conversations

### Beginner Spanish
```
You: Hola, yo llamo Juan.
Correction: "yo llamo" → "me llamo" (reflexive verb)
AI: ¡Hola Juan! Me llamo Sofia. ¿Cómo estás hoy?
```

### Intermediate French
```
You: Hier, je suis allé au cinéma.
Correction: "je suis allé" → "je suis allé" (correct! ✓)
AI: Super ! Qu'est-ce que tu as regardé ? J'adore le cinéma aussi.
```

### Advanced German
```
You: Ich würde gerne über die deutsche Kultur sprechen.
AI: Sehr gerne! Was interessiert dich besonders? Die Geschichte, 
    die Literatur, oder vielleicht die moderne Popkultur?
```

## Troubleshooting Visual Issues

If the UI looks broken:
1. Refresh (Ctrl+R or Cmd+R)
2. Check browser console for errors
3. Verify CSS files loaded
4. Clear browser cache
5. Restart Electron app

## Customization

Want to change the look? Edit CSS files:
- `frontend/src/App.css` - Main styles
- `frontend/src/components/*.css` - Component styles

Colors are defined as CSS variables in App.css for easy theming.
