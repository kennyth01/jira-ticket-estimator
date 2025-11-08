# Workflow Phase Formulas

Complete formulas for calculating manual development time across all project types.

## Scale Factor

Base formula used across all complexity-scaled phases:

```
scaleFactor = adjustedComplexity / 5
```

This normalizes complexity to a scale factor where:
- Complexity 1 → scaleFactor = 0.2 (20% of base time)
- Complexity 5 → scaleFactor = 1.0 (100% of base time)
- Complexity 10 → scaleFactor = 2.0 (200% of base time)

## Phase 1: Planning & Design

**Scales with complexity**

```
planningTime = projectType.planning_design.base_minutes_at_complexity_5 × scaleFactor
```

**Base times by project type** (at complexity 5, scaleFactor = 1.0):

| Project Type | Base Minutes | Range (complexity 1-10) | Description |
|--------------|--------------|-------------------------|-------------|
| Monolithic | 90 min | 18-180 min | DB schema, API contracts, routing |
| Serverless | 120 min | 24-240 min | Event design, IAM, IaC templates |
| Frontend | 75 min | 15-150 min | Component architecture, state management |
| Full-Stack | 120 min | 24-240 min | Backend + frontend architecture |

**Example**: Monolithic with complexity 3.5
```
planningTime = 90 × (3.5 / 5) = 90 × 0.7 = 63 minutes
```

## Phase 2: Implementation

**Uses task-type-specific base units, scales with adjusted complexity**

```
implementationTime = adjustedComplexity × baseUnits[taskType]
```

**Base units by task type**:

| Task Type | Base Unit (minutes) | Rationale |
|-----------|---------------------|-----------|
| Net-New | 30 | Building from scratch, no reference code |
| Enhancement | 22.5 | Extending existing, has patterns to follow |
| Refactor | 17.5 | Improving existing code, behavior unchanged |
| Bug Fix | 12.5 | Localized change, known problem |
| Spike | null | Time-boxed separately (1-4 hours) |

**Example**: Bug fix with adjusted complexity 2.1
```
implementationTime = 2.1 × 12.5 = 26.25 minutes
```

**Example**: Net-new feature with adjusted complexity 6.5
```
implementationTime = 6.5 × 30 = 195 minutes (3.25 hours)
```

## Phase 3: Self Review

**Fixed time** (does not scale with complexity)

```
selfReviewTime = projectType.self_review.base_minutes
```

**Base time**: 30 minutes (all project types)

Self review happens before testing to catch obvious bugs, edge cases, and code quality issues.

**Example**: All project types
```
selfReviewTime = 30 minutes
```

## Phase 4: Testing

**Percentage of implementation time** (varies by project type)

```
testingTime = implementationTime × (testingPercentage / 100)
```

**Testing percentages by project type**:

| Project Type | Percentage | Rationale |
|--------------|------------|-----------|
| Monolithic | 40% | Unit + integration tests |
| Serverless | 35% | Unit + integration + local invoke |
| Frontend | 45% | Unit + integration + E2E (Playwright/Cypress) |
| Full-Stack | 50% | Backend + frontend + E2E tests |

**Example**: Frontend with implementation = 120 minutes
```
testingTime = 120 × 0.45 = 54 minutes
```

## Phase 5: Code Review & Revisions

**Scales with complexity**

```
codeReviewTime = projectType.code_review.base_minutes_at_complexity_5 × scaleFactor
```

**Base times by project type** (at complexity 5, scaleFactor = 1.0):

| Project Type | Base Minutes | Range (complexity 1-10) | Includes |
|--------------|--------------|-------------------------|----------|
| Monolithic | 45 min | 9-90 min | Peer review, addressing feedback |
| Serverless | 40 min | 8-80 min | Peer + security review |
| Frontend | 35 min | 7-70 min | Peer + accessibility review |
| Full-Stack | 60 min | 12-120 min | Backend + frontend review |

**Example**: Serverless with complexity 4.5
```
codeReviewTime = 40 × (4.5 / 5) = 40 × 0.9 = 36 minutes
```

## Phase 6: Deployment to Test

**Fixed time** (does not scale with complexity)

```
if (hasInfrastructureChanges) {
  deployTime = projectType.deployment_to_test.infrastructure_changes_minutes
} else {
  deployTime = projectType.deployment_to_test.base_minutes
}
```

**Deploy times by project type**:

| Project Type | Standard | With Infra Changes | Details |
|--------------|----------|-------------------|---------|
| Monolithic | 25 min | 50 min | Deploy to test environment, DB migrations |
| Serverless | 25 min | 60 min | CI/CD pipeline execution |
| Frontend | 25 min | 35 min | Build and deploy |
| Full-Stack | 25 min | 60 min | Backend + frontend deployment |
| Mobile | 25 min | 40 min | TestFlight/Internal Testing build |

**Example**: Full-stack with infrastructure changes
```
deployTime = 60 minutes
```

## Phase 7: Verification

**Scales with complexity**

```
verificationTime = projectType.verification.base_minutes_at_complexity_5 × scaleFactor
```

**Base times by project type** (at complexity 5, scaleFactor = 1.0):

| Project Type | Base Minutes | Range (complexity 1-10) | Details |
|--------------|--------------|-------------------------|---------|
| Monolithic | 20 min | 4-40 min | Smoke tests, manual verification |
| Serverless | 20 min | 4-40 min | CloudWatch logs, API testing |
| Frontend | 20 min | 4-40 min | Cross-browser testing, visual checks |
| Full-Stack | 20 min | 4-40 min | End-to-end verification |
| Mobile | 20 min | 4-40 min | Device verification, gesture testing |

**Example**: Frontend with complexity 3.5
```
verificationTime = 20 × (3.5 / 5) = 20 × 0.7 = 14 minutes
```

## Total Time Calculation

### Base Workflow Time

```
workflowTime = planningTime + implementationTime + selfReviewTime +
               testingTime + codeReviewTime + deployTime + verificationTime
```

### Overhead Activities (Optional)

Detected automatically based on keywords in ticket content:

```
overheadTime = sum(detected_overhead_activities)
```

Examples:
- Database Change Management: +20 min
- Cross-Team Coordination: +30 min
- Security Review: +30 min

### Manual Time Adjustments (Optional)

Extracted from explicit time patterns in ticket title/description:

```
manualAdjustmentTime = sum(extracted_time_values)
```

Supported patterns:
- `(+4h)`, `(4h)`, `(+4 hours)` → +4 hours
- `(+30m)`, `(30m)`, `(+30 minutes)` → +30 minutes
- `+2.5h` → +2.5 hours

### File Touch Overhead (Manual Workflow Only)

**Applies to**: Manual workflow only (AI can batch process files efficiently)

Accounts for the mechanical overhead of opening, reading, understanding, and modifying multiple files. This is **real overhead often forgotten** in estimates.

**Formula**:
```
if (file_count >= minimum_files_for_overhead) {
  complexityMultiplier = getComplexityMultiplier(adjustedComplexity)
  fileOverheadMinutes = file_count × base_time_per_file × complexityMultiplier
  fileOverheadMinutes = min(fileOverheadMinutes, maximum_overhead_minutes)
} else {
  fileOverheadMinutes = 0
}
```

**Configuration** (from heuristics.json):
- `base_time_per_file_minutes`: 2.5 minutes
- `minimum_files_for_overhead`: 20 files (no overhead below this)
- `maximum_overhead_minutes`: 300 minutes (5 hours cap)

**Complexity Multipliers**:
```
if (adjustedComplexity < 3.0) {
  multiplier = 0.6  // Low complexity (simple find/replace)
} else if (adjustedComplexity < 6.0) {
  multiplier = 1.0  // Medium complexity (moderate changes)
} else {
  multiplier = 1.5  // High complexity (architectural changes)
}
```

**Examples**:

**Example 1**: 75 files, complexity 4.0 (medium)
```
75 files >= 20 threshold ✓
complexityMultiplier = 1.0 (medium)
fileOverheadMinutes = 75 × 2.5 × 1.0 = 187.5 minutes (3.1 hours)
187.5 < 300 cap ✓
Final overhead: 187.5 minutes
```

**Example 2**: 120 files, complexity 7.5 (high)
```
120 files >= 20 threshold ✓
complexityMultiplier = 1.5 (high)
fileOverheadMinutes = 120 × 2.5 × 1.5 = 450 minutes
450 > 300 cap → capped at 300 minutes (5 hours)
Final overhead: 300 minutes
```

**Example 3**: 15 files, complexity 2.0 (low)
```
15 files < 20 threshold ✗
Final overhead: 0 minutes (below threshold)
```

**Example 4**: 50 files, complexity 2.5 (low)
```
50 files >= 20 threshold ✓
complexityMultiplier = 0.6 (low)
fileOverheadMinutes = 50 × 2.5 × 0.6 = 75 minutes (1.25 hours)
75 < 300 cap ✓
Final overhead: 75 minutes
```

**Important Notes**:
- File touch overhead is **added to the implementation phase** of manual workflow only
- AI-assisted workflow does NOT include this overhead (AI can batch process efficiently)
- Always count **unique files** (deduplicate across multiple searches)
- Include: source files, test files, config files, migration files
- This overhead captures: opening file, reading context, understanding dependencies, making change, saving

**Impact on Estimates**:
- 20-50 files: Adds ~0.8-2h to manual estimate
- 50-100 files: Adds ~2-4h to manual estimate
- 100+ files: Adds ~4-5h to manual estimate (capped)

**Common mistake**: Forgetting to count files results in **2-5 hour underestimate** for large refactors!

### Final Total Time

```
totalTime = workflowTime + fileOverheadTime + overheadTime + manualAdjustmentTime
```

**Important**:
- File touch overhead applies **only to manual workflow**
- Overhead activities and manual adjustments apply equally to both manual and AI-assisted workflows
- File overhead, overhead activities, and manual adjustments **cannot be accelerated by AI**

## Bucket Rounding

After calculating total time, round to nearest standardized bucket using threshold-based approach.

**Buckets** (hours): 0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36, 40

**Threshold formula**:
```
threshold = currentBucket + ((nextBucket - currentBucket) × 0.25)
```

**Threshold table**:

| Calculated Hours | Current Bucket | Threshold | Rounded Result |
|------------------|----------------|-----------|----------------|
| 0.2h | 0h | 0.25h | 0h (≤ threshold) |
| 0.3h | 0h | 0.25h | 1h (> threshold) |
| 1.2h | 1h | 1.25h | 1h (≤ threshold) |
| 1.3h | 1h | 1.25h | 2h (> threshold) |
| 2.2h | 2h | 2.25h | 2h (≤ threshold) |
| 2.4h | 2h | 2.25h | 3h (> threshold) |
| 3.2h | 3h | 3.25h | 3h (≤ threshold) |
| 3.3h | 3h | 3.25h | 4h (> threshold) |
| 4.4h | 4h | 4.5h | 4h (≤ threshold) |
| 5.0h | 4h | 4.5h | 6h (> threshold) |
| 12.9h | 12h | 13.0h | 12h (≤ threshold) |
| 13.5h | 12h | 13.0h | 16h (> threshold) |
| 20.8h | 20h | 21.0h | 20h (≤ threshold) |
| 22.0h | 20h | 21.0h | 24h (> threshold) |

**Rule**: If calculated total > threshold, jump to next bucket; otherwise, stay at current bucket.

## Complete Example: Bug Fix - Monolithic (XS)

**Inputs**:
- Project Type: Monolithic
- Task Type: Bug Fix
- Raw Complexity: 3.0/10
- Adjusted Complexity: 1.26/10 (3.0 × 0.42)
- Scale Factor: 0.252 (1.26 / 5)
- Infrastructure Changes: No

**Calculations**:

```
Planning & Design:
  90 × 0.252 = 22.68 minutes

Implementation:
  1.26 × 12.5 = 15.75 minutes

Self Review:
  30 minutes (fixed)

Testing:
  15.75 × 0.40 = 6.3 minutes

Code Review:
  45 × 0.252 = 11.34 minutes

Deployment to Test:
  25 minutes (no infra changes)

Verification:
  20 × 0.252 = 5.04 minutes

Total:
  22.68 + 15.75 + 30 + 6.3 + 11.34 + 25 + 5.04 = 116.11 minutes = 1.94 hours

Bucket Rounding:
  1.94h → current bucket = 1h, threshold = 1.25h
  1.94 > 1.25 → rounds to 2h

Final Estimate: 2 hours
```

## Complete Example: Enhancement - Full-Stack (L)

**Inputs**:
- Project Type: Full-Stack
- Task Type: Enhancement
- Raw Complexity: 8.5/10
- Adjusted Complexity: 6.38/10 (8.5 × 0.75)
- Scale Factor: 1.276 (6.38 / 5)
- Infrastructure Changes: Yes

**Calculations**:

```
Planning & Design:
  120 × 1.276 = 153.12 minutes

Implementation:
  6.38 × 22.5 = 143.55 minutes

Self Review:
  30 minutes (fixed)

Testing:
  143.55 × 0.50 = 71.78 minutes

Code Review:
  60 × 1.276 = 76.56 minutes

Deployment to Test:
  60 minutes (with infra changes)

Verification:
  20 × 1.276 = 25.52 minutes

Total:
  153.12 + 143.55 + 30 + 71.78 + 76.56 + 60 + 25.52 = 560.53 minutes = 9.34 hours

Bucket Rounding:
  9.34h → current bucket = 8h, threshold = 9.0h
  9.34 > 9.0 → rounds to 12h

Final Estimate: 12 hours (1.5 days)
```

## Complete Example with Overhead and Manual Adjustments

**Ticket**: "Add user authentication with database migration (+2h for manual security testing)"

**Inputs**:
- Project Type: Monolithic
- Task Type: Net-New Feature
- Raw Complexity: 7.0/10
- Adjusted Complexity: 7.0/10 (no task type adjustment for net-new)
- Scale Factor: 1.4 (7.0 / 5)
- Infrastructure Changes: No

**Workflow Calculations**:

```
Planning & Design:
  90 × 1.4 = 126 minutes

Implementation:
  7.0 × 30 = 210 minutes

Self Review:
  30 minutes (fixed)

Testing:
  210 × 0.40 = 84 minutes

Code Review:
  45 × 1.4 = 63 minutes

Deployment to Test:
  25 minutes (no infra changes)

Verification:
  20 × 1.4 = 28 minutes

Workflow Total:
  126 + 210 + 30 + 84 + 63 + 25 + 28 = 566 minutes = 9.43 hours
```

**Overhead Activities Detected**:

```
Database Change Management: +20 min (keyword: "database", "migration")

Overhead Total: 20 minutes = 0.33 hours
```

**Manual Time Adjustments Detected**:

```
Pattern: "(+2h for manual security testing)"
Extracted: +2 hours

Manual Adjustment Total: 2 hours
```

**Final Calculation**:

```
Total Time = 9.43h (workflow) + 0.33h (overhead) + 2.0h (adjustments)
Total Time = 11.76 hours

Bucket Rounding:
  11.76h → current bucket = 12h, threshold = 13.0h
  11.76 < 13.0 → stays at 12h

Final Estimate: 12 hours (1.5 days)
```

**Breakdown in Output**:

```
Manual Development Time: 12h
  - Workflow: 9.43h
  - Overhead: 0.33h (Database Change Management)
  - Manual Adjustments: 2h (manual security testing)

AI-Assisted Development Time: ~8h
  - Workflow: 5.1h (estimated 46% savings on workflow)
  - Overhead: 0.33h (same - cannot be accelerated)
  - Manual Adjustments: 2h (same - cannot be accelerated)
```

This example demonstrates how overhead activities and manual time adjustments combine to provide a complete, realistic estimate.
