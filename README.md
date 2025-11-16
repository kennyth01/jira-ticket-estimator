# Jira Ticket Estimator

A Claude Code skill for estimating manual and AI-assisted development time for Jira tickets. Provides T-shirt sizes, story points, and phase-by-phase time breakdowns based on task type classification, complexity scoring, and project architecture.

## Features

- **Dual Workflow Estimation**: Get both manual and AI-assisted development time estimates
- **7-Phase Manual Workflow**: Planning & Design → Implementation → Self Review → Testing → Code Review & Revisions → Deployment to Test → Verification
- **7-Phase AI-Assisted Workflow**: AI Planning → AI Implementation → AI Review → Human Review & Testing → Iterations & Vibe Coding → Deploy to Test → Test Verification
- **6 Project Types**: Monolithic, Serverless, Frontend, Full-Stack, Mobile (iOS/Android/React Native/Flutter), Test Automation (Serenity BDD/Playwright/Cypress)
- **Automatic Task Classification**: Net-New, Enhancement, Refactor, Bug Fix, Spike
- **Complexity-Based Scaling**: Implementation time scales with adjusted complexity scores
- **File Touch Overhead**: Realistic time estimates for multi-file refactors (manual development only)
- **Overhead Activities**: Automatic detection of database changes, security reviews, and custom processes
- **Manual Time Adjustments**: Automatic detection of explicit time additions in ticket content (e.g., `+4h`, `(30m)`)
- **T-Shirt Sizing & Story Points**: XS, S, M, L, XL mapped to Fibonacci story points
- **Smart Bucket Rounding**: Rounds to standardized time buckets (1h, 2h, 3h, 4h, 6h, 8h, 12h, 16h, 20h, etc.)

## Installation

### Prerequisites

- **Claude Code** installed and configured
- **Python 3** (for the estimation calculation engine)
- **Git** (for cloning the skill repository)

### Option 1: Install Globally (All Projects)

Install the skill globally to use it across all your projects:

```bash
# Navigate to global skills directory
cd ~/.claude/skills/

# Clone the skill repository
git clone https://github.com/kennyth01/jira-ticket-estimator.git

# Verify installation
ls -la ~/.claude/skills/jira-ticket-estimator
```

### Option 2: Install Per-Project (Project-Specific)

Install the skill for a specific project only:

```bash
# Navigate to your project
cd /path/to/your/project

# Create skills directory if it doesn't exist
mkdir -p .claude/skills

# Clone the skill repository
cd .claude/skills
git clone https://github.com/kennyth01/jira-ticket-estimator.git

# Verify installation
ls -la .claude/skills/jira-ticket-estimator
```

### Option 3: Install from Local Clone

If you've already cloned or downloaded the skill:

```bash
# For global installation
cp -r /path/to/jira-ticket-estimator ~/.claude/skills/

# For project-specific installation
cp -r /path/to/jira-ticket-estimator /path/to/project/.claude/skills/
```

### Verify Installation

Start Claude Code and test the skill:

```bash
# Start Claude Code in your project
claude

# In Claude Code, ask:
# "Estimate this ticket: Add user authentication to the app"
```

If the skill is installed correctly, I'll automatically use it to provide detailed time estimates.

### Optional: Atlassian MCP Integration

For automatic Jira ticket fetching, install the Atlassian MCP server:

```bash
# Install via MCP
# Follow Atlassian MCP documentation for setup
```

Without MCP, you can still use the skill by providing ticket details manually.

## Quick Start

### Basic Usage

**Estimate a Jira ticket:**
```
Estimate PROJ-123 for our Laravel monolith
```

**Estimate from description:**
```
Estimate this ticket: Add OAuth authentication with role-based permissions.
Project type: fullstack
```

**Estimate mobile ticket:**
```
Estimate ticket for iOS app: Implement offline photo sync with background upload
Project type: mobile
```

### How It Works

1. **Fetch Ticket Details** - Retrieves ticket information via Atlassian MCP (or prompts you)
2. **Classify Task Type** - Analyzes keywords to classify as Bug Fix, Refactor, Enhancement, Net-New, or Spike
3. **Detect Manual Time Adjustments** - Scans for explicit time additions like `(+4h)` or `+30m`
4. **Repository Reconnaissance** - Scans codebase to understand scope (files, LOC, integration points)
5. **Score Complexity** - Evaluates 5 factors: Scope Size, Technical Complexity, Testing Requirements, Risk & Unknowns, Dependencies
6. **Calculate File Touch Overhead** - Adds realistic time for touching many files (manual development only)
7. **Calculate Estimates** - Uses Python calculation engine with your project configuration
8. **Present Results** - Shows both manual and AI-assisted estimates with phase breakdowns, overhead activities, and file touch overhead

## Project Types

### Monolithic (Laravel, Rails, Django)
- Best for: Traditional MVC applications with integrated databases
- Planning: 90 min @ complexity 5
- Testing: 40% of implementation time
- Deployment to Test: 25 min (50 min with infrastructure changes)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Serverless (AWS Lambda, Cloud Functions)
- Best for: Event-driven architectures with cloud functions
- Planning: 120 min @ complexity 5 (includes IaC planning)
- Testing: 35% of implementation time
- Deployment to Test: 25 min (60 min with infrastructure changes)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Frontend (React, Vue, Angular)
- Best for: Single-page applications and UI components
- Planning: 75 min @ complexity 5
- Testing: 45% of implementation time (includes E2E)
- Deployment to Test: 25 min (35 min with infrastructure changes)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Full-Stack (Backend + Frontend)
- Best for: Features spanning both backend and frontend
- Planning: 120 min @ complexity 5
- Testing: 50% of implementation time (most comprehensive)
- Deployment to Test: 25 min (60 min with infrastructure changes)
- Verification: 20 min @ complexity 5 (scales with complexity)

### Mobile (iOS, Android, React Native, Flutter)
- Best for: Native and cross-platform mobile applications
- Planning: 100 min @ complexity 5 (screen flows, offline support)
- Testing: 50% of implementation time (device testing critical)
- Deployment to Test: 25 min (40 min with infrastructure changes) - TestFlight/Internal Testing
- Verification: 20 min @ complexity 5 (scales with complexity)

### Test Automation (Serenity BDD, Playwright, Cypress)
- Best for: Test automation development, QA automation, E2E test suites
- **Custom 7-Phase Workflow**: Analysis & Test Planning → Environment & Framework Setup → Page Objects & Locators → Step Implementations & Business Logic → Step Definitions & Gherkin Integration → Testing & Evidence Collection → Integration & Documentation
- Phase 1 - Analysis & Test Planning: 145 min @ complexity 5 (test scenario design, flow coverage planning)
- Phase 2 - Environment Setup: 63 min @ complexity 5 (test environment config, framework dependencies)
- Phase 3 - Page Objects & Locators: 199 min @ complexity 5 (locator identification, element mappings)
- Phase 4 - Step Implementations: Task-type based (test steps, validation logic, assertions)
- Phase 5 - Gherkin Integration: 136 min @ complexity 5 (wire steps to implementations)
- Phase 6 - Testing & Evidence: 72 min @ complexity 5 (test execution, screenshot capture)
- Phase 7 - Documentation: 54 min @ complexity 5 (CI/CD integration, reporting)
- **AI-Assisted**: 45% time savings (AI generates page objects, steps, Gherkin wiring)
- **Common Overhead**: Regression Assurance (+45 min) for validation across multiple flows

## Complexity Factors

Each ticket is scored on 5 factors (1-10 scale):

1. **Scope Size** - Number of files, LOC, API changes
2. **Technical Complexity** - Algorithms, integrations, new technologies
3. **Testing Requirements** - Test coverage needs, test complexity
4. **Risk & Unknowns** - Ambiguity, breaking changes, new patterns
5. **Dependencies** - Blockers, coordination needs, impact radius

See `references/complexity-scoring-guide.md` for detailed scoring guide.

## Task Types

### Net-New Feature (45 min/complexity point)
Building something entirely new without reference code.
- Keywords: new, create, build, implement
- Complexity Multiplier: 1.0x (no adjustment)

### Enhancement (34 min/complexity point)
Extending existing functionality with patterns to follow.
- Keywords: add, extend, enhance (without "new")
- Complexity Multiplier: 0.75x

### Refactor (26 min/complexity point)
Improving existing code without changing behavior.
- Keywords: refactor, improve, optimize, harden
- Complexity Multiplier: 0.58x

### Bug Fix (19 min/complexity point)
Localized changes to fix known problems.
- Keywords: fix, bug, error
- Issue Type: Bug
- Complexity Multiplier: 0.42x

### Spike (time-boxed separately)
Research and investigation tasks.
- Keywords: investigate, research, spike
- Time-boxed: 1-4 hours

See `references/task-type-classification.md` for complete classification guide.

## Example Output

```
# Estimate: PROJ-4156

**Project Type**: Monolithic Application
**Task Type**: Enhancement (keywords: "add", "extend")
**T-Shirt Size**: M
**Story Points**: 5
**Complexity**: 6.2/10 → 4.65/10 adjusted (scale factor: 0.93)

## Manual Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. Planning & Design | 84 min | Architecture review, DB schema, API design |
| 2. Implementation | 209 min | Core development work |
| 3. Self Review | 30 min | Review own code before testing |
| 4. Testing | 84 min | Unit, integration tests |
| 5. Code Review & Revisions | 42 min | Peer review, address feedback |
| 6. Deployment to Test | 25 min | Deploy to test environment |
| 7. Verification | 19 min | Smoke tests, verification |
| **Total (calculated)** | **8.22h** | |
| **Total (rounded)** | **8h** | Snapped to bucket |

## AI-Assisted Development Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| 1. AI Planning | 25 min | AI generates architecture, API contracts (70% savings) |
| 2. AI Implementation | 73 min | AI generates code, tests (65% savings) |
| 3. AI Review | 12 min | AI reviews for bugs, improvements |
| 4. Human Review & Testing | 80 min | Validate AI output, run tests |
| 5. Iterations & Vibe Coding | 23 min | Fix AI mistakes, refine prompts |
| 6. Deploy to Test | 60 min | Deploy to test environment |
| 7. Test Verification | 20 min | Smoke tests, E2E verification |
| **Total (calculated)** | **4.88h** | |
| **Total (rounded)** | **6h** | Snapped to bucket |

## Overhead Activities

*Overhead activities apply to both manual and AI-assisted workflows*

| Activity | Time | Reason |
|----------|------|--------|
| *No overhead detected in this example* | - | - |

## Manual Time Adjustments

*Manual time adjustments apply to both manual and AI-assisted workflows*

| Adjustment | Time | Source |
|------------|------|--------|
| *No manual adjustments detected in this example* | - | - |

## Time Savings

- Manual Development: 8.22h (workflow) + 0h (overhead) + 0h (adjustments) = 8.22h → 8h rounded
- AI-Assisted Development: 4.88h (workflow) + 0h (overhead) + 0h (adjustments) = 4.88h → 6h rounded
- Time Savings: 3.34h (40.6% faster)

*Note: Overhead activities and manual adjustments are added to both workflow totals and cannot be accelerated by AI*

## Complexity Scores

| Factor | Score | Rationale |
|--------|-------|-----------|
| Scope Size | 6/10 | 8-10 files, ~200 LOC changes |
| Technical Complexity | 7/10 | OAuth integration, token management |
| Testing Requirements | 6/10 | Auth flow testing, integration tests |
| Risk & Unknowns | 5/10 | Standard OAuth pattern |
| Dependencies | 7/10 | Depends on user service, auth library |

## Assumptions

1. OAuth library already exists in project dependencies
2. User table supports role-based permissions
3. Test environment has OAuth test credentials configured

## Confidence Level

**Medium** - Standard OAuth implementation but coordination with identity provider may add time
```

## Overhead Activities

The skill automatically detects project-specific overhead processes:

### Enabled by Default

**Database Change Management** (+20 min)
- Detected by keywords: migration, database, table, schema, sql
- Process: Create DBA ticket, execute on test/prod, document

**Cross-Team Coordination** (+30 min)
- Detected by keywords: devops, ops team, infrastructure team, collab with, coordinate with, deployment process
- Process: Create coordination tickets, discuss with other teams, explain changes

**Regression Assurance & Validation** (+45 min) - For Test Automation Projects
- Detected by keywords: regression, test automation, serenity, automation test, e2e test, test suite, playwright, cypress, flows, validation
- Process: Execute regression tests across affected flows, validate OTP/auth paths, collect evidence, stabilize flaky tests
- Applies to: test_automation project type only

### Disabled by Default (enable in heuristics.json)

**Security Review** (+30 min)
- Keywords: security, auth, authentication, credential, token

**Legal/Compliance Review** (+45 min)
- Keywords: privacy, gdpr, ccpa, consent, pii

**Documentation Update** (+15 min)
- Keywords: api change, breaking change, public api

See `references/overhead-activities.md` for complete configuration guide.

## Manual Time Adjustments

Sometimes tickets include explicit time requirements that can't be captured by the standard workflow. The skill automatically detects and applies these manual time additions.

### Supported Formats

**Hours notation:**
- `(+4h)`, `(4h)`, `(+4 hours)` - Parentheses format (recommended)
- `+4h`, `+4 hours` - Plus prefix format
- `+2.5h`, `+1.5 hours` - Decimal values supported

**Minutes notation:**
- `(+30m)`, `(30m)`, `(+30 minutes)` - Parentheses format
- `+30m`, `+15 minutes` - Plus prefix format

### Example Tickets

**Example 1**: "Ensure QA automation run is not affected (+4h)"
- Detected: +4 hours
- Applied to both manual and AI-assisted workflows

**Example 2**: "Fix login bug - manual regression testing required +2h"
- Detected: +2 hours
- Applied to both workflows

**Example 3**: "Add validation logic (+30m) and coordinate with ops team (+1h)"
- Detected: +30 minutes + 1 hour = 1.5 hours
- Applied to both workflows

### How It Works

1. Scans ticket title and description for time patterns
2. Extracts all time values (hours and minutes)
3. Sums them together
4. Adds total to both manual and AI-assisted estimates
5. Displays clearly in output

**Important**: Manual adjustments apply to BOTH workflows equally. They represent additional time that cannot be accelerated by AI (e.g., waiting for manual QA, coordinating with external teams, physical device testing).

### Configuration

Enable or disable in `heuristics.json`:

```json
{
  "manual_time_adjustments": {
    "enabled": true,
    "patterns": [...],
    "search_locations": ["title", "description"]
  }
}
```

## File Touch Overhead

For large-scale refactors touching many files, humans need additional time for navigation, context switching, and understanding each file. AI can batch process files efficiently. This feature adds realistic overhead **only to manual development estimates**.

### How It Works

```
Overhead Time = File Count × Base Time per File × Complexity Multiplier
```

**Default Parameters:**
- Base time per file: **5 minutes** (open, read, understand, modify)
- Minimum threshold: **20 files** (no overhead below this)
- Maximum cap: **300 minutes** (5 hours)

**Complexity Scaling:**
| Complexity | Range | Multiplier | Meaning |
|-----------|-------|------------|---------|
| Low | < 3.0/10 | 1.0× | Simple find/replace |
| Medium | 3.0-6.0/10 | 1.5× | Moderate changes |
| High | > 6.0/10 | 1.8× | Complex architectural changes |

### Example Usage

```
Estimate SATHREE-40524 with 60 files to be modified
Project type: monolithic
Task type: refactor
```

**Result for 60 files at complexity 7.65/10:**
- Overhead: 60 × 5 min × 1.8 (high) = **540 min, capped at 300 min (5h)**
- Manual estimate: 6h → **11h** (+5h overhead)
- AI-assisted: 4h → **4h** (NO overhead - AI batches files)

### Real-World Example

**SATHREE-40524 - Messages Cleanup:**
- Files affected: 60+ (32 sync files + 28 extendables)
- Complexity: 7.65/10 (high)
- Without overhead: 6h manual (unrealistic)
- With overhead: 11h manual (6h + 5h capped overhead - realistic)
- AI-assisted: 4h (no overhead needed)

### Why Manual Only?

**Manual Development:**
- Must open each file individually (~1 min)
- Read and understand context (~2 min)
- Make changes carefully (~1.5 min)
- Context switch between files (~30 sec)
- **Total: ~5 min per file**

**AI-Assisted Development:**
- Grep entire codebase (10 sec)
- Batch process all changes (2-3 min)
- No context switching overhead
- **Can handle 60 files as easily as 6**

### Configuration

Edit `heuristics.json` to customize:

```json
{
  "file_touch_overhead": {
    "enabled": true,
    "applies_to_workflow": "manual_only",
    "base_time_per_file_minutes": 5,
    "minimum_files_for_overhead": 20,
    "maximum_overhead_minutes": 300,
    "complexity_scaling": {
      "enabled": true,
      "low_complexity_multiplier": 1.0,
      "medium_complexity_multiplier": 1.5,
      "high_complexity_multiplier": 1.8,
      "thresholds": {
        "low": 3.0,
        "medium": 6.0,
        "high": 9.0
      }
    }
  }
}
```

**Customization options:**
1. Adjust `base_time_per_file_minutes` for your codebase complexity
2. Lower `minimum_files_for_overhead` to apply to smaller tasks
3. Increase `maximum_overhead_minutes` for very large refactors
4. Disable complexity scaling for flat multiplier
5. Set `enabled: false` to turn off entirely

See `FILE_TOUCH_OVERHEAD.md` for complete documentation.

## Configuration

All estimation parameters are stored in `heuristics.json`:

### Customize Workflow Phase Times

```json
{
  "project_types": {
    "monolithic": {
      "workflow_phases": {
        "planning_design": {
          "base_minutes_at_complexity_5": 90
        },
        "self_review": {
          "base_minutes": 30
        }
      }
    }
  }
}
```

### Customize Task Type Base Units

```json
{
  "task_types": {
    "net_new": {
      "base_unit_minutes": 45,
      "complexity_multiplier": 1.0
    }
  }
}
```

### Customize Overhead Activities

```json
{
  "overhead_activities": {
    "activities": {
      "database_changes": {
        "enabled": true,
        "additional_minutes": 20
      }
    }
  }
}
```

### Customize Bucket Rounding

```json
{
  "bucket_rounding": {
    "threshold_formula": "currentBucket + ((nextBucket - currentBucket) * 0.25)",
    "buckets": [0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36, 40]
  }
}
```

## Calibration

To customize estimates for your team:

1. **Start with defaults** - Use monolithic configuration as baseline
2. **Track estimated vs actual** - Log time for 10-20 tickets across all phases
3. **Calculate variance** - Compare estimated vs actual by phase
4. **Adjust parameters** - Update `heuristics.json` based on data
5. **Recalibrate quarterly** - Refine as team velocity changes

### Example Calibration Process

```
Ticket: PROJ-123 (Bug Fix, Monolithic)
Estimated: 2h (Planning: 23min, Impl: 16min, Self Review: 30min, Testing: 6min, Review: 11min, Deploy: 25min, Verification: 5min)
Actual:    2.5h (Planning: 30min, Impl: 20min, Self Review: 30min, Testing: 10min, Review: 15min, Deploy: 25min, Verification: 5min)

Adjustment: Increase planning_design base from 90 to 100 minutes
```

After 10-20 tickets, update `heuristics.json`:

```json
{
  "monolithic": {
    "workflow_phases": {
      "planning_design": {
        "base_minutes_at_complexity_5": 100
      }
    }
  }
}
```

## File Structure

```
jira-ticket-estimator/
├── README.md                           # This file
├── SKILL.md                            # Skill definition for Claude Code
├── FILE_TOUCH_OVERHEAD.md              # File touch overhead feature guide
├── heuristics.json                     # All estimation configuration
├── scripts/
│   └── estimator.py                    # Python calculation engine
└── references/
    ├── task-type-classification.md     # Task type guide
    ├── complexity-scoring-guide.md     # Complexity scoring reference
    ├── workflow-formulas.md            # Mathematical formulas
    └── overhead-activities.md          # Overhead configuration guide
```

## Advanced Usage

### Manual Complexity Scores

If you want to override automatic complexity calculation:

```
Estimate PROJ-123 with these complexity scores:
- Scope Size: 8
- Technical Complexity: 7
- Testing Requirements: 6
- Risk & Unknowns: 5
- Dependencies: 7
```

### Force Task Type

If automatic classification is wrong:

```
Estimate PROJ-123 as a refactor (not an enhancement)
Project type: serverless
```

### Infrastructure Changes

For tickets with infrastructure changes (longer deploy times):

```
Estimate PROJ-123 with infrastructure changes
Project type: fullstack
```

### File Count for Multi-File Refactors

For large-scale refactors touching many files:

```
Estimate PROJ-123 with 60 files to be modified
Project type: monolithic
```

This adds realistic file touch overhead to manual estimates only. The overhead includes time for:
- Opening and navigating to each file
- Reading and understanding context
- Making changes carefully
- Context switching between different areas

AI-assisted estimates do NOT include this overhead since AI can batch process files efficiently.

## Time Savings Breakdown

AI-assisted development typically provides 40-50% time savings:

| Phase | Manual | AI-Assisted | Savings |
|-------|--------|-------------|---------|
| Planning & Design | 100% | 30-35% | 65-70% faster |
| Implementation | 100% | 35-40% | 60-65% faster |
| Self Review | 100% | AI Review (fixed 10-15min) | ~80% faster |
| Testing | 100% | 55-70% (human validation) | 30-45% faster |
| Code Review | 100% | Iterations (20-35min) | 60-80% faster |
| Deploy | 100% | 100% (same time) | 0% |
| Verification | 100% | ~50% (faster smoke tests) | ~50% faster |
| **Overhead Activities** | **100%** | **100% (same time)** | **0%** |
| **Manual Time Adjustments** | **100%** | **100% (same time)** | **0%** |
| **File Touch Overhead** | **100%** | **0% (not needed)** | **100% saved** |

**Important**: Overhead activities (DBA tickets, cross-team coordination, security reviews) and manual time adjustments take the same time regardless of AI usage. However, **file touch overhead** provides massive savings - AI can handle 60 files as easily as 6 files.

**Example 1 - Overhead**: A task with 10h manual workflow and 5h AI-assisted workflow (50% savings) plus 1h overhead becomes 11h manual vs 6h AI-assisted (45% overall savings).

**Example 2 - Manual Adjustment**: A ticket with "(+4h)" for manual QA testing: 6h manual workflow + 4h adjustment = 10h total; 3h AI workflow + 4h adjustment = 7h total (30% overall savings, down from 50% workflow-only savings).

**Example 3 - File Touch Overhead**: A refactor touching 60 files: 6h manual base + 5h file overhead (capped) = 11h manual; 3h AI base + 0h file overhead = 3h AI (73% savings! File overhead amplifies AI advantage).

**Note**: AI-assisted savings assume:
- Access to AI coding tools (Claude, Cursor, GitHub Copilot)
- Developer experienced with AI pair programming
- Well-defined requirements and acceptance criteria
- Existing codebase with patterns AI can follow

## Troubleshooting

### Estimates seem too high/low

1. Check task type classification - is it correct?
2. Review complexity scores - are they accurate?
3. Compare to actual time from similar past tickets
4. Adjust base times in `heuristics.json`

### Overhead not detected

1. Check keywords in ticket title/description
2. Verify overhead is enabled in `heuristics.json`
3. Add custom keywords if needed
4. Check `applies_to_task_types` constraint

### Manual time adjustment not detected

1. Check format: Use `(+4h)`, `+4h`, `(30m)`, or `+30m`
2. Verify feature is enabled in `heuristics.json`
3. Check ticket title and description for patterns
4. Try parentheses format for clarity: `(+Xh)`

### File touch overhead not applied

1. Check if `file_count` parameter was provided
2. Verify file count is ≥ 20 (minimum threshold)
3. Check if feature is enabled in `heuristics.json`
4. Ensure you're looking at manual estimate (not AI-assisted)
5. Verify overhead is shown in implementation phase breakdown

### File touch overhead seems too high/low

1. Adjust `base_time_per_file_minutes` in `heuristics.json`
2. Review complexity multiplier thresholds
3. Check if cap was applied (300 min default)
4. Compare to actual time from similar multi-file refactors
5. Consider disabling complexity scaling for flat multiplier

### Wrong project type selected

Explicitly specify project type:
```
Estimate PROJ-123 for serverless project
```

## Contributing

To customize this skill for your team:

1. **Clone/fork** this skill
2. **Calibrate** base times using your historical data
3. **Add custom overheads** for your processes
4. **Document assumptions** in comments
5. **Share learnings** with your team

## License

This skill is part of the Claude Code ecosystem. Customize freely for your team's needs.

## Support

For issues or questions:
1. Check `references/` directory for detailed guides
2. Review example outputs in `scripts/estimator.py`
3. Consult `SKILL.md` for complete workflow documentation

---

**Last Updated**: 2025-11-15
**Version**: 2.5 (fixed file touch overhead thresholds, added input validation, improved spike handling, added config caching, word boundary matching)
