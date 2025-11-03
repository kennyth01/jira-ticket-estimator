---
name: Jira Ticket Estimator
description: This skill should be used when estimating development time for Jira tickets. It provides both manual and AI-assisted estimates with T-shirt sizes, story points, and phase-by-phase time breakdowns based on task type classification, complexity scoring, and project architecture (monolithic/serverless/frontend/fullstack/mobile).
---

# Jira Ticket Estimator

Estimate manual and AI-assisted development time for Jira tickets using a 7-phase manual workflow and 7-phase AI-assisted workflow that mirror real development processes.

## When to Use This Skill

Invoke when:
- Estimating a Jira ticket before work starts
- Sprint planning requires story point assignments
- Stakeholders need time estimates for features/bugs/refactors
- Comparing estimates across different project types
- Understanding time savings with AI-assisted development

## Inputs

**Required** (one of):
- Jira ticket ID/URL (e.g., PROJ-123)
- Free-form description of work
- User story with acceptance criteria

**Optional Flags**:
- `--project-type`: monolithic|serverless|frontend|fullstack|mobile (default: monolithic)
- `--task-type`: Manual override for task classification
- `--team-velocity`: Velocity factor for story points (default: 1.0)
- `--has-infrastructure-changes`: Flag for infrastructure changes

## Estimation Workflow

### 1. Fetch Ticket Details

Use Atlassian MCP tools to retrieve ticket information:

```bash
mcp__atlassian_fetch_jira_ticket --ticket-id=<ticket-id>
```

Extract: title, description, acceptance criteria, issue type, labels.

If MCP unavailable, prompt user for ticket details.

### 2. Classify Task Type

Classify into one of 5 types using keywords and issue type:
- **Bug Fix**: Keywords: fix, bug, error | Issue Type: Bug
- **Refactor**: Keywords: refactor, improve, optimize, harden
- **Enhancement**: Keywords: add, extend, enhance (without "new")
- **Net-New**: Keywords: new, create, build, implement
- **Spike**: Keywords: investigate, research, spike

See `references/task-type-classification.md` for complete classification guide.

### 3. Repository Reconnaissance

Scan codebase to understand scope:
- Use Grep/Glob to find related files
- Count files likely to be modified
- Estimate LOC changes
- Identify integration points
- Check test coverage in affected areas

### 4. Detect Manual Time Adjustments

Scan ticket title and description for explicit time additions:

**Supported patterns:**
- `(+4h)`, `(4h)`, `(+4 hours)` - Parentheses format (recommended)
- `+4h`, `+4 hours` - Plus prefix format
- `(+30m)`, `(30m)`, `(+30 minutes)` - Minutes notation
- `+2.5h`, `+1.5 hours` - Decimal values supported

**Examples:**
- "ensure qa automation run is not affected (+4h)"
- "manual testing required +2h"
- "coordinate with DevOps team (30m)"

These adjustments are added on top of calculated estimates and overhead activities.

### 5. Score Complexity Factors

Score each factor on 1-10 scale:

1. **Scope Size**: Files, LOC, API changes
2. **Technical Complexity**: Algorithms, integrations
3. **Testing Requirements**: Coverage needs, test complexity
4. **Risk & Unknowns**: New tech, ambiguity, breaking changes
5. **Dependencies**: Blockers, coordination, impact radius

See `references/complexity-scoring-guide.md` for detailed scoring guide.

### 6. Calculate Estimates Using Python Script

Execute the estimation script with gathered inputs:

```bash
cd .claude/skills/jira-ticket-estimator

python3 scripts/estimator.py <<EOF
{
  "title": "<ticket_title>",
  "description": "<ticket_description>",
  "project_type": "<monolithic|serverless|frontend|fullstack>",
  "issue_type": "<Bug|Story|Task|Spike>",
  "complexity_scores": {
    "scope_size": <1-10>,
    "technical_complexity": <1-10>,
    "testing_requirements": <1-10>,
    "risk_and_unknowns": <1-10>,
    "dependencies": <1-10>
  },
  "has_infrastructure_changes": <true|false>
}
EOF
```

Or use Python directly:

```python
from scripts.estimator import TicketEstimator
import json

estimator = TicketEstimator('heuristics.json')
result = estimator.estimate_ticket(
    title="<ticket_title>",
    description="<ticket_description>",
    project_type="<project_type>",
    issue_type="<issue_type>",
    complexity_scores={
        'scope_size': <score>,
        'technical_complexity': <score>,
        'testing_requirements': <score>,
        'risk_and_unknowns': <score>,
        'dependencies': <score>
    },
    has_infrastructure_changes=<bool>
)

print(json.dumps(result, indent=2))
```

Script outputs JSON with complete estimate breakdown including both manual and AI-assisted workflows, plus detected overhead activities.

### 7. Parse and Format Results

Extract from JSON output:
- Project type and task type classification
- T-shirt size (XS/S/M/L/XL)
- Story points (Fibonacci)
- Raw and adjusted complexity scores
- Manual workflow phase-by-phase time breakdown
- AI-assisted workflow phase-by-phase time breakdown
- Detected overhead activities
- Detected manual time adjustments
- Time savings comparison
- Total time (calculated and rounded)

### 8. Present Estimate to User

Format output as markdown table:

```markdown
# Estimate: <TICKET-ID>

**Project Type**: <type>
**Task Type**: <type> (<classification rationale>)
**T-Shirt Size**: <size>
**Story Points**: <points>
**Complexity**: <raw>/10 → <adjusted>/10 (scale factor: <sf>)

## Manual Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. Planning & Design | X min | <description> |
| 2. Implementation | X min | <task-type base unit> × <complexity> |
| 3. Self Review | 30 min | Review own code before testing |
| 4. Testing | X min | <percentage>% of implementation |
| 5. Code Review & Revisions | X min | <description> |
| 6. Deployment to Test | X min | Deploy to test environment |
| 7. Verification | X min | Smoke tests, verification (scales with complexity) |
| **TOTAL (calculated)** | **X.XXh** | |
| **TOTAL (rounded)** | **Xh** | Snapped to bucket |

## AI-Assisted Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. AI Planning | X min | AI generates architecture, API contracts (X% savings) |
| 2. AI Implementation | X min | AI generates code, tests (X% savings) |
| 3. AI Review | X min | AI reviews for bugs, improvements |
| 4. Human Review & Testing | X min | Validate AI output, run tests |
| 5. Iterations & Vibe Coding | X min | Fix AI mistakes, refine prompts |
| 6. Deploy to Test | X min | Deploy to test environment |
| 7. Test Verification | X min | Smoke tests, E2E verification |
| **TOTAL (calculated)** | **X.XXh** | |
| **TOTAL (rounded)** | **Xh** | Snapped to bucket |

## Overhead Activities

*Overhead activities apply to BOTH manual and AI-assisted workflows*

*If any overhead activities detected:*

| Activity | Time | Reason |
|----------|------|--------|
| Database Change Management | +20 min | Create DBA ticket + Confluence doc |
| Cross-Team Coordination | +30 min | Coordinate with ops/infrastructure team |
| Security Review | +30 min | Submit review + address findings |
| **Total Overhead** | **+X min (X.XXh)** | |

*If no overheads detected: Skip this section*

## Manual Time Adjustments

*Manual time adjustments apply to BOTH manual and AI-assisted workflows*

*If manual time adjustments detected in ticket:*

| Adjustment | Time | Source |
|------------|------|--------|
| Manual time addition | +4h | Title: "ensure qa automation run is not affected (+4h)" |
| Additional testing | +30m | Description: "manual regression testing +30m" |
| **Total Adjustments** | **+X.XXh** | |

*If no manual adjustments detected: Skip this section*

## Time Savings

- **Manual Development**: X.XXh (workflow) + X.XXh (overhead) + X.XXh (manual adjustments) = X.XXh → Xh rounded
- **AI-Assisted Development**: X.XXh (workflow) + X.XXh (overhead) + X.XXh (manual adjustments) = X.XXh → Xh rounded
- **Time Savings**: X.XXh (XX.X% faster)

*Note: Overhead time and manual adjustments are the same for both workflows. Only the core workflow phases benefit from AI acceleration.*

## Complexity Scores

| Factor | Score | Rationale |
|--------|-------|-----------|
| Scope Size | X/10 | <why> |
| Technical Complexity | X/10 | <why> |
| Testing Requirements | X/10 | <why> |
| Risk & Unknowns | X/10 | <why> |
| Dependencies | X/10 | <why> |

## Assumptions

1. <assumption 1>
2. <assumption 2>
3. <assumption 3>

## Confidence Level

**<High|Medium|Low>** - <rationale>

## Next Steps

1. Review estimate with stakeholders
2. Validate complexity scores and task type
3. Approval gate: proceed, modify scope, or reject
4. Choose development approach (manual vs AI-assisted)
5. Track actual vs estimated time for calibration
```

### 9. Optional: Update Jira

If `--update-jira` flag provided:

```bash
mcp__atlassian_update_jira_issue --ticket-id=<ticket-id> --story-points=<points>
```

## Project Types

Five project types with customized workflow phases:

### Monolithic (Laravel, Rails, Django)
- Planning: 90 min @ complexity 5
- Testing: 40% of implementation
- Deployment to Test: 25 min (50 min with infra)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Serverless (AWS Lambda, Cloud Functions)
- Planning: 120 min @ complexity 5 (more for IaC)
- Testing: 35% of implementation
- Deployment to Test: 25 min (60 min with infra)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Frontend (React, Vue, Angular)
- Planning: 75 min @ complexity 5
- Testing: 45% of implementation (includes E2E)
- Deployment to Test: 25 min (35 min with infra)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Full-Stack (Backend + Frontend)
- Planning: 120 min @ complexity 5
- Testing: 50% of implementation (most comprehensive)
- Deployment to Test: 25 min (60 min with infra)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Mobile (Android, iOS, React Native, Flutter)
- Planning: 100 min @ complexity 5 (screen flows, offline support)
- Testing: 50% of implementation (device testing critical)
- Deployment to Test: 25 min (40 min with infra) - TestFlight/Internal Testing
- Verification: 20 min @ complexity 5 (scales with complexity)

All phase times scale with complexity. See `references/workflow-formulas.md` for complete formulas.

## The 7-Phase Manual Workflow

Estimates follow real development phases:

1. **Planning & Design** - Architecture, DB schema, API contracts
2. **Implementation** - Core development work
3. **Self Review** - Review own code for bugs, edge cases, code quality
4. **Testing** - Unit, integration, E2E tests
5. **Code Review & Revisions** - Peer review, addressing feedback
6. **Deployment to Test** - Deploy to test environment (fixed time, infra-aware)
7. **Verification** - Smoke tests, verification (scales with complexity)

## The 7-Phase AI-Assisted Workflow

AI-assisted development follows these phases:

1. **AI Planning** - AI generates architecture, DB schema, API contracts (60-70% time savings)
2. **AI Implementation** - AI generates code, controllers, models, tests (60-70% time savings)
3. **AI Review** - AI reviews generated code for bugs and improvements
4. **Human Review & Testing** - Developer validates AI output and runs tests
5. **Iterations & Vibe Coding** - Fix AI mistakes, regenerate code, refine prompts
6. **Deploy to Test** - Deploy to test environment
7. **Test Verification** - Smoke tests, E2E verification, validation

Typical time savings: 40-50% compared to manual development.

## Configuration

All parameters stored in `heuristics.json`:

### Customizable per Project Type
- Workflow phase base times (manual and AI-assisted)
- Testing percentages
- Deploy times with/without infrastructure changes
- AI time savings percentages

### Overhead Activities
- Database change management (+20 min by default)
- Cross-team coordination (+30 min by default)
- Security review (disabled by default)
- Legal/compliance review (disabled by default)
- Documentation update (disabled by default)
- Custom overheads for your team's processes

See `references/overhead-activities.md` for configuration guide.

### Manual Time Adjustments
- Automatic detection of explicit time additions in ticket content
- Supports patterns: `(+4h)`, `+2h`, `(30m)`, `+15 minutes`
- Supports hours and minutes notation
- Supports decimal values: `+2.5h`
- All detected adjustments are summed and added to final estimate
- Can be disabled by setting `"enabled": false` in heuristics.json

### Global Settings
- Task type definitions and keywords
- Complexity factor scoring guides
- Complexity weights by task type
- T-shirt sizing ranges
- Story points mapping
- Bucket rounding thresholds

### Calibration

To customize for your team:
1. Start with defaults (monolithic)
2. Track estimated vs actual for 10-20 tickets
3. Adjust phase base times in `heuristics.json`
4. Recalibrate quarterly

Example adjustment:
```json
{
  "monolithic": {
    "workflow_phases": {
      "planning_design": {
        "base_minutes_at_complexity_5": 120
      }
    }
  }
}
```

## Bundled Resources

- `heuristics.json` - Complete estimation configuration
- `scripts/estimator.py` - Python calculation engine
- `references/task-type-classification.md` - Detailed task type guide
- `references/complexity-scoring-guide.md` - Factor-by-factor scoring guide
- `references/workflow-formulas.md` - Complete formulas and examples
- `references/overhead-activities.md` - Project-specific overhead configuration guide

## Example Usage

**User**: "Estimate LOOM-4156 for our Laravel monolith"

**Agent**:
1. Fetch ticket via MCP
2. Classify as "Bug Fix" (keywords: "fix", "error")
3. Scan repository - find LoginController.php
4. Score complexity: Scope=2, Technical=2, Testing=4, Risk=2, Dependencies=3
5. Execute estimator script
6. Present formatted estimate:

```markdown
# Estimate: LOOM-4156

**Project Type**: Monolithic Application
**Task Type**: Bug Fix (keywords: "fix", "validation", "error")
**T-Shirt Size**: XS
**Story Points**: 1
**Complexity**: 3.0/10 → 1.26/10 (scale factor: 0.252)

## Manual Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. Planning & Design | 23 min | Architecture review, edge cases |
| 2. Implementation | 16 min | Fix validation logic |
| 3. Self Review | 30 min | Review own code before testing |
| 4. Testing | 6 min | Unit tests for validation |
| 5. Code Review & Revisions | 11 min | Peer review |
| 6. Deployment to Test | 25 min | Deploy to test environment |
| 7. Verification | 5 min | Smoke test, verify fix |
| **Total (calculated)** | **1.93h** | |
| **Total (rounded)** | **2h** | Snapped to bucket |

## AI-Assisted Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. AI Planning | 7 min | AI generates fix approach (70% savings) |
| 2. AI Implementation | 6 min | AI generates validation fix (65% savings) |
| 3. AI Review | 5 min | AI reviews for edge cases |
| 4. Human Review & Testing | 8 min | Validate fix, run tests |
| 5. Iterations & Vibe Coding | 3 min | Refine if needed |
| 6. Deploy to Test | 25 min | Deploy to test environment |
| 7. Test Verification | 10 min | Verify fix works |
| **Total (calculated)** | **1.15h** | |
| **Total (rounded)** | **1h** | Snapped to bucket |

## Time Savings

- **Manual Development**: 1.93h → 2h rounded
- **AI-Assisted Development**: 1.15h → 1h rounded
- **Time Savings**: 0.78h (40% faster)
```

7. Track in backlog for calibration

## Notes

- **Estimates are predictive** - refine after reconnaissance
- **Both workflows calculated automatically** - choose based on your development approach
- **AI-assisted estimates assume**: Effective prompt engineering, experienced with AI tools, quality review process
- **Overhead activities are configurable** - enable/disable based on your processes
- **Manual time adjustments detected automatically** - use `(+Xh)` or `+Xh` format in ticket content
- **Track actual vs estimated** by phase, overhead, and adjustments for calibration
- **Adjust `heuristics.json`** based on team historical data
- **Use `--update-jira`** to persist story points automatically
- **Open-source ready** - all team-specific configs in heuristics.json
