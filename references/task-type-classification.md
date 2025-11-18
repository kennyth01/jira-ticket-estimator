# Task Type Classification Guide

Complete guide to classifying tickets into one of 5 task types, each with distinct characteristics and estimation multipliers.

## Overview

Task types determine:
1. **Base unit time** for implementation (12.5-30 min per complexity point)
2. **Complexity multiplier** applied to raw complexity score (0.42-1.0×)
3. **Complexity weight distribution** across the 5 factors

## Task Type Definitions

### 1. Net-New Feature

**Building something that doesn't exist in the codebase**

**Characteristics**:
- Creating new files/components from scratch
- Introducing new patterns or architectures
- Adding new integrations or dependencies
- No similar code to reference

**Estimation Parameters**:
- Base Unit: **30 minutes** per complexity point
- Complexity Multiplier: **1.0×** (no reduction)
- Human Multiplier: **3.0×** AI time

**Keywords**: new, create, build, implement

**Issue Types**: Story

**Complexity Weights**:
| Factor | Weight |
|--------|--------|
| Scope Size | 25% |
| Technical Complexity | 25% |
| Testing Requirements | 20% |
| Risk & Unknowns | 20% |
| Dependencies | 10% |

**Examples**:
- "Build new Stripe payment integration with webhook handlers"
- "Implement real-time chat feature using WebSockets"
- "Create admin dashboard for user management"

---

### 2. Enhancement/Extension

**Extending existing functionality with new capabilities**

**Characteristics**:
- Adding features to existing components
- Following established patterns
- Similar code exists as reference
- Some new logic but within familiar domain

**Estimation Parameters**:
- Base Unit: **22.5 minutes** per complexity point
- Complexity Multiplier: **0.75×** (25% reduction from net-new)
- Human Multiplier: **2.75×** AI time

**Keywords**: add, extend, enhance, support (without "new")

**Complexity Weights**:
| Factor | Weight |
|--------|--------|
| Scope Size | 20% |
| Technical Complexity | 25% |
| Testing Requirements | 20% |
| Risk & Unknowns | 20% |
| Dependencies | 15% |

**Examples**:
- "Add pagination to existing search results"
- "Extend user profile with additional fields"
- "Support CSV export in existing reports"

---

### 3. Refactor/Hardening

**Improving existing code without changing behavior**

**Characteristics**:
- Strengthening validation/error handling
- Improving type safety
- Optimizing existing code
- No new features, just better implementation
- Established patterns being reinforced

**Estimation Parameters**:
- Base Unit: **17.5 minutes** per complexity point
- Complexity Multiplier: **0.58×** (42% reduction from net-new)
- Human Multiplier: **2.5×** AI time

**Keywords**: refactor, improve, optimize, harden, strengthen, type, validate

**Complexity Weights**:
| Factor | Weight |
|--------|--------|
| Scope Size | 15% |
| Technical Complexity | 20% |
| Testing Requirements | 25% ⚠️ |
| Risk & Unknowns | 15% |
| Dependencies | 25% ⚠️ |

**Note**: Testing and Dependencies are emphasized because refactoring requires extensive regression testing and careful consideration of what else might break.

**Examples**:
- "Strengthen zipcode validation and add error handling"
- "Improve DynamoDB query patterns for better performance"
- "Add type guards to existing JavaScript functions"
- "Optimize Lambda cold start time"

---

### 4. Bug Fix

**Fixing incorrect behavior in existing code**

**Characteristics**:
- Problem is well-defined
- Code location is known
- Fix is typically localized (1-3 files)
- Testing focuses on regression

**Estimation Parameters**:
- Base Unit: **12.5 minutes** per complexity point
- Complexity Multiplier: **0.42×** (58% reduction from net-new)
- Human Multiplier: **2.5×** AI time

**Keywords**: fix, bug, defect, issue, broken, error

**Issue Types**: Bug

**Complexity Weights**:
| Factor | Weight |
|--------|--------|
| Scope Size | 10% |
| Technical Complexity | 15% |
| Testing Requirements | 30% ⚠️ |
| Risk & Unknowns | 10% |
| Dependencies | 35% ⚠️ |

**Note**: Dependencies are heavily weighted (35%) because understanding "what else breaks if we change this?" is critical for bug fixes.

**Examples**:
- "Fix validation error on login form"
- "Correct calculation logic in tax computation"
- "Resolve null pointer exception in checkout flow"
- "Fix race condition in async operation"

---

### 5. Spike/Investigation

**Research work with uncertain outcomes**

**Characteristics**:
- Exploring unknowns
- Prototyping solutions
- Evaluating technologies
- No production deliverable

**Estimation Parameters**:
- Base Unit: **null** (time-boxed separately)
- Complexity Multiplier: **null**
- Human Multiplier: **1.5×** AI time
- Time Box: **1-4 hours**

**Keywords**: spike, investigate, research, explore, poc, prototype

**Issue Types**: Spike

**Note**: Spikes are handled differently - they're time-boxed rather than complexity-scored.

**Examples**:
- "Investigate third-party API behavior for edge cases"
- "Prototype new architecture approach for microservices"
- "Research performance bottleneck in data processing pipeline"
- "Evaluate GraphQL vs REST for new API"

---

## Classification Logic

**IMPORTANT**: Classify based on **characteristics** first, using keywords only as supporting evidence. The nature of the work matters more than specific words used.

### Step 1: Check Issue Type (Strongest Signal)

```
if (issueType === "Bug") → classify as Bug Fix
if (issueType === "Spike") → classify as Spike
```

### Step 2: Analyze Characteristics (Primary Classification)

Look for these indicators in title and description:

#### Net-New Feature Indicators
- **Creating new files/components from scratch**
  - Signals: "new [component/service/module]", "build from scratch", "first [integration/implementation]"
  - Context: No existing code mentioned, no reference to current implementation
  - Examples: "new API endpoint", "build Stripe integration", "first GraphQL service"

#### Refactor/Hardening Indicators
- **Improving existing code WITHOUT changing behavior**
  - Signals: "existing", "current", "strengthen", "improve [existing thing]", "optimize", "type safety", "error handling"
  - Context: Mentions what already exists, focuses on quality/performance/safety
  - Examples: "strengthen existing validation", "improve current query patterns", "add type guards to existing functions"
  - **Key**: If "create" or "add" appears WITH "existing/current" → likely Refactor, not Net-New

#### Enhancement Indicators
- **Adding new capabilities to existing components**
  - Signals: "add [feature] to existing", "extend current", "support additional", references to existing code
  - Context: Building on top of what exists, following established patterns
  - Examples: "add pagination to existing search", "extend user profile", "support CSV export in reports"

#### Bug Fix Indicators
- **Fixing known problems**
  - Signals: "fix", "broken", "not working", "error", "incorrect behavior"
  - Context: Problem is defined, location is known
  - Examples: "fix validation error", "correct calculation", "resolve null pointer"

#### Spike Indicators
- **Research and exploration**
  - Signals: "investigate", "research", "explore", "evaluate", "prototype", "poc"
  - Context: Uncertain outcome, learning-focused
  - Examples: "investigate API behavior", "research performance", "evaluate GraphQL vs REST"

### Step 3: Keyword Check (Secondary Support)

Use keywords to **support** the characteristic analysis, not replace it:

```
// Refactor-strong keywords (high confidence)
if (matches: refactor, optimize, harden, strengthen, type safety, error handling)
  AND (mentions: existing, current, improve)
  → Refactor

// Bug Fix keywords
if (matches: fix, bug, broken, error, defect, incorrect)
  → Bug Fix

// Spike keywords
if (matches: spike, investigate, research, explore, poc, prototype)
  → Spike

// Enhancement keywords
if (matches: add, extend, enhance, support)
  AND (mentions: existing, current)
  AND NOT (mentions: new component/service/module from scratch)
  → Enhancement

// Net-New keywords (only if no existing code mentioned)
if (matches: new, create, build, implement)
  AND NOT (mentions: existing, current, improve)
  → Net-New

// Ambiguous case: "create" with existing code context
if (matches: create) AND (mentions: existing, current)
  → Likely Refactor or Enhancement, not Net-New
```

### Step 4: Default

```
if (no clear classification) → Enhancement (conservative default)
```

### Manual Override

Allow manual override with `--task-type-override` flag:
```
--task-type-override=refactor
--task-type-override=bug-fix
--task-type-override=enhancement
--task-type-override=net-new
--task-type-override=spike
```

---

## Classification Examples

### Example 1: Clear Bug Fix

**Title**: "Fix validation error on login form"
**Issue Type**: Bug
**Classification**: **Bug Fix** ✓
**Rationale**: Issue type is "Bug" + keywords: "fix", "error"

---

### Example 2: Ambiguous - Refactor vs Enhancement

**Title**: "Add type safety to user management module"
**Issue Type**: Task
**Keywords Found**: "add", "type"
**Classification**: **Refactor** ✓
**Rationale**: "type" keyword (refactor) takes precedence over "add" (enhancement) because type safety is about improving existing code, not adding new functionality

---

### Example 3: Net-New vs Enhancement

**Title**: "Add new dashboard widget for real-time metrics"
**Keywords Found**: "add", "new"
**Classification**: **Net-New** ✓
**Rationale**: "new" keyword indicates building from scratch

vs.

**Title**: "Add pagination to existing dashboard"
**Keywords Found**: "add", "existing"
**Classification**: **Enhancement** ✓
**Rationale**: "add" without "new", mentions "existing" → extending functionality

---

### Example 4: "Create" in Refactoring Context

**Title**: "Create type guards for existing validation functions"
**Keywords Found**: "create", "type", "existing", "validation"
**Classification**: **Refactor** ✓
**Rationale**:
- **Characteristic Analysis**: Mentions "existing" functions → improving existing code
- **Context**: Type guards = improving type safety, not adding new functionality
- **Keyword Priority**: "existing" + "type" (refactor signals) override "create" (net-new signal)

vs.

**Title**: "Create new validation service from scratch"
**Keywords Found**: "create", "new", "validation", "scratch"
**Classification**: **Net-New** ✓
**Rationale**:
- **Characteristic Analysis**: "new service" + "from scratch" → building something that doesn't exist
- **Context**: No reference to existing code
- **Keyword Priority**: "new" + "from scratch" clearly indicate net-new work

---

### Example 5: "Add" in Different Contexts

**Title**: "Add error handling to existing API endpoints"
**Keywords Found**: "add", "existing", "error handling"
**Classification**: **Refactor** ✓
**Rationale**: Adding error handling = improving existing code quality, not new functionality

vs.

**Title**: "Add new PDF export feature to reports"
**Keywords Found**: "add", "new", "feature"
**Classification**: **Net-New** ✓
**Rationale**: "new feature" = building something that doesn't exist yet

vs.

**Title**: "Add pagination to existing search results"
**Keywords Found**: "add", "existing", "search"
**Classification**: **Enhancement** ✓
**Rationale**: Adding capability (pagination) to existing component (search)

---

### Example 6: Spike

**Title**: "Investigate performance bottleneck in data processing"
**Keywords Found**: "investigate"
**Classification**: **Spike** ✓
**Rationale**: Investigation keyword + research-focused

---

## Impact on Estimates

Same raw complexity, different task types:

| Scenario | Raw Complexity | Task Type | Multiplier | Adjusted Complexity | Implementation Time (base unit) |
|----------|----------------|-----------|------------|---------------------|--------------------------------|
| A | 5.0 | Net-New | 1.0× | 5.0 | 5.0 × 30 = **150 min** |
| B | 5.0 | Enhancement | 0.75× | 3.75 | 3.75 × 22.5 = **84 min** |
| C | 5.0 | Refactor | 0.58× | 2.9 | 2.9 × 17.5 = **51 min** |
| D | 5.0 | Bug Fix | 0.42× | 2.1 | 2.1 × 12.5 = **26 min** |

**Impact**: A bug fix with complexity 5 takes **1/6th the time** of a net-new feature with the same complexity!

---

## Best Practices

1. **Start with issue type** - it's the strongest signal (Bug, Spike types are usually correct)

2. **Analyze characteristics first, keywords second**
   - Ask: "Does this code/component already exist?"
   - Ask: "Is this adding new functionality or improving existing quality?"
   - Ask: "Is behavior changing or staying the same?"

3. **Look for context clues**
   - "existing", "current" → likely Refactor or Enhancement, not Net-New
   - "new [component/service]", "from scratch" → likely Net-New
   - "to existing [thing]" → likely Enhancement or Refactor

4. **Keyword conflicts require context**
   - "create" + "existing" → probably Refactor
   - "create" + "new" → probably Net-New
   - "add" + "error handling" → probably Refactor
   - "add" + "new feature" → probably Net-New or Enhancement

5. **Consider the nature of work**
   - Type safety, validation, error handling → Refactor
   - New capabilities to existing components → Enhancement
   - Brand new components from scratch → Net-New

6. **When in doubt, ask** - use manual override if classification is unclear

7. **Document rationale** - explain why this task type was chosen, especially for ambiguous cases

8. **Validate with team** - classification affects estimates significantly (26 min vs 150 min for same complexity!)
