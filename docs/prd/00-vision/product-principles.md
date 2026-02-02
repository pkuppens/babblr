# Product Principles

## Purpose

This document defines Babblr's core design principles and decision-making framework. These principles guide all product decisions, feature prioritization, and trade-offs.

## Core Design Principles

### 1. Natural Conversation Over Gamification

**Principle**: Language fluency comes from natural conversation practice, not gamified drills.

**What This Means**:
- Focus on realistic, contextual conversations
- Avoid points, streaks, leaderboards, and artificial rewards
- Measure progress through real proficiency improvement (CEFR levels)
- Prioritize conversation quality over engagement metrics

**Real Examples**:
- ✅ **YES**: Adaptive conversations that feel like talking to a patient tutor
- ✅ **YES**: Error corrections in context with explanations
- ❌ **NO**: Daily streak counters or XP points
- ❌ **NO**: Competitive leaderboards or social comparison

**Research Basis**: Communicative Language Teaching (CLT) emphasizes meaningful interaction over mechanical drills. See [language-learning-context.md](../03-context/language-learning-context.md).

---

### 2. Adaptive Difficulty That Grows With You

**Principle**: Learning is most effective at the edge of current ability (comprehensible input +1).

**What This Means**:
- Support all CEFR levels (A1 beginner to C2 mastery)
- Adjust vocabulary and grammar to learner's level
- Allow manual difficulty adjustment
- Future: Automatic difficulty adaptation based on performance

**Real Examples**:
- ✅ **YES**: CEFR level selection (A1-C2)
- ✅ **YES**: Vocabulary and grammar complexity matched to level
- ✅ **YES**: Learner can adjust difficulty if too easy/hard
- ❌ **NO**: One-size-fits-all conversations
- ❌ **NO**: Throwing advanced learners into beginner content

**Research Basis**: Krashen's Input Hypothesis (i+1) - learning occurs when exposed to language slightly above current level.

---

### 3. Immersive Learning Through Practical Use

**Principle**: Learn by using the language in realistic situations, not by memorizing decontextualized lists.

**What This Means**:
- Conversation topics relevant to real life (travel, work, daily routines)
- Vocabulary learned in context, not isolated flashcards
- Grammar corrections embedded in conversation flow
- Speaking and listening practice, not just reading/writing

**Real Examples**:
- ✅ **YES**: "Ordering food at a restaurant" conversation scenario
- ✅ **YES**: Vocabulary extracted from actual conversations
- ✅ **YES**: STT (speech-to-text) and TTS (text-to-speech) for listening/speaking
- ❌ **NO**: Memorizing word lists without context
- ❌ **NO**: Grammar drills divorced from communication

**Research Basis**: Task-Based Language Teaching (TBLT) - language acquired through meaningful tasks, not isolated exercises.

---

### 4. Free/Affordable APIs and Local Processing

**Principle**: Language learning should be accessible and affordable, not locked behind expensive subscriptions.

**What This Means**:
- Support free/affordable LLM options (Ollama, low-cost APIs)
- Local-first architecture (SQLite, no cloud required)
- Users control their API costs
- Future: Fully offline mode with local models

**Real Examples**:
- ✅ **YES**: Ollama integration for free local LLM
- ✅ **YES**: User brings their own API keys (Claude, Gemini)
- ✅ **YES**: Local Whisper STT, Edge TTS (free)
- ❌ **NO**: Mandatory expensive subscriptions
- ❌ **NO**: Vendor lock-in to specific LLM providers

**Business Balance**: Free for students using their own APIs; commercial licensing for enterprises embedding Babblr.

---

### 5. Privacy-First and Local-First

**Principle**: User data stays local and under user control.

**What This Means**:
- SQLite database stored locally on user's device
- Conversations sent only to user-chosen LLM provider
- No telemetry, tracking, or data sales
- No required cloud account

**Real Examples**:
- ✅ **YES**: SQLite database in user's home directory
- ✅ **YES**: User chooses LLM provider (Claude, Gemini, Ollama)
- ✅ **YES**: Transparent about what data goes where
- ❌ **NO**: Required cloud sync or account creation
- ❌ **NO**: Selling user data to third parties
- ❌ **NO**: Hidden telemetry or analytics

**Legal Alignment**: Supports GDPR, CCPA, and user data rights.

---

### 6. Evidence-Based Pedagogy

**Principle**: Product decisions grounded in second language acquisition research.

**What This Means**:
- Features aligned with proven teaching methods (CLT, TBLT, comprehensible input)
- Error correction strategy based on research (gentle, explanatory, contextual)
- CEFR framework for standardized proficiency measurement
- Open to updating approach based on new research

**Real Examples**:
- ✅ **YES**: Gentle error corrections with explanations (research-backed)
- ✅ **YES**: CEFR levels for standardized proficiency
- ✅ **YES**: Focus on communication over accuracy drills
- ❌ **NO**: Punitive error feedback (demotivating)
- ❌ **NO**: Features based on trends rather than evidence

**See Also**: [language-learning-context.md](../03-context/language-learning-context.md) for research basis.

---

### 7. Open Source With Sustainable Business Model

**Principle**: Balance open-source values with project sustainability through dual licensing.

**What This Means**:
- AGPL-3.0 license for open-source use
- Commercial license for proprietary/embedded use
- CLA ensures dual licensing rights
- Transparent about business model

**Real Examples**:
- ✅ **YES**: Full source code on GitHub under AGPL-3.0
- ✅ **YES**: Commercial licensing for EdTech companies embedding Babblr
- ✅ **YES**: CLA for contributors (enables dual licensing)
- ❌ **NO**: Relicensing past contributions without CLA
- ❌ **NO**: Bait-and-switch (open-core, feature restrictions)

**See Also**: [licensing-strategy.md](../07-business/licensing-strategy.md)

---

### 8. Modular and Extensible Architecture

**Principle**: Build for flexibility and community contributions.

**What This Means**:
- Pluggable LLM, STT, TTS providers
- Clean API boundaries
- Well-documented codebase
- Support for third-party integrations (future)

**Real Examples**:
- ✅ **YES**: Abstract `BaseLLMProvider` class for swappable LLM providers
- ✅ **YES**: Factory pattern for provider selection
- ✅ **YES**: Comprehensive developer docs ([CLAUDE.md](../../../CLAUDE.md))
- ❌ **NO**: Hardcoded provider dependencies
- ❌ **NO**: Monolithic, tightly-coupled architecture

**See Also**: [architecture-requirements.md](../06-technical/architecture-requirements.md)

---

## Decision Framework

When evaluating new features, changes, or trade-offs, ask:

### 1. Mission Alignment
**Question**: Does this help learners practice natural conversation and become more fluent?

- If YES → Aligns with core mission
- If NO → Reconsider or justify deviation

### 2. Principle Check
**Question**: Does this align with our 8 core principles?

- Check against: Natural conversation, adaptive difficulty, immersive, affordable, privacy-first, evidence-based, open-source, modular
- If conflicts with principle → Document trade-off in [trade-offs.md](../08-decisions/trade-offs.md)

### 3. User Impact
**Question**: Does this address a real user pain point or need?

- Reference stakeholder docs: [students.md](../01-stakeholders/students.md), [tutors.md](../01-stakeholders/tutors.md)
- Validate through user research or feedback

### 4. Evidence Basis
**Question**: Is this grounded in language learning research or validated user feedback?

- Prefer research-backed features over unproven trends
- Cite sources in [language-learning-context.md](../03-context/language-learning-context.md)

### 5. Sustainability
**Question**: Does this support long-term project viability?

- Consider: Development effort, maintenance burden, commercial impact
- Reference [business-model.md](../07-business/business-model.md)

### 6. Privacy Impact
**Question**: Does this respect user privacy and data ownership?

- Local-first whenever possible
- Transparent about data flows
- User control and consent

### 7. Open Source Compatibility
**Question**: Can we build this openly while protecting commercial interests?

- AGPL-3.0 compatible
- Dual licensing friendly
- No proprietary lock-in

### Scoring
- 6-7 YES → Strong go
- 4-5 YES → Consider with documented trade-offs
- 0-3 YES → Likely reject or reconsider

---

## Applying Principles to Past Decisions

### Decision: Focus on Conversation, Not Gamification

**Principle Applied**: Natural Conversation Over Gamification

**Alternatives Considered**:
- Daily streaks and XP points (like Duolingo)
- Leaderboards and social competition

**Why Rejected**:
- Research shows extrinsic motivation (points) less effective than intrinsic motivation (real progress)
- Gamification can distract from actual learning
- Our target users (self-directed learners) value real proficiency over game mechanics

**Documented In**: [prd-decisions.md](../08-decisions/prd-decisions.md)

---

### Decision: Desktop App Over Web/Mobile (Initially)

**Principles Applied**: Privacy-First, Affordable APIs, Modular

**Alternatives Considered**:
- Web app with cloud backend
- Mobile-first approach

**Why Desktop First**:
- Easier offline capability (SQLite local storage)
- Better privacy (no required cloud account)
- Lower infrastructure costs (user's device)
- Faster development (single codebase, Electron)

**Future Plan**: Mobile apps once desktop MVP validated

**Documented In**: [trade-offs.md](../08-decisions/trade-offs.md)

---

### Decision: Dual Licensing (AGPL-3.0 + Commercial)

**Principles Applied**: Open Source with Sustainable Business Model

**Alternatives Considered**:
- Pure open source (MIT/Apache)
- Pure proprietary (closed source)
- Open-core (free tier, paid features)

**Why Dual Licensing**:
- Balances open-source values with sustainability
- Allows commercial use with revenue
- AGPL prevents proprietary forks without contributing back
- CLA enables dual licensing legally

**Trade-Offs**: CLA adds contributor friction, but necessary for model

**Documented In**: [licensing-strategy.md](../07-business/licensing-strategy.md), [trade-offs.md](../08-decisions/trade-offs.md)

---

## Principles in Action: Examples

### Feature Request: Add Daily Streak Counter

**Decision**: ❌ Reject

**Principles Violated**:
- Natural Conversation Over Gamification
- Evidence-Based Pedagogy (extrinsic rewards less effective)

**Alternative**: Progress dashboard showing real metrics (CEFR level, conversations completed, vocabulary learned)

---

### Feature Request: Cloud Sync Across Devices

**Decision**: ❌ Reject (for now)

**Principles Violated**:
- Privacy-First (requires cloud account, data leaves device)

**Trade-Off**: Convenience vs. privacy

**Decision**: Prioritize privacy. Users who want sync can manually export/import data.

**Documented In**: [rejected-features.md](../08-decisions/rejected-features.md)

---

### Feature Request: Support More LLM Providers

**Decision**: ✅ Accept

**Principles Aligned**:
- Affordable APIs (more options for users)
- Privacy-First (user choice)
- Modular Architecture (pluggable providers)

**Implementation**: Abstract provider interface, factory pattern

---

### Feature Request: Grammar Explanations

**Decision**: ✅ Accept (P1 priority)

**Principles Aligned**:
- Evidence-Based Pedagogy (explicit grammar instruction helpful)
- Immersive Learning (grammar in context of errors)

**Implementation**: Integrated into error corrections, not separate drills

---

## Evolving Principles

Principles are not set in stone. They evolve as we learn:

**When to Update Principles**:
- New research challenges assumptions
- User feedback reveals unmet needs
- Market conditions change
- Strategic direction shifts

**How to Update**:
1. Propose change with rationale
2. Review with stakeholders (product, tech, business)
3. Document in [prd-decisions.md](../08-decisions/prd-decisions.md)
4. Update this document
5. Communicate change to contributors

---

## Related Documents

- [Mission & Vision](mission-vision.md) - Strategic foundation
- [Market Positioning](market-positioning.md) - Competitive differentiation
- [PRD Decisions](../08-decisions/prd-decisions.md) - Decision log
- [Rejected Features](../08-decisions/rejected-features.md) - Features rejected based on principles
- [Trade-Offs](../08-decisions/trade-offs.md) - Documented trade-offs
- [Language Learning Context](../03-context/language-learning-context.md) - Research basis

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
**Owner**: Product Management
**Review Frequency**: Quarterly
