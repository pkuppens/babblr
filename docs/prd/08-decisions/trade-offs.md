# Trade-Offs

## Purpose

Document key trade-offs made and justification.

## Trade-Off Log

### 1. Dual Licensing (AGPL + Commercial) vs. Pure Open Source

**Given Up**: Some contributor goodwill, wider adoption

**Gained**: Sustainable revenue model, long-term viability

**Justification**:
- Pure open-source risks abandonment if no funding
- AGPL still permits open-source use
- Commercial license optional, not required

**Decision**: Worth the trade-off for sustainability

---

### 2. Desktop-First vs. Mobile-First

**Given Up**: Larger mobile user base, convenience

**Gained**: Faster development, better offline support, privacy

**Justification**:
- Desktop easier for MVP (single codebase, Electron)
- Better privacy (local SQLite)
- Mobile planned for v3.0

**Decision**: Desktop-first, mobile later

---

### 3. CLA Requirement vs. No CLA

**Given Up**: Contributor friction (signing CLA)

**Gained**: Dual licensing legally enforceable

**Justification**:
- CLA necessary for commercial licensing
- Transparent about rationale
- Many successful projects use CLA

**Decision**: Required for business model

---

### 4. Privacy (Local-First) vs. Convenience (Cloud Sync)

**Given Up**: Multi-device sync convenience

**Gained**: Strong privacy, no cloud costs, no vendor lock-in

**Justification**:
- Privacy differentiator in market
- Manual export/import workaround acceptable
- Target users (privacy-conscious) value privacy over convenience

**Decision**: Prioritize privacy

---

### 5. Natural Conversation vs. Gamification

**Given Up**: Engagement tactics (streaks, points), potentially higher retention

**Gained**: Evidence-based learning, adult-focused UX, intrinsic motivation

**Justification**:
- Research: intrinsic motivation > extrinsic for long-term learning
- Target users (adults) find gamification childish
- Differentiation from Duolingo

**Decision**: Natural conversation, no gamification

---

## Trade-Off Framework

When evaluating trade-offs:
1. What are we giving up? What are we gaining?
2. Does it align with mission and principles?
3. Is it reversible? (If yes, easier decision)
4. What do users/stakeholders prefer?
5. What does research say?

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
