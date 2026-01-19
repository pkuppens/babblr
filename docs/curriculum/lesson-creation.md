# Lesson Creation Guide

This guide explains how to create and manage lessons in the Babblr system, including curriculum structure, GenAI-powered generation, and extending the curriculum.

## Overview

Lessons in Babblr support multiple types:
- **Grammar**: Grammar rules, conjugations, sentence structures
- **Vocabulary**: Word lists, phrases, topic-based vocabulary
- **Listening**: Listening comprehension exercises (future)

Lessons are generated using GenAI (LLM) to create metadata, with content generated on-demand when lessons are accessed.

## Curriculum Structure

The curriculum is defined in `backend/app/scripts/generate_lessons.py` as a Python dictionary:

```python
SPANISH_CURRICULUM = {
    "A1": {
        "grammar": [
            {"subject": "present_ar_verbs", "order": 1},
            {"subject": "present_er_ir_verbs", "order": 2},
            # ... more topics
        ],
        "vocabulary": [
            {"subject": "greetings", "topic_id": "greetings", "order": 1},
            # ... more topics
        ],
    },
    # ... A2, B1, B2, C1, C2
}
```

### Key Fields

- **subject**: Semantic identifier for the lesson topic (e.g., "present_ar_verbs", "shopping")
- **order**: Display order within the level (lower numbers appear first)
- **topic_id**: Optional link to vocabulary topic (for vocabulary lessons)

## Generating Lessons

### Using the Generation Script

```bash
cd backend
python -m app.scripts.generate_lessons
```

This script:
1. Loads the curriculum structure
2. For each topic/level:
   - Uses LLM to generate lesson metadata (title, oneliner, tutor_prompt)
   - Creates Lesson record in database
   - Sets all fields (subject, order_index, difficulty_level, etc.)

### What Gets Generated

**Metadata (stored in database):**
- `title`: Clear, engaging lesson title
- `oneliner`: Brief description for lesson cards
- `tutor_prompt`: Extensive prompt for on-demand content generation

**Content (generated on-demand):**
- Exercises
- Examples
- Explanations
- Audio URLs

This two-phase approach allows:
- Fast lesson listing (metadata only)
- Dynamic, personalized content generation
- Efficient storage

## Extending the Curriculum

### Adding New Topics

1. **Edit curriculum structure** in `generate_lessons.py`:
   ```python
   "A1": {
       "grammar": [
           # ... existing topics
           {"subject": "new_topic", "order": 6},
       ],
   }
   ```

2. **Run generation script**:
   ```bash
   python -m app.scripts.generate_lessons
   ```

3. **Verify** lessons appear in API:
   ```bash
   curl "http://localhost:8000/lessons?language=es&level=A1&type=grammar"
   ```

### Adding New Levels

1. **Add level to curriculum**:
   ```python
   "A3": {  # Hypothetical new level
       "grammar": [
           {"subject": "advanced_topic", "order": 1},
       ],
   }
   ```

2. **Update CEFRLevel enum** if needed (in `app/models/cefr.py`)

3. **Run generation script**

### Adding New Languages

1. **Create new curriculum structure**:
   ```python
   ITALIAN_CURRICULUM = {
       "A1": {
           # ... topics
       },
   }
   ```

2. **Modify generation script** to support multiple languages

3. **Run generation** for each language

## CEFR Guidelines

When creating curriculum, reference official CEFR documentation:

- **A1 (Beginner)**: Basic phrases, simple sentences, present tense
- **A2 (Elementary)**: Past tense intro, common vocabulary, simple conversations
- **B1 (Intermediate)**: Complex sentences, subjunctive intro, varied topics
- **B2 (Upper Intermediate)**: Advanced grammar, nuanced vocabulary, abstract topics
- **C1 (Advanced)**: Complex structures, idiomatic expressions, professional topics
- **C2 (Proficient)**: Near-native fluency, literary language, all topics

### Resources

- [CEFR Official Website](https://www.coe.int/en/web/common-european-framework-reference-languages)
- [CEFR Self-Assessment Grid](https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale)
- Language-specific CEFR guidelines (e.g., Instituto Cervantes for Spanish)

## Best Practices

### Curriculum Design

1. **Start with essentials**: Focus on most common/useful topics first
2. **Progressive difficulty**: Build on previous lessons
3. **Balance types**: Mix grammar, vocabulary, and listening
4. **Real-world relevance**: Prioritize practical, everyday language

### Subject Naming

Use clear, consistent subject identifiers:
- `present_ar_verbs` (not `present_ar` or `ar_verbs`)
- `ser_estar_basic` (not `ser_estar` or `ser_vs_estar`)
- `shopping_vocabulary` (not `shopping` or `shop`)

### Tutor Prompts

Effective tutor prompts include:
- **Learning objectives**: What will the learner achieve?
- **Key concepts**: What grammar/vocabulary to cover?
- **Examples**: Sample structures to include
- **Common mistakes**: Errors to address proactively
- **Teaching approach**: How to present for the level

Example:
```
You are teaching Spanish present tense -ar verbs to an A1 learner.

Learning objectives:
- Understand the conjugation pattern
- Practice common verbs (hablar, comprar, estudiar)
- Form simple sentences

Key concepts:
- Verb stem + endings (-o, -as, -a, -amos, -áis, -an)
- Subject-verb agreement

Common mistakes:
- Forgetting to change the ending
- Using wrong person ending

Generate clear, encouraging explanations with simple examples.
```

## Not Aiming for 100% Coverage

The curriculum focuses on **key topics that provide value**, not exhaustive coverage. This allows:
- Faster implementation
- Focus on high-value lessons
- Incremental expansion based on user needs

## Manual Lesson Creation

You can also create lessons manually via the API or database:

```python
from app.models.models import Lesson

lesson = Lesson(
    language="es",
    lesson_type="grammar",
    title="Custom Lesson",
    oneliner="Learn something custom",
    subject="custom_topic",
    difficulty_level="A1",
    order_index=10,
    is_active=True,
)
```

## Troubleshooting

### Lessons Not Appearing

1. Check `is_active=True` in database
2. Verify language code matches (e.g., "es" not "spanish")
3. Check level format (uppercase: "A1" not "a1")

### Generation Errors

1. Check LLM provider is configured
2. Verify database connection
3. Check logs for JSON parsing errors

### Duplicate Lessons

The script skips existing lessons (same language, type, subject, level). To regenerate:
1. Delete existing lesson from database
2. Run generation script again
