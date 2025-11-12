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


class TicketEstimator:
    """Main estimator class with all calculation logic."""

    def __init__(self, heuristics_file='heuristics.json'):
        """Load configuration from heuristics.json."""
        with open(heuristics_file, 'r') as f:
            self.config = json.load(f)['estimation_config']

    def classify_task_type(self, title: str, description: str, issue_type: str = None) -> Tuple[str, List[str]]:
        """
        Classify ticket into task type based on keywords and issue type.

        Returns:
            Tuple of (task_type_key, reasons)
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        reasons = []

        # Check issue type first
        if issue_type:
            for task_key, task_config in self.config['task_types'].items():
                if 'issue_types' in task_config and issue_type in task_config['issue_types']:
                    reasons.append(f"Issue type is '{issue_type}'")
                    return task_key, reasons

        # Check keywords for each task type
        for task_key, task_config in self.config['task_types'].items():
            keywords = task_config.get('keywords', [])
            exclude_keywords = task_config.get('exclude_keywords', [])

            # Check if any keyword matches
            keyword_matches = []
            for keyword in keywords:
                if keyword in title_lower or keyword in desc_lower:
                    keyword_matches.append(keyword)

            # Check if any exclude keyword matches
            exclude_matches = []
            for exclude in exclude_keywords:
                if exclude in title_lower or exclude in desc_lower:
                    exclude_matches.append(exclude)

            # If we have keyword matches and no exclude matches, classify
            if keyword_matches and not exclude_matches:
                reasons.append(f"Keywords found: {', '.join(keyword_matches)}")
                return task_key, reasons

        # Default to enhancement if uncertain
        reasons.append("No specific keywords found, defaulting to enhancement")
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
        adjusted_complexity = raw_complexity * multiplier

        # Calculate scale factor
        scale_factor = adjusted_complexity / 5.0

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

    def detect_overhead_activities(self,
                                   title: str,
                                   description: str,
                                   task_type: str,
                                   project_type: str = None,
                                   files_involved: List[str] = None) -> List[Dict]:
        """
        Detect overhead activities based on keywords and file patterns.

        Args:
            title: Ticket title
            description: Ticket description
            task_type: Task type (bug_fix, enhancement, etc.)
            project_type: Project type (monolithic, serverless, test_automation, etc.)
            files_involved: List of file paths involved in the change

        Returns:
            List of detected overhead activities with time and rationale
        """
        if 'overhead_activities' not in self.config:
            return []

        overhead_config = self.config['overhead_activities']
        detected = []

        for activity_key, activity in overhead_config.get('activities', {}).items():
            # Skip if not enabled
            if not activity.get('enabled', False):
                continue

            # Check if applies to this task type
            applies_to_task_types = activity.get('applies_to_task_types', [])
            if applies_to_task_types and task_type not in applies_to_task_types:
                continue

            # Check if applies to this project type
            applies_to_project_types = activity.get('applies_to_project_types', [])
            if applies_to_project_types and project_type and project_type not in applies_to_project_types:
                continue

            detection = activity.get('detection', {})
            keywords = detection.get('keywords', [])
            check_title = detection.get('check_title', False)
            check_description = detection.get('check_description', False)
            check_files = detection.get('check_files', False)
            file_patterns = detection.get('file_patterns', [])

            # Check for keyword matches
            matched_keywords = []
            text_to_check = ''

            if check_title:
                text_to_check += ' ' + title.lower()
            if check_description:
                text_to_check += ' ' + description.lower()

            # Check text for keywords
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    matched_keywords.append(keyword)

            # Check file patterns if files provided
            file_matches = []
            if check_files and files_involved:
                import fnmatch
                for file_path in files_involved:
                    file_lower = file_path.lower()
                    for pattern in file_patterns:
                        if fnmatch.fnmatch(file_lower, pattern.lower()):
                            file_matches.append(file_path)
                            break

            # If we found matches, add to detected
            if matched_keywords or file_matches:
                detected.append({
                    'activity_key': activity_key,
                    'label': activity.get('label', activity_key),
                    'description': activity.get('description', ''),
                    'rationale': activity.get('rationale', ''),
                    'additional_minutes': activity.get('additional_minutes', 0),
                    'matched_keywords': matched_keywords[:3],  # Show up to 3 keywords
                    'matched_files': file_matches[:3],  # Show up to 3 files
                    'notes': activity.get('notes', '')
                })

        return detected

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
            if base_unit is None:  # Spike - time-boxed separately
                implementation_time = 0
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

            # Total
            total_minutes = (test_planning_time + environment_setup_time + page_objects_time +
                            implementation_time + gherkin_integration_time + testing_time + documentation_time)

            return {
                'test_planning': round(test_planning_time, 1),
                'environment_setup': round(environment_setup_time, 1),
                'page_objects': round(page_objects_time, 1),
                'implementation': round(implementation_time, 1),
                'gherkin_integration': round(gherkin_integration_time, 1),
                'testing': round(testing_time, 1),
                'documentation': round(documentation_time, 1),
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
                    }
                }
            }

        # Standard workflow for other project types
        # Phase 1: Planning & Design (scales with complexity)
        planning_base = phases['planning_design']['base_minutes_at_complexity_5']
        planning_time = planning_base * scale_factor

        # Phase 2: Implementation (task-type-specific base unit × adjusted complexity)
        base_unit = task_config['base_unit_minutes']
        if base_unit is None:  # Spike - time-boxed separately
            implementation_time = 0
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

        # Total
        total_minutes = (planning_time + implementation_time + self_review_time +
                        testing_time + code_review_time + deploy_time + verification_time)

        return {
            'planning_design': round(planning_time, 1),
            'implementation': round(implementation_time, 1),
            'self_review': round(self_review_time, 1),
            'testing': round(testing_time, 1),
            'code_review': round(code_review_time, 1),
            'deployment_to_test': round(deploy_time, 1),
            'verification': round(verification_time, 1),
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

            # Total
            total_minutes = (ai_test_planning_time + ai_environment_time + ai_page_objects_time +
                            ai_implementation_time + ai_gherkin_time + ai_testing_time + ai_documentation_time)

            return {
                'ai_test_planning': round(ai_test_planning_time, 1),
                'ai_environment_setup': round(ai_environment_time, 1),
                'ai_page_objects': round(ai_page_objects_time, 1),
                'ai_implementation': round(ai_implementation_time, 1),
                'ai_gherkin': round(ai_gherkin_time, 1),
                'ai_testing': round(ai_testing_time, 1),
                'ai_documentation': round(ai_documentation_time, 1),
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

        # Total
        total_minutes = (ai_planning_time + ai_implementation_time + ai_review_time +
                        human_review_testing_time + iterations_time + deploy_time + verification_time)

        return {
            'ai_planning': round(ai_planning_time, 1),
            'ai_implementation': round(ai_implementation_time, 1),
            'ai_review': round(ai_review_time, 1),
            'human_review_testing': round(human_review_testing_time, 1),
            'iterations': round(iterations_time, 1),
            'deploy_test': round(deploy_time, 1),
            'test_verification': round(verification_time, 1),
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
        base_time = config.get('base_time_per_file_minutes', 2.5)

        # Calculate complexity multiplier
        scaling_config = config.get('complexity_scaling', {})
        if scaling_config.get('enabled', True):
            thresholds = scaling_config.get('thresholds', {})
            if raw_complexity < thresholds.get('low', 3.0):
                multiplier = scaling_config.get('low_complexity_multiplier', 0.6)
                complexity_level = 'low'
            elif raw_complexity < thresholds.get('medium', 6.0):
                multiplier = scaling_config.get('medium_complexity_multiplier', 1.0)
                complexity_level = 'medium'
            else:
                multiplier = scaling_config.get('high_complexity_multiplier', 1.5)
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
                       Adds 2.5 min/file overhead to manual workflow (20 file minimum).
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
            task_type = task_type_override
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

        # Validate file_count for large scope
        if complexity_scores['scope_size'] >= 7 and (file_count is None or file_count == 0):
            import warnings
            warnings.warn(
                f"\n{'=' * 70}\n"
                f"WARNING: High scope_size ({complexity_scores['scope_size']}/10) detected but file_count=0!\n"
                f"\n"
                f"File touch overhead may be significantly underestimated.\n"
                f"Consider running repository reconnaissance to count affected files:\n"
                f"  - Use Grep/Glob to find all files to be modified\n"
                f"  - Count unique files across all searches\n"
                f"  - Pass file_count parameter to estimate_ticket()\n"
                f"\n"
                f"Impact: For large refactors (50-100+ files), this can add 2-5 hours\n"
                f"to the manual workflow estimate.\n"
                f"{'=' * 70}\n",
                UserWarning,
                stacklevel=2
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
            # Find the implementation phase key (differs by project type)
            impl_phase_key = '4_implementation' if project_type == 'test_automation' else '2_implementation'
            manual_workflow['phases'][impl_phase_key]['time_minutes'] += file_touch_overhead['overhead_minutes']
            manual_workflow['phases'][impl_phase_key]['file_touch_overhead'] = file_touch_overhead

        # Detect overhead activities
        overhead_activities = self.detect_overhead_activities(title, description, task_type, project_type=project_type, files_involved=None)

        # Calculate total overhead time
        overhead_minutes = sum(activity['additional_minutes'] for activity in overhead_activities)
        overhead_hours = overhead_minutes / 60.0

        # Add overhead to workflow total
        total_with_overhead = manual_workflow['total_hours'] + overhead_hours

        # Apply bucket rounding (on total including overhead)
        rounded_hours, rounding_threshold = self.apply_bucket_rounding(total_with_overhead)

        # Calculate AI-assisted workflow
        ai_assisted_workflow = self.calculate_ai_assisted_workflow_time(
            project_type=project_type,
            task_type=task_type,
            adjusted_complexity=adjusted_complexity,
            scale_factor=scale_factor,
            manual_workflow=manual_workflow,
            has_infrastructure_changes=has_infrastructure_changes
        )

        # Add overhead to AI-assisted total (same overhead applies)
        ai_total_with_overhead = ai_assisted_workflow['total_hours'] + overhead_hours

        # Apply bucket rounding to AI-assisted total
        ai_rounded_hours, ai_rounding_threshold = self.apply_bucket_rounding(ai_total_with_overhead)

        # Calculate time savings
        time_savings_hours = total_with_overhead - ai_total_with_overhead
        time_savings_percentage = (time_savings_hours / total_with_overhead * 100) if total_with_overhead > 0 else 0

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
                'manual_total': round(total_with_overhead, 2),
                'ai_assisted_total': round(ai_total_with_overhead, 2)
            },
            'overhead_activities': {
                'detected': overhead_activities,
                'total_overhead_minutes': round(overhead_minutes, 1),
                'total_overhead_hours': round(overhead_hours, 2),
                'count': len(overhead_activities)
            },
            'total_including_overhead': {
                'total_hours_calculated': round(total_with_overhead, 2),
                'total_hours_rounded': rounded_hours,
                'rounding_threshold': rounding_threshold
            },
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
    print(f"  7. Verification:             {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
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
    print(f"  7. Verification:             {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
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
    print(f"  7. Verification:             {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
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
    print(f"  7. Verification:             {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
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
    print(f"  7. Verification:             {workflow['verification']:6.1f} min ({workflow['verification']/60:.2f}h)")
    print(f"  {'─' * 50}")
    print(f"  Subtotal (workflow):         {workflow['total_hours']:.2f}h")

    # Show overhead activities
    overhead = result['overhead_activities']
    if overhead['count'] > 0:
        print(f"\nOverhead Activities Detected: {overhead['count']}")
        for activity in overhead['detected']:
            print(f"  • {activity['label']}: +{activity['additional_minutes']} min")
            print(f"    Reason: {activity['rationale']}")
            if activity['matched_keywords']:
                print(f"    Keywords: {', '.join(activity['matched_keywords'])}")
        print(f"  Total Overhead: {overhead['total_overhead_minutes']} min ({overhead['total_overhead_hours']}h)")

    totals = result['total_including_overhead']
    print(f"\n  {'─' * 50}")
    print(f"  TOTAL (with overhead):       {totals['total_hours_calculated']:.2f}h")
    print(f"  TOTAL (rounded to bucket):   {totals['total_hours_rounded']}h")

    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70 + "\n")
