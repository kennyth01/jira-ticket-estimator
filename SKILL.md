---
name: Jira Ticket Estimator
description: This skill should be used when estimating manual development time for Jira tickets. It provides T-shirt sizes, story points, and phase-by-phase time breakdowns based on task type classification, complexity scoring, and project architecture (monolithic/serverless/frontend/fullstack/mobile).
---

# Jira Ticket Estimator

Estimate manual development time for Jira tickets using a 6-phase workflow that mirrors real development processes.

## When to Use This Skill

Invoke when:
- Estimating a Jira ticket before work starts
- Sprint planning requires story point assignments
- Stakeholders need time estimates for features/bugs/refactors
- Comparing estimates across different project types

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

### 4. Score Complexity Factors

Score each factor on 1-10 scale:

1. **Scope Size**: Files, LOC, API changes
2. **Technical Complexity**: Algorithms, integrations
3. **Testing Requirements**: Coverage needs, test complexity
4. **Risk & Unknowns**: New tech, ambiguity, breaking changes
5. **Dependencies**: Blockers, coordination, impact radius

See `references/complexity-scoring-guide.md` for detailed scoring guide.

### 5. Calculate Estimates Using Python Script

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

Script outputs JSON with complete estimate breakdown including detected overhead activities.

### 6. Parse and Format Results

Extract from JSON output:
- Project type and task type classification
- T-shirt size (XS/S/M/L/XL)
- Story points (Fibonacci)
- Raw and adjusted complexity scores
- Phase-by-phase time breakdown
- Total time (calculated and rounded)

### 7. Present Estimate to User

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
| 6. Deploy to Test + Verification | X min | <infra changes: yes/no> |
| **Subtotal (workflow)** | **X.XXh** | Sum of 6 phases |

## Overhead Activities

*If any overhead activities detected:*

| Activity | Time | Reason |
|----------|------|--------|
| Database Change Management | +20 min | Create DBA ticket + Confluence doc |
| Security Review | +30 min | Submit review + address findings |
| **Total Overhead** | **+X min** | |

| **TOTAL (with overhead)** | **X.XXh** | |
| **TOTAL (rounded)** | **Xh** | Snapped to bucket |

*If no overheads: Show workflow total as final total*

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
4. If approved, execute following 5-phase workflow
5. Track actual vs estimated time for calibration
```

### 8. Optional: Update Jira

If `--update-jira` flag provided:

```bash
mcp__atlassian_update_jira_issue --ticket-id=<ticket-id> --story-points=<points>
```

## Project Types

Five project types with customized workflow phases:

### Monolithic (Laravel, Rails, Django)
- Planning: 90 min @ complexity 5
- Testing: 40% of implementation
- Deploy: 30 min (60 min with infra)

### Serverless (AWS Lambda, Cloud Functions)
- Planning: 120 min @ complexity 5 (more for IaC)
- Testing: 35% of implementation
- Deploy: 45 min (90 min with infra)

### Frontend (React, Vue, Angular)
- Planning: 75 min @ complexity 5
- Testing: 45% of implementation (includes E2E)
- Deploy: 25 min (45 min with infra)

### Full-Stack (Backend + Frontend)
- Planning: 120 min @ complexity 5
- Testing: 50% of implementation (most comprehensive)
- Deploy: 45 min (90 min with infra)

### Mobile (Android, iOS, React Native, Flutter)
- Planning: 100 min @ complexity 5 (screen flows, offline support)
- Testing: 50% of implementation (device testing critical)
- Deploy: 35 min (50 min with infra) - TestFlight/Internal Testing

All phase times scale with complexity. See `references/workflow-formulas.md` for complete formulas.

## The 6-Phase Manual Workflow

Estimates follow real development phases:

1. **Planning & Design** - Architecture, DB schema, API contracts
2. **Implementation** - Core development work
3. **Self Review** - Review own code for bugs, edge cases, code quality
4. **Testing** - Unit, integration, E2E tests
5. **Code Review & Revisions** - Peer review, addressing feedback
6. **Deployment to Test + Verification** - Deploy, smoke tests, verification

## Configuration

All parameters stored in `heuristics.json`:

### Customizable per Project Type
- Workflow phase base times
- Testing percentages
- Deploy times with/without infrastructure changes

### Overhead Activities
- Database change management (+20 min by default)
- Security review (disabled by default)
- Legal/compliance review (disabled by default)
- Documentation update (disabled by default)
- Custom overheads for your team's processes

See `references/overhead-activities.md` for configuration guide.

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
| 6. Deploy to Test + Verification | 30 min | Deploy, smoke test |
| **Total (calculated)** | **1.93h** | |
| **Total (rounded)** | **2h** | Snapped to bucket |
```

7. Track in backlog for calibration

## Notes

- **Estimates are predictive** - refine after reconnaissance
- **Overhead activities are configurable** - enable/disable based on your processes
- **Track actual vs estimated** by phase and overhead for calibration
- **Adjust `heuristics.json`** based on team historical data
- **Use `--update-jira`** to persist story points automatically
- **Open-source ready** - all team-specific configs in heuristics.json