# File Touch Overhead Feature

## Overview

The **File Touch Overhead** feature adds realistic time estimates for manual development tasks that touch many files. This overhead accounts for the mechanical work of navigating, reading, understanding context, and modifying multiple files.

**Key Principle**: This overhead **only applies to manual development**, NOT AI-assisted development, because AI can batch process many files efficiently while humans must context-switch between files.

## When It Applies

- **Enabled by default**: Yes
- **Minimum file threshold**: 20 files
- **Maximum overhead cap**: 300 minutes (5 hours)
- **Workflow**: Manual only (AI-assisted workflow is NOT affected)

## How It Works

### Calculation Formula

```
Overhead Time = File Count × Base Time per File × Complexity Multiplier
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_time_per_file_minutes` | 2.5 min | Time to open, read, understand, and modify one file |
| `minimum_files_for_overhead` | 20 files | Threshold below which no overhead is applied |
| `maximum_overhead_minutes` | 300 min | Cap to prevent runaway estimates |

### Complexity Multipliers

The multiplier scales based on raw complexity (not adjusted):

| Complexity Level | Range | Multiplier | Meaning |
|-----------------|-------|------------|---------|
| **Low** | < 3.0/10 | 0.6× | Simple find/replace, mechanical changes |
| **Medium** | 3.0 - 6.0/10 | 1.0× | Moderate changes with some logic |
| **High** | > 6.0/10 | 1.5× | Complex architectural changes |

## Usage

### Basic Usage

```python
from estimator import TicketEstimator

estimator = TicketEstimator('heuristics.json')

result = estimator.estimate_ticket(
    title="Messages Cleanup (BE)",
    description="Refactor messaging sync code across 60 files",
    project_type="monolithic",
    complexity_scores={
        'scope_size': 8,
        'technical_complexity': 7,
        'testing_requirements': 8,
        'risk_and_unknowns': 7,
        'dependencies': 8
    },
    task_type_override="refactor",
    file_count=60  # <-- NEW PARAMETER
)

print(result['file_touch_overhead'])
```

### Output

```json
{
  "enabled": true,
  "overhead_minutes": 225.0,
  "overhead_hours": 3.75,
  "file_count": 60,
  "base_time_per_file": 2.5,
  "complexity_multiplier": 1.5,
  "complexity_level": "high",
  "raw_complexity": 7.65,
  "calculation": "60 files × 2.5 min × 1.5 = 225.0 min",
  "capped": false,
  "details": "60 files with high complexity (7.7/10)"
}
```

## Examples

### Example 1: Large Refactor (60 files, high complexity)

**Input:**
- File count: 60
- Raw complexity: 7.65/10

**Calculation:**
```
60 files × 2.5 min × 1.5 (high complexity) = 225 minutes (3.75 hours)
```

**Impact:**
- Manual Development: 5.90h → **9.65h** (+3.75h)
- AI-Assisted: 3.32h → **3.32h** (no change)

### Example 2: Medium Refactor (30 files, high complexity)

**Input:**
- File count: 30
- Raw complexity: 7.65/10

**Calculation:**
```
30 files × 2.5 min × 1.5 (high complexity) = 112.5 minutes (1.88 hours)
```

**Impact:**
- Manual Development: 5.90h → **7.78h** (+1.88h)
- AI-Assisted: 3.32h → **3.32h** (no change)

### Example 3: Small Task (15 files)

**Input:**
- File count: 15
- Raw complexity: 7.65/10

**Calculation:**
```
Below minimum threshold (20 files) → 0 minutes overhead
```

**Impact:**
- Manual Development: 5.90h (no change)
- AI-Assisted: 3.32h (no change)

## Configuration

Edit `heuristics.json` to customize the behavior:

```json
{
  "file_touch_overhead": {
    "enabled": true,
    "applies_to_workflow": "manual_only",
    "base_time_per_file_minutes": 2.5,
    "minimum_files_for_overhead": 20,
    "maximum_overhead_minutes": 300,
    "complexity_scaling": {
      "enabled": true,
      "low_complexity_multiplier": 0.6,
      "medium_complexity_multiplier": 1.0,
      "high_complexity_multiplier": 1.5,
      "thresholds": {
        "low": 3.0,
        "medium": 6.0,
        "high": 10.0
      }
    }
  }
}
```

### Customization Options

1. **Adjust base time per file**: Change `base_time_per_file_minutes` based on your codebase complexity
2. **Change threshold**: Lower `minimum_files_for_overhead` if you want overhead for smaller tasks
3. **Adjust cap**: Increase `maximum_overhead_minutes` for very large refactors
4. **Disable complexity scaling**: Set `complexity_scaling.enabled` to `false` for flat multiplier
5. **Disable entirely**: Set `enabled` to `false` to turn off the feature

## Why Manual Only?

**Manual Development:**
- Human must open each file individually
- Read and understand surrounding code
- Navigate between files
- Context switch between different areas
- Each file takes ~2-3 minutes minimum

**AI-Assisted Development:**
- AI can grep entire codebase in seconds
- Batch process multiple files simultaneously
- Generate changes across many files in one prompt
- No context switching overhead
- Can handle 60 files as easily as 6 files

## Real-World Validation

**SATHREE-40524 - Messages Cleanup:**
- **Files affected**: 60+
- **Manual estimate without overhead**: 6h
- **Manual estimate with overhead**: 12h (+3.75h overhead)
- **AI-assisted estimate**: 6h (no overhead)
- **Original Jira estimate**: 26h (includes unknowns and coordination)

The feature bridges the gap between "ideal time" (6h) and "realistic time" (12h), making the 26h original estimate more understandable (includes testing, coordination, unknowns).

## Benefits

1. **More realistic estimates** for large-scale refactors
2. **Highlights AI value** by showing where AI saves the most time
3. **Configurable** for different team speeds and codebase complexities
4. **Automatic** - no manual calculation needed
5. **Capped** - prevents unrealistic estimates

## Best Practices

1. **Count files accurately**: Use grep/find to count files that will actually be modified
2. **Be conservative**: Round up if unsure about file count
3. **Consider test files**: Include test files in the count if they need updates
4. **Review estimates**: For 40+ files, review the overhead to ensure it's reasonable
5. **Track actuals**: Compare estimated vs actual to calibrate `base_time_per_file_minutes`

## Limitations

1. **Assumes uniform changes**: Doesn't account for some files being more complex than others
2. **No distinction between file types**: Treats all files equally (config vs code)
3. **Linear scaling**: Assumes constant time per file (reality may have diminishing returns)
4. **Doesn't account for tools**: Modern IDEs with "find/replace all" can reduce overhead

Despite these limitations, the feature provides significantly more realistic estimates for multi-file refactors than ignoring file count entirely.
