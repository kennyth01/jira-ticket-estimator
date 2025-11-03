# Overhead Activities Guide

Additional time for project-specific processes and workflows that occur outside core development phases.

## Overview

Overhead activities are extra tasks that must be completed as part of the ticket but aren't captured in the standard 7-phase workflow. These are typically organizational processes, compliance requirements, or coordination activities.

**Related Feature**: See also [Manual Time Adjustments](#related-manual-time-adjustments) for handling explicit time additions specified directly in tickets (e.g., `+4h`, `(30m)`).

### Key Characteristics

- **Additive**: Added on top of the 7-phase workflow time
- **Applies to BOTH workflows**: Overhead time is added to both manual AND AI-assisted workflows
- **NOT accelerated by AI**: Creating DBA tickets or coordinating with teams takes the same time regardless of AI usage
- **Configurable**: Enable/disable per team's processes
- **Automatic Detection**: Triggered by keywords in title/description/files
- **Task-Type Aware**: Some overheads only apply to certain task types
- **Non-Stacking**: Each overhead applied once per ticket, regardless of how many times criteria match

### Why Overhead Isn't Accelerated by AI

While AI can significantly speed up planning, coding, and testing, it **cannot** accelerate:
- Creating coordination tickets for other teams
- Waiting for DBA to execute database changes
- Meeting with DevOps to explain deployment process
- Getting security/legal reviews approved

**Example**:
```
Manual workflow:         10.5h
AI-assisted workflow:     5.2h  (50% savings on workflow phases)
Overhead activities:     +0.8h  (same for both)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manual total:            11.3h
AI-assisted total:        6.0h  (47% savings overall - lower due to overhead)
```

The presence of overhead activities **reduces the overall time savings percentage** because a portion of the work cannot be accelerated.

## Default Overhead Activities

### 1. Database Change Management ✅ Enabled by Default

**Time**: +20 minutes
**Applies To**: Net-New, Enhancement, Refactor, Bug Fix

**Process**:
1. Create separate JIRA ticket for DBA team
2. DBA executes migration manually on test DB
3. DBA executes migration manually on prod DB
4. Attach migration script to Confluence page
5. Update documentation

**Detection Keywords**:
- Database-related: migration, database, db, table, column, index, schema
- SQL operations: create table, alter table, drop table, add column, modify column
- Constraints: add index, create index, foreign key, constraint

**File Patterns**:
- `*migration*` - Migration files
- `*schema*` - Schema definition files
- `*.sql` - SQL scripts

**Example Tickets**:
- "Add user_preferences table with migration"
- "Alter users table to add email_verified column"
- "Create index on orders.created_at for performance"
- "Update database schema for audit logging"

**Configuration**:
```json
{
  "database_changes": {
    "enabled": true,
    "additional_minutes": 20
  }
}
```

---

### 2. Cross-Team Coordination ✅ Enabled by Default

**Time**: +30 minutes
**Applies To**: Net-New, Enhancement, Refactor, Bug Fix

**Process**:
1. Create coordination ticket for operations/infrastructure team
2. Discuss and explain deployment/removal process
3. Coordinate with other teams for approvals
4. Document handoff and expectations

**Detection Keywords**:
- Team names: devops, infrastructure team, ops team, operations team, platform team, sre team, site reliability
- Collaboration: collab with, collaborate with, coordinate with, work with team, discuss with, explain to, sync with, align with
- Processes: deployment process, removal process, rollout process, infrastructure change, server change, environment change, create ticket for, coordinate deployment, handoff to

**Example Tickets**:
- "Remove old API endpoint - create ops ticket, collab with platform team to discuss and explain the removal process"
- "Deploy new feature - coordinate with DevOps team for infrastructure changes"
- "Update server configuration - work with infrastructure team on deployment"
- "Database migration - create coordination ticket and sync with operations team"

**Configuration**:
```json
{
  "cross_team_coordination": {
    "enabled": true,
    "additional_minutes": 30
  }
}
```

---

### 3. Security Review Process ❌ Disabled by Default

**Time**: +30 minutes
**Applies To**: Net-New, Enhancement, Refactor

**Process**:
1. Submit security review request
2. Security team reviews changes
3. Address security team findings
4. Get final approval

**Detection Keywords**:
- Auth/authz: security, auth, authentication, authorization, permission
- Credentials: credential, token, oauth, sso, role, access control

**When to Enable**:
- Organization requires formal security reviews
- Changes to authentication/authorization systems
- Handling sensitive data or credentials

**Configuration**:
```json
{
  "security_review": {
    "enabled": true,
    "additional_minutes": 30
  }
}
```

---

### 4. Legal/Compliance Review ❌ Disabled by Default

**Time**: +45 minutes
**Applies To**: Net-New, Enhancement

**Process**:
1. Submit to legal/compliance team
2. Review user-facing content or data handling
3. Incorporate legal feedback
4. Get final approval

**Detection Keywords**:
- Privacy: privacy, gdpr, ccpa, consent, pii, personal data
- Legal: terms, policy, data collection

**When to Enable**:
- Organization requires legal review for user-facing changes
- Changes affect data collection or privacy
- Updates to terms of service or policies

**Configuration**:
```json
{
  "legal_compliance": {
    "enabled": true,
    "additional_minutes": 45
  }
}
```

---

### 5. Documentation Update ❌ Disabled by Default

**Time**: +15 minutes
**Applies To**: Net-New, Enhancement

**Process**:
1. Update user-facing documentation
2. Update API documentation
3. Update wiki/confluence pages
4. Request documentation review

**Detection Keywords**:
- API changes: api change, breaking change, public api
- User-facing: new feature, user-facing, documentation needed

**When to Enable**:
- Documentation updates tracked separately from code
- Formal documentation review process exists
- External API documentation required

**Configuration**:
```json
{
  "documentation_update": {
    "enabled": true,
    "additional_minutes": 15
  }
}
```

---

## Creating Custom Overhead Activities

Add new overhead activities to `heuristics.json`:

```json
{
  "overhead_activities": {
    "activities": {
      "your_custom_overhead": {
        "enabled": true,
        "label": "Custom Overhead Name",
        "description": "What this overhead covers",
        "additional_minutes": 25,
        "rationale": "Explain why this time is needed",
        "detection": {
          "keywords": [
            "keyword1", "keyword2", "keyword3"
          ],
          "check_title": true,
          "check_description": true,
          "check_files": false,
          "file_patterns": ["*pattern*"]
        },
        "applies_to_task_types": ["net_new", "enhancement"],
        "notes": "Additional context for users"
      }
    }
  }
}
```

### Custom Overhead Examples

#### Example: Performance Testing

```json
{
  "performance_testing": {
    "enabled": true,
    "label": "Performance Testing",
    "description": "Load testing and performance validation",
    "additional_minutes": 40,
    "rationale": "Process: Run load tests + analyze results + document findings",
    "detection": {
      "keywords": ["performance", "load test", "stress test", "scalability", "throughput"],
      "check_title": true,
      "check_description": true,
      "check_files": false
    },
    "applies_to_task_types": ["net_new", "enhancement"],
    "notes": "For features expected to handle high load"
  }
}
```

#### Example: Accessibility Audit

```json
{
  "accessibility_audit": {
    "enabled": true,
    "label": "Accessibility Audit",
    "description": "A11y compliance check and remediation",
    "additional_minutes": 30,
    "rationale": "Process: Run a11y tools + manual keyboard testing + screen reader testing",
    "detection": {
      "keywords": ["frontend", "ui", "user interface", "component", "accessibility", "a11y"],
      "check_title": true,
      "check_description": true,
      "check_files": false
    },
    "applies_to_task_types": ["net_new", "enhancement"],
    "notes": "For user-facing UI changes"
  }
}
```

#### Example: Data Migration

```json
{
  "data_migration": {
    "enabled": true,
    "label": "Data Migration",
    "description": "Migrating existing data to new schema",
    "additional_minutes": 60,
    "rationale": "Process: Write migration script + test on sample data + execute on production + verify results",
    "detection": {
      "keywords": ["data migration", "migrate data", "backfill", "schema change with data"],
      "check_title": true,
      "check_description": true,
      "check_files": true,
      "file_patterns": ["*data_migration*", "*backfill*"]
    },
    "applies_to_task_types": ["enhancement", "refactor"],
    "notes": "For schema changes requiring data transformation"
  }
}
```

---

## How Overhead Detection Works

### Detection Sequence

1. **Check if enabled**: Skip if `enabled: false`
2. **Check task type applicability**: Skip if current task type not in `applies_to_task_types`
3. **Check keywords**: Scan title/description for keywords (case-insensitive)
4. **Check files**: Match file patterns against files involved (if specified)
5. **Record match**: If any keywords or files match, add overhead to estimate

### Multiple Overheads

Multiple overheads can apply to a single ticket:

**Example 1**: "Add OAuth authentication with database migration"
- ✅ Database Change Management: +20 min (keywords: "database", "migration")
- ✅ Security Review: +30 min (keywords: "authentication")
- **Total Overhead**: +50 minutes

**Example 2**: "Database schema change - create ops ticket and coordinate with infrastructure team"
- ✅ Database Change Management: +20 min (keywords: "database", "schema")
- ✅ Cross-Team Coordination: +30 min (keywords: "ops team", "coordinate with", "infrastructure team")
- **Total Overhead**: +50 minutes

### Keyword Matching

- **Case-insensitive**: "Database" matches "database"
- **Partial match**: Keyword "table" matches "create table" or "user_table"
- **Title or description**: Checks both locations if enabled
- **First match wins**: Once overhead triggered, additional matches ignored

### File Pattern Matching

Uses glob-style patterns:
- `*migration*` - Matches any file with "migration" in path
- `*.sql` - Matches all SQL files
- `schema/*.json` - Matches JSON files in schema directory

---

## Calibration

### Adjusting Time

Track actual overhead time and adjust in `heuristics.json`:

```json
{
  "database_changes": {
    "additional_minutes": 25  // Increased from 20 based on actuals
  }
}
```

### Adjusting Keywords

Add project-specific keywords:

```json
{
  "database_changes": {
    "detection": {
      "keywords": [
        "migration", "database", "db", "table",
        "flyway", "liquibase"  // Added project-specific tools
      ]
    }
  }
}
```

### Tracking Accuracy

Log overhead activities and actual time:

```
PROJ-123: Database Change Management
Estimated: +20 min
Actual: +25 min (DBA ticket took longer)
Adjustment: Increase to 25 min

PROJ-456: Security Review
Estimated: +30 min
Actual: +15 min (quick approval)
Note: Team improved security review process
```

---

## Best Practices

### 1. Start Conservative

Begin with a few essential overheads:
- ✅ Database changes (if you have DBAs)
- ❌ Everything else disabled

Add more as you identify patterns.

### 2. Be Specific with Keywords

**Good**: `["create table", "alter table", "add column"]`
**Bad**: `["change", "update", "add"]` (too broad)

### 3. Document the "Why"

Always include clear rationale:
```json
{
  "rationale": "Process: Create JIRA ticket for DBA + execute on test + execute on prod + document"
}
```

This helps teams understand and calibrate.

### 4. Review Quarterly

Every quarter:
1. Review detected overheads vs actuals
2. Adjust times based on data
3. Add new overheads for emerging patterns
4. Remove overheads that no longer apply

### 5. Make it Visible

Include overhead activities in estimate output:
```
Overhead Activities Detected: 2
  • Database Change Management: +20 min
  • Security Review: +30 min
Total Overhead: 50 min (0.83h)
```

This transparency helps stakeholders understand the full effort.

---

## Frequently Asked Questions

### Q: Should I create an overhead for every process?

**A**: No. Only create overheads for:
- Activities that consistently take >15 minutes
- Activities that occur frequently (>20% of tickets)
- Activities that are often forgotten in estimates

Don't create overheads for:
- Activities already in the 7 phases
- One-off edge cases
- Activities taking <10 minutes

### Q: What if overhead time varies widely?

**A**: Use the average time, then track variance:
- If variance >50%, consider splitting into multiple overheads (e.g., "Small Security Review" vs "Large Security Review")
- If specific to project type, create project-specific versions

### Q: Can I have project-type-specific overheads?

**A**: Yes! Nest overheads under project types:

```json
{
  "project_types": {
    "serverless": {
      "overhead_activities": {
        "lambda_deployment": {
          "enabled": true,
          "additional_minutes": 15
        }
      }
    }
  }
}
```

(Note: This requires custom estimator.py modifications)

### Q: Should overhead scale with complexity?

**A**: Generally no. Overhead activities are fixed processes (e.g., creating DBA ticket takes the same time regardless of complexity).

Exception: If overhead genuinely scales (e.g., documentation proportional to feature size), integrate it into a workflow phase instead.

---

## Open Source Considerations

When sharing this skill:

1. **Disable team-specific overheads**: Only enable universally applicable ones (like database changes)
2. **Document your processes**: Explain why each overhead exists
3. **Provide calibration guide**: Show how to adjust based on team data
4. **Include examples**: Real tickets that triggered each overhead
5. **Make it optional**: Teams should easily disable what doesn't apply

Example README section:

```markdown
## Overhead Activities

This skill includes optional overhead activities for common processes:

- ✅ Database Change Management: +20 min (enabled)
- ❌ Security Review: +30 min (disabled - enable if needed)
- ❌ Legal Review: +45 min (disabled - enable if needed)

To customize, edit `heuristics.json -> overhead_activities`.
```

This makes the skill reusable across different teams and organizations!

---

## Related: Manual Time Adjustments

While overhead activities are **automatically detected** based on keywords, **manual time adjustments** allow you to **explicitly specify** additional time directly in the ticket content.

### Key Differences

| Feature | Overhead Activities | Manual Time Adjustments |
|---------|---------------------|-------------------------|
| Detection | Automatic via keywords | Explicit in ticket content |
| Format | Keyword-based | Time pattern: `(+4h)`, `+30m` |
| Configuration | Enable/disable in heuristics.json | Regex patterns in heuristics.json |
| When to Use | Predictable process overhead | Case-specific additional time |
| Examples | DBA tickets, security reviews | Manual QA testing, external dependencies |

### When to Use Each

**Use Overhead Activities when**:
- The process is standard and repeatable
- Time is consistent across similar tickets
- Detection can be automated via keywords
- Example: "Database migration" → always +20 min for DBA ticket

**Use Manual Time Adjustments when**:
- Time requirement is specific to this ticket
- Amount varies by situation
- Stakeholder/PM explicitly specifies time
- Example: "Fix bug **(+4h for manual regression testing)**"

### Example: Combined Usage

Ticket: "Add OAuth authentication with database migration (+2h for manual security audit)"

**Overhead Activities Detected**:
- Database Change Management: +20 min (keyword: "database", "migration")
- Security Review: +30 min (keyword: "authentication")
- Total Overhead: +50 minutes

**Manual Time Adjustments Detected**:
- +2 hours (pattern: `(+2h for manual security audit)`)

**Total Additional Time**: 50 min + 2h = 2.83 hours

Both are added to the final estimate on top of the calculated workflow phases.

### Configuration

**Overhead Activities** (`heuristics.json`):
```json
{
  "overhead_activities": {
    "activities": {
      "database_changes": {
        "enabled": true,
        "additional_minutes": 20,
        "keywords": ["migration", "database"]
      }
    }
  }
}
```

**Manual Time Adjustments** (`heuristics.json`):
```json
{
  "manual_time_adjustments": {
    "enabled": true,
    "patterns": [
      {"regex": "\\(\\+?(\\d+(?:\\.\\d+)?)\\s*h(?:ours?)?\\)"}
    ]
  }
}
```

### Best Practice

Use both features together:
1. **Overhead activities** for predictable, repeatable processes
2. **Manual time adjustments** for one-off, explicit time requirements

This ensures estimates capture both standard organizational overhead and ticket-specific time needs.
