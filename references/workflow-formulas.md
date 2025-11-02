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

```
totalTime = planningTime + implementationTime + selfReviewTime +
            testingTime + codeReviewTime + deployTime + verificationTime
```

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
