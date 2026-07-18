# Babblr

Babblr is a desktop language-learning app for conversational practice with an AI tutor across CEFR levels A1-C2.

## Language

**Tutor**:
The AI role that converses with the student in the target language, adapting vocabulary and grammar to the student's CEFR level.
_Avoid_: Teacher agent, teacher

**Student Simulator**:
An LLM prompted to role-play a student at a given CEFR level, producing realistic level-appropriate mistakes, used to generate conversation transcripts for evaluation without a real learner.
_Avoid_: Fake student, mock student

**Comprehensible Input Ratio**:
The proportion of words in a tutor response that the student already knows or has been taught, versus new/unexplained words. Not a fixed number — the target ratio (e.g. ~80%) is a starting point determined by human observation of what feels understandable at a level, not a hard threshold enforced by a frequency list. New words introduced beyond this ratio should be level-appropriate (i+1: a small stretch above the student's current level, not far beyond it).
_Avoid_: Vocabulary coverage, 90% coverage principle

**LLM-as-Judge**:
An LLM used to score a tutor/student conversation transcript against a rubric (e.g. comprehensible input ratio, level-appropriateness of new vocabulary), as a scalable stand-in for human review. Its verdicts are calibrated against a human reading the same transcripts before being trusted to score unsupervised at scale.
