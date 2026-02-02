# Licensing Strategy

## Purpose

Rationale and implementation of dual licensing model.

## Dual Licensing Model

### AGPL-3.0 (Open Source)
**Who**: Individual users, open-source projects, AGPL-compliant use

**Rights**:
- Use, modify, distribute
- Must share source if networked use
- Must use AGPL-3.0 for derivatives

**See**: [LICENSE](../../../LICENSE)

### Commercial License
**Who**: Enterprises embedding in proprietary products

**Rights**:
- Use without AGPL source-sharing requirement
- Proprietary derivative works
- Commercial redistribution

**See**: [COMMERCIAL_LICENSE.md](../../../COMMERCIAL_LICENSE.md)

## Rationale

### Why Dual Licensing?
1. **Sustainability**: Generate revenue to fund development
2. **Balance**: Open-source values + business viability
3. **Protection**: AGPL prevents proprietary forks without contributing

### Why AGPL-3.0 (Not MIT/Apache)?
- **Network Copyleft**: Prevents SaaS providers from using without sharing
- **Stronger Protection**: Ensures derivatives contribute back
- **Commercial Incentive**: Creates clear need for commercial license

### Trade-Offs
- **CLA Required**: Adds contributor friction
- **Less Permissive**: May deter some users (accept this trade-off)

## CLA (Contributor License Agreement)

**Purpose**: Enable dual licensing legally

**What It Does**:
- Contributors grant rights for both AGPL and commercial use
- Project owner can dual-license contributions

**See**: [CLA.md](../../../CLA.md)

## Related Docs

- [LICENSING.md](../../../LICENSING.md) - Plain-English guidance
- [trade-offs.md](../08-decisions/trade-offs.md) - Licensing trade-offs

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
