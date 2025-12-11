#!/usr/bin/env python3
"""
Jira Ticket Estimator - Utility Functions

Provides calculation and classification functions for comprehensive
ticket estimation based on task type, complexity scoring, and workflow phases.

All configuration is loaded from heuristics.json.
"""

import re
import json
import math
from typing import Dict, List, Tuple, Optional

# Constants
COMPLEXITY_REFERENCE_POINT = 5.0  # Midpoint of 1-10 complexity scale
MIN_COMPLEXITY_SCORE = 1
MAX_COMPLEXITY_SCORE = 10
DEFAULT_SELF_REVIEW_MINUTES = 30

# Config cache to avoid re-parsing JSON
_config_cache = {}


class TicketEstimator:
    """Main estimator class with all calculation logic."""

    def __init__(self, heuristics_file='heuristics.json'):
        """Load configuration from heuristics.json with caching."""
        if heuristics_file not in _config_cache:
            with open(heuristics_file, 'r') as f:
                _config_cache[heuristics_file] = json.load(f)['estimation_config']
        self.config = _config_cache[heuristics_file]

    def classify_task_type(self, title: str, description: str, issue_type: str = None) -> Tuple[str, List[str]]:
        """
        Classify ticket into task type based on characteristics, context clues, and keywords.

        Uses characteristic-based classification (not purely keyword-based):
        - Analyzes context clues like "existing", "current", "improve"
        - Considers the nature of work (quality improvements vs new functionality)
        - Uses keywords as supporting evidence, not primary classification

        Returns:
            Tuple of (task_type_key, reasons)
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        combined_text = f"{title_lower} {desc_lower}"
        reasons = []

        # Check issue type first (strongest signal)
        if issue_type:
            for task_key, task_config in self.config['task_types'].items():
                if 'issue_types' in task_config and issue_type in task_config['issue_types']:
                    reasons.append(f"Issue type is '{issue_type}'")
                    return task_key, reasons

        # Detect context clues for characteristic-based classification
        context_clues = {
            'existing_code': bool(re.search(r'\b(existing|current|already exists?)\b', combined_text)),
            'from_scratch': bool(re.search(r'\b(from scratch|brand new|first (integration|implementation))\b', combined_text)),
            'quality_improvement': bool(re.search(r'\b(type safety|type guard|error handling|validation|strengthen|harden|optimize|improve|refactor)\b', combined_text)),
            'new_component': bool(re.search(r'\bnew (component|service|module|feature|endpoint|integration|api)\b', combined_text)),
        }

        # Collect keyword matches for all task types
        all_matches = {}
        for task_key, task_config in self.config['task_types'].items():
            keywords = task_config.get('keywords', [])
            exclude_keywords = task_config.get('exclude_keywords', [])

            keyword_matches = []
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, combined_text):
                    keyword_matches.append(keyword)

            exclude_matches = []
            for exclude in exclude_keywords:
                pattern = r'\b' + re.escape(exclude) + r'\b'
                if re.search(pattern, combined_text):
                    exclude_matches.append(exclude)

            if keyword_matches and not exclude_matches:
                all_matches[task_key] = keyword_matches

        # Characteristic-based classification with context awareness

        # Priority 1: Refactor - if quality improvement indicators + existing code
        if 'refactor' in all_matches or context_clues['quality_improvement']:
            if context_clues['existing_code'] or context_clues['quality_improvement']:
                reasons.append(f"Improving existing code quality/safety")
                if 'refactor' in all_matches:
                    reasons.append(f"Keywords: {', '.join(all_matches['refactor'])}")
                if context_clues['existing_code']:
                    reasons.append(f"Context: mentions existing/current code")
                return 'refactor', reasons

        # Priority 2: Bug Fix
        if 'bug_fix' in all_matches:
            reasons.append(f"Keywords found: {', '.join(all_matches['bug_fix'])}")
            return 'bug_fix', reasons

        # Priority 3: Spike
        if 'spike' in all_matches:
            reasons.append(f"Keywords found: {', '.join(all_matches['spike'])}")
            return 'spike', reasons

        # Priority 4: Net-New - only if truly new component without existing code reference
        if 'net_new' in all_matches:
            if context_clues['new_component'] or context_clues['from_scratch']:
                if not context_clues['existing_code']:
                    reasons.append(f"Building new component from scratch")
                    reasons.append(f"Keywords: {', '.join(all_matches['net_new'])}")
                    if context_clues['new_component']:
                        reasons.append(f"Context: new component/service/module detected")
                    return 'net_new', reasons

            # "create"/"new" found but with existing code context -> likely enhancement or refactor
            if context_clues['existing_code']:
                reasons.append(f"Keywords '{', '.join(all_matches['net_new'])}' found, but working with existing code")
                # Check if it's more like enhancement or refactor
                if 'enhancement' in all_matches:
                    reasons.append(f"Classified as Enhancement: extending existing functionality")
                    return 'enhancement', reasons
                else:
                    reasons.append(f"Classified as Enhancement: context suggests extending existing code")
                    return 'enhancement', reasons

        # Priority 5: Enhancement - adding to existing code
        if 'enhancement' in all_matches:
            reasons.append(f"Keywords found: {', '.join(all_matches['enhancement'])}")
            if context_clues['existing_code']:
                reasons.append(f"Context: working with existing code")
            return 'enhancement', reasons

        # Default to enhancement if uncertain
        reasons.append("No clear classification, defaulting to enhancement (conservative)")
        return 'enhancement', reasons

    def calculate_complexity_score(self,
                                   task_type: str,
                                   scope_score: int,
                                   technical_score: int,
                                   testing_score: int,
                                   risk_score: int,
                                   dependencies_score: int) -> Tuple[float, float, float]:
        """
        Calculate raw and adjusted complexity scores.

        Returns:
            Tuple of (raw_complexity, adjusted_complexity, scale_factor)
        """
        # Validate all complexity scores
        scores = {
            'scope_size': scope_score,
            'technical_complexity': technical_score,
            'testing_requirements': testing_score,
            'risk_and_unknowns': risk_score,
            'dependencies': dependencies_score
        }

        for factor, score in scores.items():
            if not MIN_COMPLEXITY_SCORE <= score <= MAX_COMPLEXITY_SCORE:
                raise ValueError(
                    f"{factor} must be between {MIN_COMPLEXITY_SCORE}-{MAX_COMPLEXITY_SCORE}, got {score}"
                )

        # Get task-type-specific weights
        weights = self.config['complexity_weights'][task_type]

        # Calculate weighted average (raw complexity)
        raw_complexity = (
            scope_score * weights['scope_size'] +
            technical_score * weights['technical_complexity'] +
            testing_score * weights['testing_requirements'] +
            risk_score * weights['risk_and_unknowns'] +
            dependencies_score * weights['dependencies']
        ) / 100.0

        # Apply task type multiplier
        task_config = self.config['task_types'][task_type]
        multiplier = task_config['complexity_multiplier']

        # Handle spike which has None multiplier (time-boxed, complexity doesn't scale)
        if multiplier is None:
            adjusted_complexity = raw_complexity  # No adjustment for spikes
            scale_factor = 1.0  # Fixed scale factor for spikes
        else:
            adjusted_complexity = raw_complexity * multiplier
            scale_factor = adjusted_complexity / COMPLEXITY_REFERENCE_POINT

        return raw_complexity, adjusted_complexity, scale_factor

    def get_t_shirt_size(self, adjusted_complexity: float) -> str:
        """Map adjusted complexity to T-shirt size."""
        for size, config in self.config['t_shirt_sizing'].items():
            min_val, max_val = config['complexity_range']
            if min_val <= adjusted_complexity <= max_val:
                return size
        return 'XL'  # Default to XL if over 10

    def get_story_points(self, adjusted_complexity: float, team_velocity: float = 1.0) -> int:
        """Map adjusted complexity to Story Points (Fibonacci)."""
        # Apply team velocity
        base_points = adjusted_complexity * team_velocity

        # Get Fibonacci sequence
        fibonacci = self.config['story_points']['fibonacci_sequence']

        # Find nearest Fibonacci number
        nearest = min(fibonacci, key=lambda x: abs(x - base_points))
        return nearest

    def classify_manual_adjustment_to_phase(self,
                                            title: str,
                                            description: str,
                                            project_type: str) -> str:
        """
        Classify a manual time adjustment to determine which phase it belongs to.

        Args:
            title: Ticket title
            description: Ticket description (context where adjustment was found)
            project_type: Project type to determine available phases

        Returns:
            Phase key (e.g., 'verification', 'testing') or None if doesn't match any phase
        """
        combined_text = f"{title} {description}".lower()

        # Phase classification patterns (order matters - most specific first)
        phase_patterns = {
            # Code Review phase (CHECK FIRST - most specific)
            'code_review': [
                r'\bcode\s+review\b',
                r'\bpeer\s+review\b',
                r'\bsecurity\s+review\b',
                r'\breview\s+(with|by)\b',
                r'\bpr\s+review\b',
                r'\bpull\s+request\s+review\b',
                r'\baddress\s+(review\s+)?feedback\b'
            ],
            # Self Review phase
            'self_review': [
                r'\bself.?review\b'
            ],
            # Verification phase
            'verification': [
                r'\bqa\b',
                r'\bquality\s+assurance\b',
                r'\bmanual\s+test(ing)?\b',
                r'\bsmoke\s+test\b',
                r'\bsanity\s+test\b',
                r'\bverification\b',
                r'\bverify\b',
                r'\bqa\s+(self\s+)?run\b',
                r'\be2e\s+test\b',
                r'\bend.?to.?end\s+test\b'
            ],
            # Testing phase
            'testing': [
                r'\bunit\s+test\b',
                r'\bintegration\s+test\b',
                r'\btest\s+coverage\b',
                r'\bwrite\s+test\b',
                r'\btest\s+case\b',
                r'\btest\s+development\b',
                r'\btesting\s+(requirement|effort|time)\b'
            ],
            # Planning & Design phase
            'planning_design': [
                r'\bplanning\s+(session|meeting|discussion)\b',
                r'\barchitecture\s+(planning|design)\b',
                r'\bdesign\s+(session|meeting|document)\b',
                r'\btechnical\s+spec\b',
                r'\bspecification\b',
                r'\brequirement\s+(analysis|gathering)\b'
            ],
            # Implementation phase
            'implementation': [
                r'\bimplementation\b',
                r'\bcoding\b',
                r'\bdevelopment\b',
                r'\bwrite\s+code\b',
                r'\bdevelop\s+feature\b',
                r'\badditional\s+(implementation|coding)\b'
            ],
            # Deployment phase
            'deployment_to_test': [
                r'\bdeployment\b',
                r'\bdeploy\b',
                r'\brelease\b',
                r'\brollout\b',
                r'\bdeploy\s+to\s+(test|staging|dev)\b'
            ],
            # Feedback & Iterations phase
            'feedback_iterations': [
                r'\bfeedback\b',
                r'\biteration\b',
                r'\brefinement\b',
                r'\badjust\b',
                r'\btweak\b',
                r'\bpolish\b',
                r'\bincorporate\s+feedback\b',
                r'\biterative\s+(development|work)\b'
            ]
        }

        # Check each phase pattern
        for phase_key, patterns in phase_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    return phase_key

        # No match found
        return None

    def detect_manual_time_adjustments(self,
                                       title: str,
                                       description: str) -> Dict:
        """
        Detect manual time adjustments from ticket title/description.

        Args:
            title: Ticket title
            description: Ticket description

        Returns:
            Dict with total adjustment hours and list of detected adjustments
        """
        config = self.config.get('manual_time_adjustments', {})

        if not config.get('enabled', True):
            return {
                'enabled': False,
                'total_hours': 0,
                'adjustments': []
            }

        patterns = config.get('patterns', [])
        search_locations = config.get('search_locations', ['title', 'description'])

        # Combine search text
        search_text = ''
        if 'title' in search_locations:
            search_text += title + ' '
        if 'description' in search_locations:
            search_text += description

        adjustments = []
        total_minutes = 0
        seen_positions = set()  # Track positions to avoid overlapping matches

        for pattern_config in patterns:
            regex = pattern_config.get('regex', '')
            description_text = pattern_config.get('description', '')

            # Use finditer to get match objects with positions
            for match_obj in re.finditer(regex, search_text, re.IGNORECASE):
                # Skip if this position overlaps with a previous match
                match_range = range(match_obj.start(), match_obj.end())
                if any(pos in seen_positions for pos in match_range):
                    continue

                # Mark this range as seen
                seen_positions.update(match_range)

                match = match_obj.group(0)

                # Extract number (from first captured group)
                if match_obj.groups():
                    number = float(match_obj.group(1))
                else:
                    # Fallback: try to extract number from match
                    num_match = re.search(r'(\d+(?:\.\d+)?)', match)
                    number = float(num_match.group(1)) if num_match else 0

                # Determine if hours or minutes based on pattern
                if 'm' in regex.lower() and 'h' not in regex.lower():
                    # Minutes pattern
                    minutes = number
                    hours = number / 60.0
                else:
                    # Hours pattern
                    hours = number
                    minutes = number * 60

                # Extract context: find the line containing this match
                # Find line boundaries
                line_start = search_text.rfind('\n', 0, match_obj.start()) + 1
                line_end = search_text.find('\n', match_obj.end())
                if line_end == -1:
                    line_end = len(search_text)

                # Extract just the current line as context
                context = search_text[line_start:line_end].strip()

                # Determine source more accurately
                source = 'title' if match_obj.start() < len(title) else 'description'

                total_minutes += minutes
                adjustments.append({
                    'value': number,
                    'unit': 'minutes' if 'm' in regex.lower() and 'h' not in regex.lower() else 'hours',
                    'hours': hours,
                    'minutes': minutes,
                    'source': source,
                    'pattern': description_text,
                    'context': context,
                    'matched_text': match,
                    'position': (match_obj.start(), match_obj.end())
                })

        return {
            'enabled': True,
            'total_hours': round(total_minutes / 60.0, 2),
            'total_minutes': round(total_minutes, 1),
            'adjustments': adjustments,
            'count': len(adjustments)
        }

    def calculate_manual_workflow_time(self,
                                      project_type: str,
                                      task_type: str,
                                      adjusted_complexity: float,
                                      scale_factor: float,
                                      has_infrastructure_changes: bool = False) -> Dict[str, float]:
        """
        Calculate manual development workflow time breakdown based on project type.

        Standard workflow (7 phases):
        1. Planning & Design
        2. Implementation
        3. Self Review
        4. Testing
        5. Code Review & Revisions
        6. Deployment to Test
        7. Verification

        Test Automation workflow (7 phases):
        1. Analysis & Test Planning
        2. Environment & Framework Setup
        3. Page Objects & Locators
        4. Step Implementations & Business Logic
        5. Step Definitions & Gherkin Integration
        6. Testing & Evidence Collection
        7. Integration & Documentation

        Returns:
            Dict with phase times in minutes and total
        """
        project_config = self.config['project_types'][project_type]
        task_config = self.config['task_types'][task_type]
        phases = project_config['workflow_phases']

        # Handle test_automation project type with custom workflow
        if project_type == 'test_automation':
            # Phase 1: Analysis & Test Planning (scales with complexity)
            test_planning_base = phases['test_planning']['base_minutes_at_complexity_5']
            test_planning_time = test_planning_base * scale_factor

            # Phase 2: Environment & Framework Setup (scales with complexity)
            environment_setup_base = phases['environment_setup']['base_minutes_at_complexity_5']
            environment_setup_time = environment_setup_base * scale_factor

            # Phase 3: Page Objects & Locators (scales with complexity)
            page_objects_base = phases['page_objects']['base_minutes_at_complexity_5']
            page_objects_time = page_objects_base * scale_factor

            # Phase 4: Step Implementations & Business Logic (task-type-specific)
            base_unit = task_config['base_unit_minutes']
            if base_unit is None:  # Spike - use time-box
                time_box_hours = task_config.get('time_box_hours', [2])
                # Use middle value from time-box
                implementation_time = time_box_hours[len(time_box_hours) // 2] * 60
            else:
                implementation_time = adjusted_complexity * base_unit

            # Phase 5: Step Definitions & Gherkin Integration (scales with complexity)
            gherkin_integration_base = phases['gherkin_integration']['base_minutes_at_complexity_5']
            gherkin_integration_time = gherkin_integration_base * scale_factor

            # Phase 6: Testing & Evidence Collection (scales with complexity)
            testing_base = phases['testing']['base_minutes_at_complexity_5']
            testing_time = testing_base * scale_factor

            # Phase 7: Integration & Documentation (scales with complexity)
            documentation_base = phases['documentation']['base_minutes_at_complexity_5']
            documentation_time = documentation_base * scale_factor

            # Phase 8: Feedback & Iterations (scales with complexity)
            feedback_iterations_base = phases['feedback_iterations']['base_minutes_at_complexity_5']
            feedback_iterations_time = feedback_iterations_base * scale_factor

            # Total
            total_minutes = (test_planning_time + environment_setup_time + page_objects_time +
                            implementation_time + gherkin_integration_time + testing_time + documentation_time +
                            feedback_iterations_time)

            return {
                'test_planning': round(test_planning_time, 1),
                'environment_setup': round(environment_setup_time, 1),
                'page_objects': round(page_objects_time, 1),
                'implementation': round(implementation_time, 1),
                'gherkin_integration': round(gherkin_integration_time, 1),
                'testing': round(testing_time, 1),
                'documentation': round(documentation_time, 1),
                'feedback_iterations': round(feedback_iterations_time, 1),
                'total_minutes': round(total_minutes, 1),
                'total_hours': round(total_minutes / 60.0, 2),
                'phases': {
                    '1_test_planning': {
                        'label': phases['test_planning']['label'],
                        'description': phases['test_planning']['description'],
                        'time_minutes': round(test_planning_time, 1),
                        'scales_with_complexity': True
                    },
                    '2_environment_setup': {
                        'label': phases['environment_setup']['label'],
                        'description': phases['environment_setup']['description'],
                        'time_minutes': round(environment_setup_time, 1),
                        'scales_with_complexity': True
                    },
                    '3_page_objects': {
                        'label': phases['page_objects']['label'],
                        'description': phases['page_objects']['description'],
                        'time_minutes': round(page_objects_time, 1),
                        'scales_with_complexity': True
                    },
                    '4_implementation': {
                        'label': phases['implementation']['label'],
                        'description': phases['implementation']['description'],
                        'time_minutes': round(implementation_time, 1),
                        'scales_with_complexity': True,
                        'task_type_base_unit': base_unit
                    },
                    '5_gherkin_integration': {
                        'label': phases['gherkin_integration']['label'],
                        'description': phases['gherkin_integration']['description'],
                        'time_minutes': round(gherkin_integration_time, 1),
                        'scales_with_complexity': True
                    },
                    '6_testing': {
                        'label': phases['testing']['label'],
                        'description': phases['testing']['description'],
                        'time_minutes': round(testing_time, 1),
                        'scales_with_complexity': True
                    },
                    '7_documentation': {
                        'label': phases['documentation']['label'],
                        'description': phases['documentation']['description'],
                        'time_minutes': round(documentation_time, 1),
                        'scales_with_complexity': True
                    },
                    '8_feedback_iterations': {
                        'label': phases['feedback_iterations']['label'],
                        'description': phases['feedback_iterations']['description'],
                        'time_minutes': round(feedback_iterations_time, 1),
                        'scales_with_complexity': True
                    }
                }
            }

        # Standard workflow for other project types
        # Phase 1: Planning & Design (scales with complexity)
        planning_base = phases['planning_design']['base_minutes_at_complexity_5']
        planning_time = planning_base * scale_factor

        # Phase 2: Implementation (task-type-specific base unit × adjusted complexity)
        base_unit = task_config['base_unit_minutes']
        if base_unit is None:  # Spike - use time-box
            time_box_hours = task_config.get('time_box_hours', [2])
            # Use middle value from time-box
            implementation_time = time_box_hours[len(time_box_hours) // 2] * 60
        else:
            implementation_time = adjusted_complexity * base_unit

        # Phase 3: Self Review (fixed time)
        self_review_time = phases['self_review']['base_minutes']

        # Phase 4: Testing (percentage of implementation)
        testing_percentage = phases['testing']['percentage_of_implementation'] / 100.0
        testing_time = implementation_time * testing_percentage

        # Phase 5: Code Review & Revisions (scales with complexity)
        code_review_base = phases['code_review']['base_minutes_at_complexity_5']
        code_review_time = code_review_base * scale_factor

        # Phase 6: Deployment to Test (fixed)
        if has_infrastructure_changes:
            deploy_time = phases['deployment_to_test']['infrastructure_changes_minutes']
        else:
            deploy_time = phases['deployment_to_test']['base_minutes']

        # Phase 7: Verification (scales with complexity)
        verification_base = phases['verification']['base_minutes_at_complexity_5']
        verification_time = verification_base * scale_factor

        # Phase 8: Feedback & Iterations (scales with complexity)
        feedback_iterations_base = phases['feedback_iterations']['base_minutes_at_complexity_5']
        feedback_iterations_time = feedback_iterations_base * scale_factor

        # Total
        total_minutes = (planning_time + implementation_time + self_review_time +
                        testing_time + code_review_time + deploy_time + verification_time +
                        feedback_iterations_time)

        return {
            'planning_design': round(planning_time, 1),
            'implementation': round(implementation_time, 1),
            'self_review': round(self_review_time, 1),
            'testing': round(testing_time, 1),
            'code_review': round(code_review_time, 1),
            'deployment_to_test': round(deploy_time, 1),
            'verification': round(verification_time, 1),
            'feedback_iterations': round(feedback_iterations_time, 1),
            'total_minutes': round(total_minutes, 1),
            'total_hours': round(total_minutes / 60.0, 2),
            'phases': {
                '1_planning_design': {
                    'label': phases['planning_design']['label'],
                    'description': phases['planning_design']['description'],
                    'time_minutes': round(planning_time, 1),
                    'scales_with_complexity': True
                },
                '2_implementation': {
                    'label': phases['implementation']['label'],
                    'description': phases['implementation']['description'],
                    'time_minutes': round(implementation_time, 1),
                    'scales_with_complexity': True,
                    'task_type_base_unit': base_unit
                },
                '3_self_review': {
                    'label': phases['self_review']['label'],
                    'description': phases['self_review']['description'],
                    'time_minutes': round(self_review_time, 1),
                    'scales_with_complexity': False
                },
                '4_testing': {
                    'label': phases['testing']['label'],
                    'description': phases['testing']['description'],
                    'time_minutes': round(testing_time, 1),
                    'percentage_of_implementation': testing_percentage * 100
                },
                '5_code_review': {
                    'label': phases['code_review']['label'],
                    'description': phases['code_review']['description'],
                    'time_minutes': round(code_review_time, 1),
                    'scales_with_complexity': True
                },
                '6_deployment_to_test': {
                    'label': phases['deployment_to_test']['label'],
                    'description': phases['deployment_to_test']['description'],
                    'time_minutes': round(deploy_time, 1),
                    'infrastructure_changes': has_infrastructure_changes,
                    'scales_with_complexity': False
                },
                '7_verification': {
                    'label': phases['verification']['label'],
                    'description': phases['verification']['description'],
                    'time_minutes': round(verification_time, 1),
                    'scales_with_complexity': True
                },
                '8_feedback_iterations': {
                    'label': phases['feedback_iterations']['label'],
                    'description': phases['feedback_iterations']['description'],
                    'time_minutes': round(feedback_iterations_time, 1),
                    'scales_with_complexity': True
                }
            }
        }

    def calculate_ai_assisted_workflow_time(self,
                                            project_type: str,
                                            task_type: str,
                                            adjusted_complexity: float,
                                            scale_factor: float,
                                            manual_workflow: Dict[str, float],
                                            has_infrastructure_changes: bool = False) -> Dict[str, float]:
        """
        Calculate AI-assisted development workflow time breakdown.

        Standard AI workflow (7 phases):
        1. AI Planning
        2. AI Implementation
        3. AI Review
        4. Human Review & Testing
        5. Iterations & Vibe Coding
        6. Deploy to Test
        7. Test Verification

        Test Automation AI workflow (7 phases):
        1. AI Test Planning
        2. AI Environment Setup
        3. AI Page Objects
        4. AI Implementation
        5. AI Gherkin Integration
        6. AI Testing & Evidence
        7. AI Documentation

        Returns:
            Dict with phase times in minutes and total
        """
        project_config = self.config['project_types'][project_type]
        ai_phases = project_config['ai_assisted_workflow']

        # Handle test_automation project type with custom AI workflow
        if project_type == 'test_automation':
            # Phase 1: AI Test Planning (time savings from manual)
            ai_test_planning_config = ai_phases['ai_test_planning']
            savings_pct = ai_test_planning_config['time_savings_percentage'] / 100.0
            ai_test_planning_time = manual_workflow['test_planning'] * (1 - savings_pct)

            # Phase 2: AI Environment Setup (time savings from manual)
            ai_environment_config = ai_phases['ai_environment_setup']
            savings_pct = ai_environment_config['time_savings_percentage'] / 100.0
            ai_environment_time = manual_workflow['environment_setup'] * (1 - savings_pct)

            # Phase 3: AI Page Objects (time savings from manual)
            ai_page_objects_config = ai_phases['ai_page_objects']
            savings_pct = ai_page_objects_config['time_savings_percentage'] / 100.0
            ai_page_objects_time = manual_workflow['page_objects'] * (1 - savings_pct)

            # Phase 4: AI Implementation (time savings from manual)
            ai_implementation_config = ai_phases['ai_implementation']
            savings_pct = ai_implementation_config['time_savings_percentage'] / 100.0
            ai_implementation_time = manual_workflow['implementation'] * (1 - savings_pct)

            # Phase 5: AI Gherkin Integration (time savings from manual)
            ai_gherkin_config = ai_phases['ai_gherkin']
            savings_pct = ai_gherkin_config['time_savings_percentage'] / 100.0
            ai_gherkin_time = manual_workflow['gherkin_integration'] * (1 - savings_pct)

            # Phase 6: AI Testing & Evidence (time savings from manual)
            ai_testing_config = ai_phases['ai_testing']
            savings_pct = ai_testing_config['time_savings_percentage'] / 100.0
            ai_testing_time = manual_workflow['testing'] * (1 - savings_pct)

            # Phase 7: AI Documentation (time savings from manual)
            ai_documentation_config = ai_phases['ai_documentation']
            savings_pct = ai_documentation_config['time_savings_percentage'] / 100.0
            ai_documentation_time = manual_workflow['documentation'] * (1 - savings_pct)

            # Phase 8: Feedback & Iterations (scales with complexity)
            feedback_iterations_config = ai_phases['feedback_iterations']
            feedback_iterations_base = feedback_iterations_config['base_minutes_at_complexity_5']
            feedback_iterations_time = feedback_iterations_base * scale_factor

            # Total
            total_minutes = (ai_test_planning_time + ai_environment_time + ai_page_objects_time +
                            ai_implementation_time + ai_gherkin_time + ai_testing_time + ai_documentation_time +
                            feedback_iterations_time)

            return {
                'ai_test_planning': round(ai_test_planning_time, 1),
                'ai_environment_setup': round(ai_environment_time, 1),
                'ai_page_objects': round(ai_page_objects_time, 1),
                'ai_implementation': round(ai_implementation_time, 1),
                'ai_gherkin': round(ai_gherkin_time, 1),
                'ai_testing': round(ai_testing_time, 1),
                'ai_documentation': round(ai_documentation_time, 1),
                'feedback_iterations': round(feedback_iterations_time, 1),
                'total_minutes': round(total_minutes, 1),
                'total_hours': round(total_minutes / 60.0, 2),
                'phases': {
                    '1_ai_test_planning': {
                        'label': ai_phases['ai_test_planning']['label'],
                        'description': ai_phases['ai_test_planning']['description'],
                        'time_minutes': round(ai_test_planning_time, 1),
                        'time_savings_percentage': ai_phases['ai_test_planning']['time_savings_percentage']
                    },
                    '2_ai_environment_setup': {
                        'label': ai_phases['ai_environment_setup']['label'],
                        'description': ai_phases['ai_environment_setup']['description'],
                        'time_minutes': round(ai_environment_time, 1),
                        'time_savings_percentage': ai_phases['ai_environment_setup']['time_savings_percentage']
                    },
                    '3_ai_page_objects': {
                        'label': ai_phases['ai_page_objects']['label'],
                        'description': ai_phases['ai_page_objects']['description'],
                        'time_minutes': round(ai_page_objects_time, 1),
                        'time_savings_percentage': ai_phases['ai_page_objects']['time_savings_percentage']
                    },
                    '4_ai_implementation': {
                        'label': ai_phases['ai_implementation']['label'],
                        'description': ai_phases['ai_implementation']['description'],
                        'time_minutes': round(ai_implementation_time, 1),
                        'time_savings_percentage': ai_phases['ai_implementation']['time_savings_percentage']
                    },
                    '5_ai_gherkin': {
                        'label': ai_phases['ai_gherkin']['label'],
                        'description': ai_phases['ai_gherkin']['description'],
                        'time_minutes': round(ai_gherkin_time, 1),
                        'time_savings_percentage': ai_phases['ai_gherkin']['time_savings_percentage']
                    },
                    '6_ai_testing': {
                        'label': ai_phases['ai_testing']['label'],
                        'description': ai_phases['ai_testing']['description'],
                        'time_minutes': round(ai_testing_time, 1),
                        'time_savings_percentage': ai_phases['ai_testing']['time_savings_percentage']
                    },
                    '7_ai_documentation': {
                        'label': ai_phases['ai_documentation']['label'],
                        'description': ai_phases['ai_documentation']['description'],
                        'time_minutes': round(ai_documentation_time, 1),
                        'time_savings_percentage': ai_phases['ai_documentation']['time_savings_percentage']
                    },
                    '8_feedback_iterations': {
                        'label': ai_phases['feedback_iterations']['label'],
                        'description': ai_phases['feedback_iterations']['description'],
                        'time_minutes': round(feedback_iterations_time, 1),
                        'scales_with_complexity': True
                    }
                }
            }

        # Standard AI workflow for other project types
        # Phase 1: AI Planning (time savings from manual planning)
        ai_planning_config = ai_phases['ai_planning']
        savings_pct = ai_planning_config['time_savings_percentage'] / 100.0
        ai_planning_time = manual_workflow['planning_design'] * (1 - savings_pct)

        # Phase 2: AI Implementation (time savings from manual implementation)
        ai_impl_config = ai_phases['ai_implementation']
        savings_pct = ai_impl_config['time_savings_percentage'] / 100.0
        ai_implementation_time = manual_workflow['implementation'] * (1 - savings_pct)

        # Phase 3: AI Review (fixed time)
        ai_review_time = ai_phases['ai_review']['base_minutes']

        # Phase 4: Human Review & Testing (percentage of manual self_review + testing)
        human_review_config = ai_phases['human_review_testing']
        testing_pct = human_review_config['manual_phase_testing_percentage'] / 100.0
        self_review_pct = human_review_config['manual_phase_self_review_percentage'] / 100.0
        human_review_testing_time = (manual_workflow['self_review'] * self_review_pct +
                                      manual_workflow['testing'] * testing_pct)

        # Phase 5: Iterations & Vibe Coding (scales with complexity)
        iterations_config = ai_phases['iterations']
        iterations_base = iterations_config['base_minutes_at_complexity_5']
        iterations_time = iterations_base * scale_factor

        # Phase 6: Deploy to Test (same as manual deployment)
        deploy_time = manual_workflow['deployment_to_test']

        # Phase 7: Test Verification (fixed or based on infra)
        verification_config = ai_phases['test_verification']
        if has_infrastructure_changes:
            verification_time = verification_config['infrastructure_changes_minutes']
        else:
            verification_time = verification_config['base_minutes']

        # Phase 8: Feedback & Iterations (scales with complexity)
        feedback_iterations_config = ai_phases['feedback_iterations']
        feedback_iterations_base = feedback_iterations_config['base_minutes_at_complexity_5']
        feedback_iterations_time = feedback_iterations_base * scale_factor

        # Total
        total_minutes = (ai_planning_time + ai_implementation_time + ai_review_time +
                        human_review_testing_time + iterations_time + deploy_time + verification_time +
                        feedback_iterations_time)

        return {
            'ai_planning': round(ai_planning_time, 1),
            'ai_implementation': round(ai_implementation_time, 1),
            'ai_review': round(ai_review_time, 1),
            'human_review_testing': round(human_review_testing_time, 1),
            'iterations': round(iterations_time, 1),
            'deploy_test': round(deploy_time, 1),
            'test_verification': round(verification_time, 1),
            'feedback_iterations': round(feedback_iterations_time, 1),
            'total_minutes': round(total_minutes, 1),
            'total_hours': round(total_minutes / 60.0, 2),
            'phases': {
                '1_ai_planning': {
                    'label': ai_phases['ai_planning']['label'],
                    'description': ai_phases['ai_planning']['description'],
                    'time_minutes': round(ai_planning_time, 1),
                    'time_savings_percentage': ai_phases['ai_planning']['time_savings_percentage']
                },
                '2_ai_implementation': {
                    'label': ai_phases['ai_implementation']['label'],
                    'description': ai_phases['ai_implementation']['description'],
                    'time_minutes': round(ai_implementation_time, 1),
                    'time_savings_percentage': ai_phases['ai_implementation']['time_savings_percentage']
                },
                '3_ai_review': {
                    'label': ai_phases['ai_review']['label'],
                    'description': ai_phases['ai_review']['description'],
                    'time_minutes': round(ai_review_time, 1)
                },
                '4_human_review_testing': {
                    'label': ai_phases['human_review_testing']['label'],
                    'description': ai_phases['human_review_testing']['description'],
                    'time_minutes': round(human_review_testing_time, 1)
                },
                '5_iterations': {
                    'label': ai_phases['iterations']['label'],
                    'description': ai_phases['iterations']['description'],
                    'time_minutes': round(iterations_time, 1),
                    'scales_with_complexity': True
                },
                '6_deploy_test': {
                    'label': ai_phases['deploy_test']['label'],
                    'description': ai_phases['deploy_test']['description'],
                    'time_minutes': round(deploy_time, 1)
                },
                '7_test_verification': {
                    'label': ai_phases['test_verification']['label'],
                    'description': ai_phases['test_verification']['description'],
                    'time_minutes': round(verification_time, 1),
                    'infrastructure_changes': has_infrastructure_changes
                },
                '8_feedback_iterations': {
                    'label': ai_phases['feedback_iterations']['label'],
                    'description': ai_phases['feedback_iterations']['description'],
                    'time_minutes': round(feedback_iterations_time, 1),
                    'scales_with_complexity': True
                }
            }
        }

    def apply_bucket_rounding(self, hours: float) -> Tuple[int, float]:
        """
        Round hours to nearest bucket using threshold-based approach.

        Returns:
            Tuple of (rounded_hours, threshold_used)
        """
        buckets = self.config['bucket_rounding']['buckets_hours']
        thresholds = self.config['bucket_rounding']['thresholds']

        # Find current bucket (largest bucket <= hours)
        current_bucket = 0
        for bucket in buckets:
            if bucket <= hours:
                current_bucket = bucket
            else:
                break

        # Check if we should round up
        threshold_config = thresholds.get(str(current_bucket))
        if threshold_config:
            threshold = threshold_config['threshold']
            if hours > threshold:
                # Jump to next bucket
                rounded = threshold_config['next']
                return rounded, threshold

        # Stay at current bucket
        return current_bucket, threshold_config['threshold'] if threshold_config else hours

    def calculate_file_touch_overhead(self, file_count: int, raw_complexity: float) -> Dict:
        """
        Calculate overhead time for touching many files in manual development.

        Args:
            file_count: Number of files to be modified
            raw_complexity: Raw complexity score (0-10)

        Returns:
            Dict with overhead details
        """
        config = self.config.get('file_touch_overhead', {})

        if not config.get('enabled', False):
            return {
                'enabled': False,
                'overhead_minutes': 0,
                'overhead_hours': 0,
                'file_count': file_count,
                'details': 'File touch overhead is disabled'
            }

        if file_count is None or file_count < config.get('minimum_files_for_overhead', 20):
            return {
                'enabled': True,
                'overhead_minutes': 0,
                'overhead_hours': 0,
                'file_count': file_count or 0,
                'details': f'Below minimum threshold ({config.get("minimum_files_for_overhead", 20)} files)'
            }

        # Get base time per file
        base_time = config.get('base_time_per_file_minutes', 5)

        # Calculate complexity multiplier
        scaling_config = config.get('complexity_scaling', {})
        if scaling_config.get('enabled', True):
            thresholds = scaling_config.get('thresholds', {})
            if raw_complexity < thresholds.get('low', 3.0):
                multiplier = scaling_config.get('low_complexity_multiplier', 1.0)
                complexity_level = 'low'
            elif raw_complexity < thresholds.get('medium', 6.0):
                multiplier = scaling_config.get('medium_complexity_multiplier', 1.5)
                complexity_level = 'medium'
            else:
                multiplier = scaling_config.get('high_complexity_multiplier', 1.8)
                complexity_level = 'high'
        else:
            multiplier = 1.0
            complexity_level = 'none'

        # Calculate overhead
        overhead_minutes = file_count * base_time * multiplier

        # Apply maximum cap
        max_overhead = config.get('maximum_overhead_minutes', 300)
        if overhead_minutes > max_overhead:
            overhead_minutes = max_overhead
            capped = True
        else:
            capped = False

        return {
            'enabled': True,
            'overhead_minutes': round(overhead_minutes, 1),
            'overhead_hours': round(overhead_minutes / 60.0, 2),
            'file_count': file_count,
            'base_time_per_file': base_time,
            'complexity_multiplier': multiplier,
            'complexity_level': complexity_level,
            'raw_complexity': raw_complexity,
            'calculation': f'{file_count} files × {base_time} min × {multiplier} = {round(overhead_minutes, 1)} min',
            'capped': capped,
            'maximum_overhead': max_overhead if capped else None,
            'details': f'{file_count} files with {complexity_level} complexity ({raw_complexity:.1f}/10)'
        }

    def _find_implementation_phase_key(self, phases: Dict) -> str:
        """
        Dynamically find the implementation phase key.

        Args:
            phases: Dict of workflow phases

        Returns:
            Phase key containing 'implementation'
        """
        for key in phases.keys():
            if 'implementation' in key.lower():
                return key
        raise ValueError("No implementation phase found in workflow phases")

    def distribute_adjustments_to_phases(self,
                                        workflow: Dict,
                                        adjustments: List[Dict],
                                        title: str,
                                        description: str,
                                        project_type: str) -> Tuple[Dict, List[Dict]]:
        """
        Distribute manual time adjustments to their appropriate workflow phases.

        Args:
            workflow: Workflow dict with phases
            adjustments: List of adjustment dicts from detect_manual_time_adjustments
            title: Ticket title
            description: Ticket description
            project_type: Project type

        Returns:
            Tuple of (updated workflow, unmatched adjustments for Phase 9)
        """
        unmatched_adjustments = []
        phase_adjustments = {}  # Track adjustments per phase

        for adj in adjustments:
            # Use context to classify to a phase
            context = adj.get('context', '')
            matched_text = adj.get('matched_text', '')

            # Classify using context + matched text
            phase_key = self.classify_manual_adjustment_to_phase(
                title=matched_text,
                description=context,
                project_type=project_type
            )

            if phase_key:
                # Find the correct phase number key in workflow
                phase_number_key = None
                for key in workflow['phases'].keys():
                    if phase_key in key:
                        phase_number_key = key
                        break

                if phase_number_key:
                    # Add time to the phase
                    workflow['phases'][phase_number_key]['time_minutes'] += adj['minutes']

                    # Track this adjustment
                    if phase_number_key not in phase_adjustments:
                        phase_adjustments[phase_number_key] = []
                    phase_adjustments[phase_number_key].append(adj)

                    # Add to totals
                    workflow['total_minutes'] += adj['minutes']
                    workflow['total_hours'] = round(workflow['total_minutes'] / 60.0, 2)

                    # Also update the shorthand key if it exists
                    shorthand_key = phase_key
                    if shorthand_key in workflow:
                        workflow[shorthand_key] += adj['minutes']
                else:
                    # Phase key not found in workflow, treat as unmatched
                    unmatched_adjustments.append(adj)
            else:
                # No phase match, add to unmatched
                unmatched_adjustments.append(adj)

        # Add adjustment details to each phase
        for phase_key, adjs in phase_adjustments.items():
            if 'manual_adjustments' not in workflow['phases'][phase_key]:
                workflow['phases'][phase_key]['manual_adjustments'] = []
            workflow['phases'][phase_key]['manual_adjustments'].extend(adjs)

        return workflow, unmatched_adjustments

    def estimate_ticket(self,
                       title: str,
                       description: str,
                       project_type: str = None,
                       issue_type: str = None,
                       complexity_scores: Dict[str, int] = None,
                       task_type_override: str = None,
                       team_velocity: float = None,
                       has_infrastructure_changes: bool = None,
                       file_count: int = None) -> Dict:
        """
        Complete estimation for a ticket.

        Args:
            title: Ticket title
            description: Ticket description
            project_type: Project architecture type (monolithic, serverless, frontend, fullstack, mobile, test_automation)
            issue_type: Jira issue type (Bug, Story, Task, Spike, etc.)
            complexity_scores: Dict with keys: scope_size, technical_complexity,
                             testing_requirements, risk_and_unknowns, dependencies
            task_type_override: Manual task type override
            team_velocity: Team velocity factor
            has_infrastructure_changes: Flag for infrastructure changes
            file_count: Number of unique files to be modified (CRITICAL for file_touch_overhead).
                       Count files from Grep/Glob searches during reconnaissance.
                       Adds 5 min/file overhead to manual workflow (20 file minimum).
                       Forgetting this parameter can underestimate by 2-5 hours for large refactors!

        Returns:
            Complete estimation breakdown including:
            - Task classification and complexity scores
            - T-shirt size and story points
            - Manual workflow time breakdown (7 phases)
            - AI-assisted workflow time breakdown (7 phases)
            - File touch overhead (manual only)
            - Detected overhead activities
            - Manual time adjustments
            - Time savings analysis
        """
        # Use defaults if not provided
        defaults = self.config.get('defaults', {})
        if project_type is None:
            project_type = defaults.get('project_type', 'monolithic')
        if team_velocity is None:
            team_velocity = defaults.get('team_velocity', 1.0)
        if has_infrastructure_changes is None:
            has_infrastructure_changes = defaults.get('has_infrastructure_changes', False)

        # Classify task type
        if task_type_override:
            # Normalize task type: convert hyphens to underscores for consistency
            task_type = task_type_override.replace('-', '_')
            task_type_reasons = [f"Manual override to '{task_type}'"]
        else:
            task_type, task_type_reasons = self.classify_task_type(title, description, issue_type)

        # Use provided complexity scores or defaults
        if complexity_scores is None:
            complexity_scores = {
                'scope_size': 5,
                'technical_complexity': 5,
                'testing_requirements': 5,
                'risk_and_unknowns': 5,
                'dependencies': 5
            }

        # Calculate complexity
        raw_complexity, adjusted_complexity, scale_factor = self.calculate_complexity_score(
            task_type,
            complexity_scores['scope_size'],
            complexity_scores['technical_complexity'],
            complexity_scores['testing_requirements'],
            complexity_scores['risk_and_unknowns'],
            complexity_scores['dependencies']
        )

        # Get sizing
        t_shirt_size = self.get_t_shirt_size(adjusted_complexity)
        story_points = self.get_story_points(adjusted_complexity, team_velocity)

        # Calculate manual development time based on project type
        manual_workflow = self.calculate_manual_workflow_time(
            project_type, task_type, adjusted_complexity, scale_factor, has_infrastructure_changes
        )

        # Calculate file touch overhead (manual development only)
        file_touch_overhead = self.calculate_file_touch_overhead(file_count, raw_complexity)

        # Add file touch overhead to manual workflow implementation time
        if file_touch_overhead['overhead_minutes'] > 0:
            manual_workflow['implementation'] += file_touch_overhead['overhead_minutes']
            manual_workflow['total_minutes'] += file_touch_overhead['overhead_minutes']
            manual_workflow['total_hours'] = round(manual_workflow['total_minutes'] / 60.0, 2)
            # Find implementation phase dynamically
            impl_phase_key = self._find_implementation_phase_key(manual_workflow['phases'])
            manual_workflow['phases'][impl_phase_key]['time_minutes'] += file_touch_overhead['overhead_minutes']
            manual_workflow['phases'][impl_phase_key]['file_touch_overhead'] = file_touch_overhead

        # Detect manual time adjustments
        manual_adjustments = self.detect_manual_time_adjustments(title, description)

        # Distribute adjustments to appropriate phases
        if manual_adjustments['total_minutes'] > 0:
            manual_workflow, unmatched_adjustments = self.distribute_adjustments_to_phases(
                workflow=manual_workflow,
                adjustments=manual_adjustments['adjustments'],
                title=title,
                description=description,
                project_type=project_type
            )

            # Only create Phase 9 if there are unmatched adjustments
            if unmatched_adjustments:
                # Build detailed description from unmatched adjustments
                adjustment_details = []
                unmatched_total_minutes = 0
                for adj in unmatched_adjustments:
                    if adj['unit'] == 'hours':
                        adjustment_details.append(f"+{adj['value']}h from {adj['source']}")
                    else:
                        adjustment_details.append(f"+{adj['value']}m from {adj['source']}")
                    unmatched_total_minutes += adj['minutes']

                details_text = ", ".join(adjustment_details)

                manual_workflow['phases']['9_overhead_activities'] = {
                    'label': 'Overhead Activities',
                    'description': f'Additional time specified in ticket: {details_text}',
                    'time_minutes': round(unmatched_total_minutes, 1),
                    'adjustments': unmatched_adjustments,
                    'scales_with_complexity': False
                }
                # Add to workflow totals (already added by distribute_adjustments_to_phases for matched ones)
                manual_workflow['total_minutes'] += unmatched_total_minutes
                manual_workflow['total_hours'] = round(manual_workflow['total_minutes'] / 60.0, 2)

            # Track all adjustments
            manual_workflow['manual_adjustments_total'] = round(manual_adjustments['total_minutes'], 1)

        # Apply bucket rounding to manual workflow total (now includes Phase 9)
        rounded_hours, rounding_threshold = self.apply_bucket_rounding(manual_workflow['total_hours'])

        # Calculate AI-assisted workflow
        ai_assisted_workflow = self.calculate_ai_assisted_workflow_time(
            project_type=project_type,
            task_type=task_type,
            adjusted_complexity=adjusted_complexity,
            scale_factor=scale_factor,
            manual_workflow=manual_workflow,
            has_infrastructure_changes=has_infrastructure_changes
        )

        # Distribute adjustments to AI-assisted workflow (same logic as manual)
        if manual_adjustments['total_minutes'] > 0:
            ai_assisted_workflow, ai_unmatched_adjustments = self.distribute_adjustments_to_phases(
                workflow=ai_assisted_workflow,
                adjustments=manual_adjustments['adjustments'],
                title=title,
                description=description,
                project_type=project_type
            )

            # Only create Phase 9 if there are unmatched adjustments
            if ai_unmatched_adjustments:
                # Build detailed description from unmatched adjustments
                adjustment_details = []
                ai_unmatched_total_minutes = 0
                for adj in ai_unmatched_adjustments:
                    if adj['unit'] == 'hours':
                        adjustment_details.append(f"+{adj['value']}h from {adj['source']}")
                    else:
                        adjustment_details.append(f"+{adj['value']}m from {adj['source']}")
                    ai_unmatched_total_minutes += adj['minutes']

                details_text = ", ".join(adjustment_details)

                ai_assisted_workflow['phases']['9_overhead_activities'] = {
                    'label': 'Overhead Activities',
                    'description': f'Additional time specified in ticket: {details_text}',
                    'time_minutes': round(ai_unmatched_total_minutes, 1),
                    'adjustments': ai_unmatched_adjustments,
                    'scales_with_complexity': False
                }
                # Add to workflow totals (already added by distribute_adjustments_to_phases for matched ones)
                ai_assisted_workflow['total_minutes'] += ai_unmatched_total_minutes
                ai_assisted_workflow['total_hours'] = round(ai_assisted_workflow['total_minutes'] / 60.0, 2)

            # Track all adjustments
            ai_assisted_workflow['manual_adjustments_total'] = round(manual_adjustments['total_minutes'], 1)

        # Apply bucket rounding to AI-assisted workflow total (now includes Phase 9)
        ai_rounded_hours, ai_rounding_threshold = self.apply_bucket_rounding(ai_assisted_workflow['total_hours'])

        # Calculate time savings (based on rounded values)
        time_savings_hours = rounded_hours - ai_rounded_hours
        time_savings_percentage = (time_savings_hours / rounded_hours * 100) if rounded_hours > 0 else 0

        return {
            'project_type': project_type,
            'project_type_label': self.config['project_types'][project_type]['label'],
            'task_type': task_type,
            'task_type_label': self.config['task_types'][task_type]['label'],
            'file_touch_overhead': file_touch_overhead,
            'task_type_reasons': task_type_reasons,
            't_shirt_size': t_shirt_size,
            'story_points': story_points,
            'raw_complexity': round(raw_complexity, 2),
            'adjusted_complexity': round(adjusted_complexity, 2),
            'scale_factor': round(scale_factor, 3),
            'complexity_scores': complexity_scores,
            'manual_workflow': {
                **manual_workflow,
                'total_hours_rounded': rounded_hours,
                'rounding_threshold': rounding_threshold
            },
            'ai_assisted_workflow': {
                **ai_assisted_workflow,
                'total_hours_rounded': ai_rounded_hours,
                'rounding_threshold': ai_rounding_threshold
            },
            'time_savings': {
                'hours': round(time_savings_hours, 2),
                'percentage': round(time_savings_percentage, 1),
                'manual_total': manual_workflow['total_hours'],
                'ai_assisted_total': ai_assisted_workflow['total_hours']
            },
            'manual_time_adjustments': manual_adjustments,
            'team_velocity': team_velocity,
            'has_infrastructure_changes': has_infrastructure_changes
        }


# Example usage
if __name__ == '__main__':
    estimator = TicketEstimator('heuristics.json')

    print("\n" + "=" * 70)
    print("JIRA TICKET ESTIMATOR - MANUAL DEV WORKFLOW")
    print("=" * 70)

    # Example 1: Bug Fix - Monolithic
    print("\n" + "=" * 70)
    print("Example 1: Bug Fix - Monolithic (Laravel)")
    print("=" * 70)
    result = estimator.estimate_ticket(
        title="Fix validation error on login form",
        description="The login form is not properly validating email addresses",
        project_type="monolithic",
        issue_type="Bug",
        complexity_scores={
            'scope_size': 2,
            'technical_complexity': 2,
            'testing_requirements': 4,
            'risk_and_unknowns': 2,
            'dependencies': 3
        }
    )

    print(f"Project Type: {result['project_type_label']}")
    print(f"Task Type: {result['task_type_label']}")
    print(f"T-Shirt Size: {result['t_shirt_size']}")
    print(f"Story Points: {result['story_points']}")
    print(f"Complexity: {result['raw_complexity']}/10 raw → {result['adjusted_complexity']}/10 adjusted")
    print(f"Scale Factor: {result['scale_factor']}")
    print("\nManual Development Time Breakdown:")
    workflow = result['manual_workflow']
    print(f"  1. Planning & Design:        {workflow['planning_design']:6.1f} min ({workflow['planning_design']/60:.2f}h)")
    print(f"  2. Implementation:           {workflow['implementation']:6.1f} min ({workflow['implementation']/60:.2f}h)")
    print(f"  3. Self Review:              {workflow['self_review']:6.1f} min ({workflow['self_review']/60:.2f}h)")
    print(f"  4. Testing:                  {workflow['testing']:6.1f} min ({workflow['testing']/60:.2f}h)")
    print(f"  5. Code Review & Revisions:  {workflow['code_review']:6.1f} min ({workflow['code_review']/60:.2f}h)")
    print(f"  6. Deployment to Test:       {workflow['deployment_to_test']:6.1f} min ({workflow['deployment_to_test']/60:.2f}h)")
    print(f"  7. Test Verification:        {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  8. Feedback & Iterations:    {workflow['feedback_iterations']:6.1f} min ({workflow['feedback_iterations']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Total (calculated):          {workflow['total_hours']:.2f}h")
    print(f"  Total (rounded to bucket):   {workflow['total_hours_rounded']}h")

    # Example 2: Refactor - Serverless
    print("\n" + "=" * 70)
    print("Example 2: Refactor - Serverless (AWS Lambda)")
    print("=" * 70)
    result = estimator.estimate_ticket(
        title="Optimize Lambda cold start and improve DynamoDB query patterns",
        description="Reduce cold start time and optimize DynamoDB query patterns",
        project_type="serverless",
        complexity_scores={
            'scope_size': 5,
            'technical_complexity': 6,
            'testing_requirements': 6,
            'risk_and_unknowns': 5,
            'dependencies': 6
        }
    )

    print(f"Project Type: {result['project_type_label']}")
    print(f"Task Type: {result['task_type_label']}")
    print(f"T-Shirt Size: {result['t_shirt_size']}")
    print(f"Story Points: {result['story_points']}")
    print(f"Complexity: {result['raw_complexity']}/10 raw → {result['adjusted_complexity']}/10 adjusted")
    print(f"Scale Factor: {result['scale_factor']}")
    print("\nManual Development Time Breakdown:")
    workflow = result['manual_workflow']
    print(f"  1. Planning & Design:        {workflow['planning_design']:6.1f} min ({workflow['planning_design']/60:.2f}h)")
    print(f"  2. Implementation:           {workflow['implementation']:6.1f} min ({workflow['implementation']/60:.2f}h)")
    print(f"  3. Self Review:              {workflow['self_review']:6.1f} min ({workflow['self_review']/60:.2f}h)")
    print(f"  4. Testing:                  {workflow['testing']:6.1f} min ({workflow['testing']/60:.2f}h)")
    print(f"  5. Code Review & Revisions:  {workflow['code_review']:6.1f} min ({workflow['code_review']/60:.2f}h)")
    print(f"  6. Deployment to Test:       {workflow['deployment_to_test']:6.1f} min ({workflow['deployment_to_test']/60:.2f}h)")
    print(f"  7. Test Verification:        {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  8. Feedback & Iterations:    {workflow['feedback_iterations']:6.1f} min ({workflow['feedback_iterations']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Total (calculated):          {workflow['total_hours']:.2f}h")
    print(f"  Total (rounded to bucket):   {workflow['total_hours_rounded']}h")

    # Example 3: Net-New Feature - Frontend
    print("\n" + "=" * 70)
    print("Example 3: Net-New Feature - Frontend (React)")
    print("=" * 70)
    result = estimator.estimate_ticket(
        title="Create new dashboard widget with real-time data",
        description="Build a new widget component that displays real-time metrics",
        project_type="frontend",
        complexity_scores={
            'scope_size': 4,
            'technical_complexity': 4,
            'testing_requirements': 4,
            'risk_and_unknowns': 4,
            'dependencies': 4
        }
    )

    print(f"Project Type: {result['project_type_label']}")
    print(f"Task Type: {result['task_type_label']}")
    print(f"T-Shirt Size: {result['t_shirt_size']}")
    print(f"Story Points: {result['story_points']}")
    print(f"Complexity: {result['raw_complexity']}/10 raw → {result['adjusted_complexity']}/10 adjusted")
    print(f"Scale Factor: {result['scale_factor']}")
    print("\nManual Development Time Breakdown:")
    workflow = result['manual_workflow']
    print(f"  1. Planning & Design:        {workflow['planning_design']:6.1f} min ({workflow['planning_design']/60:.2f}h)")
    print(f"  2. Implementation:           {workflow['implementation']:6.1f} min ({workflow['implementation']/60:.2f}h)")
    print(f"  3. Self Review:              {workflow['self_review']:6.1f} min ({workflow['self_review']/60:.2f}h)")
    print(f"  4. Testing:                  {workflow['testing']:6.1f} min ({workflow['testing']/60:.2f}h)")
    print(f"  5. Code Review & Revisions:  {workflow['code_review']:6.1f} min ({workflow['code_review']/60:.2f}h)")
    print(f"  6. Deployment to Test:       {workflow['deployment_to_test']:6.1f} min ({workflow['deployment_to_test']/60:.2f}h)")
    print(f"  7. Test Verification:        {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  8. Feedback & Iterations:    {workflow['feedback_iterations']:6.1f} min ({workflow['feedback_iterations']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Total (calculated):          {workflow['total_hours']:.2f}h")
    print(f"  Total (rounded to bucket):   {workflow['total_hours_rounded']}h")

    # Example 4: Enhancement - Full-Stack with infrastructure changes
    print("\n" + "=" * 70)
    print("Example 4: Enhancement - Full-Stack (with infra changes)")
    print("=" * 70)
    result = estimator.estimate_ticket(
        title="Add user notifications system with email + SMS + in-app alerts",
        description="Implement comprehensive notification system across all channels",
        project_type="fullstack",
        complexity_scores={
            'scope_size': 8,
            'technical_complexity': 7,
            'testing_requirements': 8,
            'risk_and_unknowns': 7,
            'dependencies': 8
        },
        has_infrastructure_changes=True
    )

    print(f"Project Type: {result['project_type_label']}")
    print(f"Task Type: {result['task_type_label']}")
    print(f"T-Shirt Size: {result['t_shirt_size']}")
    print(f"Story Points: {result['story_points']}")
    print(f"Complexity: {result['raw_complexity']}/10 raw → {result['adjusted_complexity']}/10 adjusted")
    print(f"Scale Factor: {result['scale_factor']}")
    print(f"Infrastructure Changes: {result['has_infrastructure_changes']}")
    print("\nManual Development Time Breakdown:")
    workflow = result['manual_workflow']
    print(f"  1. Planning & Design:        {workflow['planning_design']:6.1f} min ({workflow['planning_design']/60:.2f}h)")
    print(f"  2. Implementation:           {workflow['implementation']:6.1f} min ({workflow['implementation']/60:.2f}h)")
    print(f"  3. Self Review:              {workflow['self_review']:6.1f} min ({workflow['self_review']/60:.2f}h)")
    print(f"  4. Testing:                  {workflow['testing']:6.1f} min ({workflow['testing']/60:.2f}h)")
    print(f"  5. Code Review & Revisions:  {workflow['code_review']:6.1f} min ({workflow['code_review']/60:.2f}h)")
    print(f"  6. Deployment to Test:       {workflow['deployment_to_test']:6.1f} min ({workflow['deployment_to_test']/60:.2f}h) [with infra]")
    print(f"  7. Test Verification:        {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Total (calculated):          {workflow['total_hours']:.2f}h")
    print(f"  Total (rounded to bucket):   {workflow['total_hours_rounded']}h")

    # Example 5: Enhancement with Database Changes - Overhead Detection
    print("\n" + "=" * 70)
    print("Example 5: Enhancement with DB Changes - Monolithic")
    print("=" * 70)
    result = estimator.estimate_ticket(
        title="Add user preferences table with migration",
        description="Create new user_preferences table to store user settings. Need database migration to create table with columns: user_id, preference_key, preference_value, created_at, updated_at. Add index on user_id.",
        project_type="monolithic",
        complexity_scores={
            'scope_size': 4,
            'technical_complexity': 3,
            'testing_requirements': 4,
            'risk_and_unknowns': 3,
            'dependencies': 4
        }
    )

    print(f"Project Type: {result['project_type_label']}")
    print(f"Task Type: {result['task_type_label']}")
    print(f"T-Shirt Size: {result['t_shirt_size']}")
    print(f"Story Points: {result['story_points']}")
    print(f"Complexity: {result['raw_complexity']}/10 raw → {result['adjusted_complexity']}/10 adjusted")
    print(f"Scale Factor: {result['scale_factor']}")
    print("\nManual Development Time Breakdown:")
    workflow = result['manual_workflow']
    print(f"  1. Planning & Design:        {workflow['planning_design']:6.1f} min ({workflow['planning_design']/60:.2f}h)")
    print(f"  2. Implementation:           {workflow['implementation']:6.1f} min ({workflow['implementation']/60:.2f}h)")
    print(f"  3. Self Review:              {workflow['self_review']:6.1f} min ({workflow['self_review']/60:.2f}h)")
    print(f"  4. Testing:                  {workflow['testing']:6.1f} min ({workflow['testing']/60:.2f}h)")
    print(f"  5. Code Review & Revisions:  {workflow['code_review']:6.1f} min ({workflow['code_review']/60:.2f}h)")
    print(f"  6. Deployment to Test:       {workflow['deployment_to_test']:6.1f} min ({workflow['deployment_to_test']/60:.2f}h)")
    print(f"  7. Test Verification:        {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  8. Feedback & Iterations:    {workflow['feedback_iterations']:6.1f} min ({workflow['feedback_iterations']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Subtotal (workflow):         {workflow['total_hours']:.2f}h")

    # Show overhead activities (Phase 9)
    adjustments = result['manual_time_adjustments']
    if adjustments['count'] > 0:
        print(f"\nOverhead Activities (Phase 9) Detected: {adjustments['count']}")
        for adj in adjustments['adjustments']:
            print(f"  • +{adj['value']}{adj['unit'][0]}: {adj['hours']:.2f}h from {adj['source']}")
        print(f"  Total Overhead (Phase 9): {adjustments['total_minutes']} min ({adjustments['total_hours']}h)")

    print(f"\n  {'─' * 50}")
    print(f"  TOTAL (calculated):          {workflow['total_hours']:.2f}h")
    print(f"  TOTAL (rounded to bucket):   {workflow['total_hours_rounded']}h")

    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70 + "\n")
