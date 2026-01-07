# Adaptive CEFR Prompt System

## Overview

The adaptive CEFR prompt system provides dynamic, level-appropriate language tutoring prompts based on the Common European Framework of Reference for Languages (CEFR). The system generates customized prompts for AI tutors that adapt to the learner's proficiency level, implementing a "level+1" teaching approach and intelligent correction strategies.

## Features

### 1. CEFR Level Support

The system supports all 6 CEFR levels:

- **A1 (Beginner)**: Complete beginner - learning basic words and simple phrases
- **A2 (Elementary)**: Elementary level - can handle simple routine exchanges
- **B1 (Intermediate)**: Intermediate level - can handle most everyday situations
- **B2 (Upper Intermediate)**: Upper intermediate level - can interact with native speakers with fluency
- **C1 (Advanced)**: Advanced level - can express ideas fluently and spontaneously
- **C2 (Proficiency)**: Proficiency level - can understand and express virtually everything with precision

### 2. Backwards Compatibility

Legacy difficulty levels are automatically mapped to CEFR:
- `beginner` → A1
- `intermediate` → B1
- `advanced` → C1

### 3. Level+1 Teaching Approach

Each level's prompt instructs the AI tutor to:
- Speak primarily at the student's current level
- Introduce slightly more advanced concepts naturally (one per response)
- Use context to help students infer meaning
- Maintain comprehensibility while encouraging growth

**Comprehension targets by level:**
- A1: 95% comprehension, 5% stretch
- A2: 90% comprehension, 10% learning
- B1: 85% comprehension, 15% learning
- B2: 80% comprehension, 20% learning
- C1: 75-80% comprehension, active engagement with complexity
- C2: Native-level discourse with full language richness

### 4. Adaptive Correction Strategies

Correction strategies evolve with proficiency level:

#### A1-B1 Levels (Ignore non-essential errors)
- ✓ **Ignore**: Punctuation, capitalization, diacritical marks (é, ñ, ü, etc.)
- ✓ **Focus**: Basic grammar, core vocabulary, word order

#### B2 Level (Transitional)
- ✓ **Ignore**: Minor punctuation, capitalization
- ✓ **Notice**: Diacritical marks (students should get these right)
- ✓ **Focus**: Subtle grammar, register appropriateness, advanced idioms

#### C1-C2 Levels (Full correction)
- ✓ **Notice**: Everything including punctuation and diacritics
- ✓ **Focus**: Stylistic refinement, cultural nuance, register precision, native-like expression

### 5. Proficiency Assessment

Each prompt includes guidance for the AI tutor to:
- Observe indicators of mastery at the current level
- Notice when students demonstrate readiness for progression
- Subtly suggest level advancement when appropriate

### 6. Variable Substitution

Prompts support dynamic variables:
- `{language}`: Target language (e.g., Spanish, French)
- `{level}`: CEFR level (A1-C2)
- `{topic}`: Current conversation topic
- `{native_language}`: User's native language for explanations
- `{recent_vocab}`: Recently learned vocabulary (auto-truncated to ~10 words)
- `{common_mistakes}`: User's frequent error patterns (auto-truncated to ~5 patterns)

## Architecture

### Components

1. **JSON Templates** (`backend/templates/prompts/`)
   - `a1.json`, `a2.json`, `b1.json`, `b2.json`, `c1.json`, `c2.json`
   - Each contains: level metadata, correction strategy, and prompt template

2. **PromptBuilder Service** (`backend/app/services/prompt_builder.py`)
   - Loads and manages templates
   - Normalizes levels (CEFR ↔ legacy)
   - Performs variable substitution
   - Provides correction strategies

3. **Integration Points**
   - `ConversationService`: Uses PromptBuilder for system prompts
   - `ClaudeService`: Uses PromptBuilder for system prompts
   - Correction methods: Apply level-appropriate correction strategies

### API Endpoints

**GET /conversations/levels/available**
```json
[
  {
    "level": "A1",
    "level_name": "Beginner",
    "description": "Complete beginner level - learning basic words and simple phrases"
  },
  ...
]
```

**POST /conversations**
```json
{
  "language": "Spanish",
  "difficulty_level": "A1"  // or "B1", "C2", "beginner", etc.
}
```

**POST /chat**
```json
{
  "conversation_id": 1,
  "user_message": "Hola, como estas?",
  "language": "Spanish",
  "difficulty_level": "A2"
}
```

## Usage Examples

### Basic Prompt Generation

```python
from app.services.prompt_builder import get_prompt_builder

builder = get_prompt_builder()

# Generate prompt for A1 Spanish learner
prompt = builder.build_prompt(
    language="Spanish",
    level="A1",
    topic="introducing yourself",
    native_language="English",
    recent_vocab=["hola", "gracias", "por favor"],
    common_mistakes=["mixing ser and estar"]
)
```

### Level Normalization

```python
builder.normalize_level("beginner")  # Returns "A1"
builder.normalize_level("b2")        # Returns "B2"
builder.normalize_level("invalid")   # Returns "A1" (default)
```

### Correction Strategies

```python
# Get correction strategy for a level
strategy = builder.get_correction_strategy("A1")
# {
#   "ignore_punctuation": true,
#   "ignore_capitalization": true,
#   "ignore_diacritics": true,
#   "focus_on": ["basic_grammar", "core_vocabulary"]
# }
```

### Level Progression

```python
builder.get_next_level("A1")  # Returns "A2"
builder.get_next_level("C2")  # Returns None (already at max)
```

## Testing

Run unit tests:
```bash
cd backend
pytest tests/test_prompt_builder.py -v
```

Run manual demonstration:
```bash
cd backend
python test_prompt_system.py
```

## Template Structure

Each CEFR level template includes:

```json
{
  "level": "A1",
  "level_name": "Beginner",
  "description": "Complete beginner level...",
  "target_vocabulary_size": 500,
  "max_sentence_length": 10,
  "grammar_complexity": "Present tense, basic subject-verb-object",
  "correction_strategy": {
    "ignore_punctuation": true,
    "ignore_capitalization": true,
    "ignore_diacritics": true,
    "focus_on": ["basic_grammar", "core_vocabulary"],
    "correction_style": "very_gentle_with_native_explanations"
  },
  "template": "You are a patient and encouraging {language} language tutor..."
}
```

## Design Principles

1. **User-Centric**: Focuses on learner needs at each proficiency stage
2. **Evidence-Based**: Follows CEFR guidelines and language acquisition research
3. **Flexible**: Supports both CEFR and legacy level systems
4. **Maintainable**: JSON templates are easy to update and version
5. **Extensible**: New variables and strategies can be added without code changes

## Future Enhancements

Potential improvements:
- Sub-level granularity (A1.1, A1.2, etc.)
- Language-specific templates with cultural adaptations
- User-specific prompt customization (learning style preferences)
- A/B testing framework for prompt variations
- Dynamic difficulty adjustment based on real-time performance
- Integration with spaced repetition for vocabulary review

## Related Files

- Templates: `backend/templates/prompts/*.json`
- Service: `backend/app/services/prompt_builder.py`
- Tests: `backend/tests/test_prompt_builder.py`
- Services using PromptBuilder:
  - `backend/app/services/conversation_service.py`
  - `backend/app/services/claude_service.py`
- API Routes: `backend/app/routes/conversations.py`
- Schemas: `backend/app/models/schemas.py`
