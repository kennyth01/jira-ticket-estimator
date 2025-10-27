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

### Step 1: Check Issue Type

```
if (issueType === "Bug") → classify as Bug Fix
if (issueType === "Spike") → classify as Spike
```

### Step 2: Check Keywords in Title and Description

Scan title and description (case-insensitive) for keywords:

```
// Bug Fix
if (matches: fix, bug, defect, issue, broken, error) → Bug Fix

// Refactor
if (matches: refactor, improve, optimize, harden, strengthen, type, validate) → Refactor

// Enhancement
if (matches: add, extend, enhance, support) AND NOT matches: new → Enhancement

// Net-New
if (matches: new, create, build, implement) → Net-New

// Spike
if (matches: spike, investigate, research, explore, poc, prototype) → Spike
```

### Step 3: Default

```
if (no keywords matched) → Enhancement (conservative default)
```

### Manual Override

Allow manual override with `--task-type` flag:
```
--task-type=refactor
--task-type=bug-fix
--task-type=enhancement
--task-type=net-new
--task-type=spike
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

### Example 4: Spike

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

1. **Start with issue type** - it's the strongest signal
2. **Look for multiple keywords** - more matches = higher confidence
3. **Consider context** - "add type safety" is refactoring, not enhancement
4. **When in doubt, ask** - use manual override if classification is unclear
5. **Document rationale** - explain why this task type was chosen
6. **Validate with team** - classification affects estimates significantly
