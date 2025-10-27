# Complexity Scoring Guide

Detailed guide for scoring each of the 5 complexity factors on a 1-10 scale.

## Overview

Each ticket is scored across 5 dimensions:
1. **Scope Size** - How much code will change
2. **Technical Complexity** - How hard is the logic
3. **Testing Requirements** - How much testing is needed
4. **Risk & Unknowns** - How many unknowns exist
5. **Dependencies** - What blockers or coordination is needed

Scores are weighted differently based on task type (see `task-type-classification.md`).

---

## Factor 1: Scope Size

**What it measures**: Breadth of changes across the codebase

### Scoring Guide

| Score | Files | LOC | API Changes | Description |
|-------|-------|-----|-------------|-------------|
| **1** | 1 | <20 | None | Single file, trivial change |
| **2** | 1-3 | 20-50 | Minimal | Few files, small changes |
| **3** | 3-5 | 50-100 | Limited | Localized to one module |
| **4** | 3-5 | 100-150 | Limited | Touches a few related files |
| **5** | 5-10 | 150-400 | Moderate | Standard feature scope |
| **6** | 5-10 | 400-600 | Moderate | Large feature, multiple modules |
| **7** | 10-20 | 600-800 | Significant | Complex feature, cross-module |
| **8** | 10-20 | 800-1000 | Significant | Major feature, many files |
| **9** | 20+ | 1000-1500 | Major | Very large feature or refactor |
| **10** | 20+ | 1500+ | Major redesign | Epic-level work |

### Examples

**Score 2**: Fix validation error in one form component
- 1 file (LoginForm.tsx)
- ~30 LOC
- No API changes

**Score 5**: Add pagination to search results
- 5-8 files (API endpoint, query builder, UI component, tests)
- ~250 LOC
- Modify existing API to support pagination params

**Score 8**: Implement notification system
- 15+ files (backend, frontend, email templates, database)
- ~900 LOC
- New API endpoints, database tables

---

## Factor 2: Technical Complexity

**What it measures**: Difficulty of the algorithms and integration points

### Scoring Guide

| Score | Algorithms | Integrations | Patterns | Description |
|-------|------------|--------------|----------|-------------|
| **1** | Trivial | None | Simple CRUD | Straightforward logic |
| **2** | Simple | None | Basic | Simple conditionals, no algorithms |
| **3** | Moderate | 1 | Standard | Some business logic |
| **4** | Moderate | 1-2 | Standard | Multiple conditions, basic validation |
| **5** | Complex | 3-4 | Advanced | Business rules, state management |
| **6** | Complex | 3-4 | Advanced | Complex validation, data transformation |
| **7** | Very complex | 5+ | Expert | Advanced patterns, multiple integrations |
| **8** | Very complex | 5+ | Expert | Concurrency, async patterns needed |
| **9** | Highly complex | Many | Cutting-edge | Distributed systems, performance critical |
| **10** | Extremely complex | Many | Novel | Research-level algorithms |

### Examples

**Score 2**: Update user profile field
- Simple UPDATE query
- No integrations
- Basic validation

**Score 5**: Implement shopping cart
- Business logic for cart rules, discounts
- 3 integrations (inventory, pricing, tax calc)
- State management (session, cache)

**Score 8**: Build real-time collaboration feature
- WebSocket connections
- Conflict resolution algorithms
- 5+ integrations (auth, presence, storage, notifications, analytics)
- Concurrency handling

---

## Factor 3: Testing Requirements

**What it measures**: How much test coverage and test complexity is needed

### Scoring Guide

| Score | Unit Tests | Integration Tests | E2E Tests | Test Data Complexity |
|-------|------------|-------------------|-----------|---------------------|
| **1** | Minimal | None | None | Simple |
| **2** | Basic | None | None | Simple |
| **3** | Standard | Basic | None | Moderate |
| **4** | Standard | Basic | None | Moderate |
| **5** | Comprehensive | Standard | None | Moderate |
| **6** | Comprehensive | Standard | Basic | Complex |
| **7** | Extensive | Extensive | Basic | Complex |
| **8** | Extensive | Extensive | Standard | Very complex |
| **9** | Very extensive | Very extensive | Extensive | Very complex |
| **10** | Critical coverage | Full integration | Full E2E | Extremely complex |

### Project-Specific Considerations

**Frontend Projects** (React, Vue):
- Higher E2E testing needs (Playwright/Cypress)
- Component testing
- Accessibility testing

**Backend Projects** (Laravel, Lambda):
- API integration tests
- Database transaction tests
- Contract tests

**Full-Stack Projects**:
- End-to-end user flows
- Backend + frontend integration

### Examples

**Score 2**: Fix typo in static text
- No test changes needed
- Verify visually

**Score 5**: Add pagination endpoint
- Unit tests for query builder
- Integration tests for API endpoint
- Test data: multiple pages of records

**Score 9**: Payment processing integration
- Extensive unit tests for business logic
- Integration tests with payment provider (sandbox)
- E2E tests for checkout flow
- Test data: various card types, edge cases, refunds

---

## Factor 4: Risk & Unknowns

**What it measures**: Uncertainty and potential for unexpected issues

### Scoring Guide

| Score | Tech Familiarity | Requirements Clarity | Breaking Changes | Third-Party Risk |
|-------|------------------|---------------------|------------------|------------------|
| **1** | Very familiar | Crystal clear | None | None |
| **2** | Familiar | Clear | None | Low |
| **3** | Familiar | Clear | Minor | Low |
| **4** | Mostly familiar | Minor ambiguity | Minor | Moderate |
| **5** | Some new tech | Some ambiguity | Moderate | Moderate |
| **6** | Some new tech | Moderate ambiguity | Moderate | Moderate |
| **7** | Significant new tech | Significant ambiguity | Significant | High |
| **8** | Mostly unfamiliar | Significant ambiguity | Significant | High |
| **9** | Unfamiliar | Major ambiguity | Major | Very high |
| **10** | Completely new | Extremely ambiguous | Critical | Critical |

### Risk Categories

**Technology Risk**:
- Using a library/framework for the first time
- Upgrading to new major version
- Adopting new architecture patterns

**Requirements Risk**:
- Vague acceptance criteria
- Unclear edge cases
- Missing stakeholder input

**Integration Risk**:
- Third-party API behavior unknown
- External service reliability concerns
- Dependency on external team

**Impact Risk**:
- Breaking changes to public API
- Database migration required
- Affects critical user flows

### Examples

**Score 2**: Add field to existing form
- Very familiar tech (React)
- Clear requirements
- No breaking changes
- No third-party dependencies

**Score 6**: Integrate new analytics provider
- Some new tech (unfamiliar SDK)
- Moderate ambiguity (which events to track?)
- No breaking changes
- Third-party API reliability unknown

**Score 9**: Migrate to microservices architecture
- Unfamiliar patterns (never done microservices)
- Major ambiguity (service boundaries unclear)
- Major breaking changes
- Many unknowns

---

## Factor 5: Dependencies

**What it measures**: Blockers, coordination needs, and what else might break

### Scoring Guide

| Score | Blockers | Coordination | Parallel Work | Impact Radius |
|-------|----------|--------------|---------------|---------------|
| **1** | None | None | Fully independent | Isolated |
| **2** | None | Minimal | Mostly independent | Localized |
| **3** | Minor | Minimal | Mostly independent | Localized |
| **4** | Minor | Some | Some dependencies | Limited radius |
| **5** | Some | Moderate | Some dependencies | Moderate radius |
| **6** | Some | Moderate | Limited parallel | Moderate radius |
| **7** | Multiple | Significant | Limited parallel | Wide radius |
| **8** | Multiple | Cross-team | Sequential only | Wide radius |
| **9** | Critical path | Extensive cross-team | Sequential only | System-wide |
| **10** | Critical blockers | Many teams | Fully sequential | System-wide |

### Dependency Types

**Blocking Dependencies**:
- Waiting for another ticket to complete
- Waiting for infrastructure provisioning
- Waiting for third-party approval/access

**Coordination Dependencies**:
- Need input from other team members
- Cross-team collaboration required
- Stakeholder approvals needed

**Impact Dependencies** ("What else breaks?"):
- Shared utilities/libraries affected
- Multiple features depend on this code
- Database schema changes affect other services

### Examples

**Score 2**: Fix typo in isolated component
- No blockers
- No coordination needed
- Fully independent work
- Isolated impact

**Score 5**: Add new API endpoint
- Some dependencies (need DB migration)
- Moderate coordination (API contract review)
- Some parallel work possible
- Moderate impact (clients need to update)

**Score 9**: Implement SSO across all products
- Critical path (all products depend on this)
- Extensive cross-team (security, product, infra)
- Must be sequential (rollout plan)
- System-wide impact

---

## Weighted Complexity Calculation

Scores are weighted differently based on task type:

### Bug Fix Example

**Scores**:
- Scope Size: 2
- Technical Complexity: 2
- Testing Requirements: 4
- Risk & Unknowns: 2
- Dependencies: 3

**Weights** (Bug Fix):
- Scope Size: 10%
- Technical Complexity: 15%
- Testing Requirements: 30%
- Risk & Unknowns: 10%
- Dependencies: 35%

**Calculation**:
```
rawComplexity = (2×10 + 2×15 + 4×30 + 2×10 + 3×35) / 100
              = (20 + 30 + 120 + 20 + 105) / 100
              = 295 / 100
              = 2.95 / 10
```

**Task Type Multiplier** (Bug Fix): 0.42×
```
adjustedComplexity = 2.95 × 0.42 = 1.24 / 10
```

---

## Scoring Best Practices

1. **Start with scope** - easiest to estimate (count files/LOC)
2. **Consider task type** - bug fixes emphasize dependencies, refactors emphasize testing
3. **Be honest about unknowns** - uncertainty should increase risk score
4. **Think about "what else breaks"** - dependencies are often underestimated
5. **Use repository reconnaissance** - don't guess, actually look at the code
6. **Compare to past work** - reference similar tickets for calibration
7. **Document assumptions** - write down what you're assuming for each score
8. **When uncertain, add +1** - better to over-estimate slightly

---

## Common Scoring Mistakes

### Mistake 1: Underestimating Dependencies

**Wrong**: "It's just one file, dependencies = 1"
**Right**: "This file is imported by 12 other modules, dependencies = 7"

### Mistake 2: Confusing Scope with Complexity

**Wrong**: "Lots of files to change, technical complexity = 10"
**Right**: "Lots of files but simple CRUD logic, scope = 8, technical = 3"

### Mistake 3: Ignoring Testing Requirements

**Wrong**: "Implementation is easy, testing = 2"
**Right**: "Easy to implement but critical path, extensive regression testing needed, testing = 8"

### Mistake 4: Over-confidence in New Tech

**Wrong**: "I'll learn it as I go, risk = 3"
**Right**: "Never used this before, risk = 7, maybe spike first?"

---

## Calibration

Track actual complexity vs estimated complexity:

After completing a ticket, review:
1. Were the scores accurate?
2. Which factor was most off?
3. What was missed in scoring?
4. Update scoring guide based on learnings

Example calibration log:
```
PROJ-123: Add pagination
Estimated: Scope=5, Technical=4, Testing=5, Risk=3, Dependencies=4
Actual: Scope=6 (more files than expected), Technical=4 ✓, Testing=7 (E2E tests complex), Risk=5 (edge cases unclear), Dependencies=4 ✓

Learning: Underestimated testing complexity for E2E scenarios. Increase testing score when E2E is involved.
```
