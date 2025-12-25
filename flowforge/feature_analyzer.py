"""
Feature Intelligence Analyzer - The AGI-pilled approach to feature evaluation.

Instead of the user deciding complexity, let the LLM analyze and classify features
based on codebase context, scope, and strategic importance.

Influenced by: The Design Panel's philosophy on intelligent systems
"Natural language in, structured feature out"
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import Enum
import subprocess
import json


class Complexity(str, Enum):
    """Feature complexity levels."""
    SMALL = "small"      # Single file, clear pattern, <1hr
    MEDIUM = "medium"    # 3-5 files, some decisions, 2-4hrs
    LARGE = "large"      # 6+ files, architectural, multi-day
    EPIC = "epic"        # Cross-cutting, needs breakdown


class ExpertDomain(str, Enum):
    """Domains that may require expert consultation."""
    STANDARD = "standard"        # No special expertise needed
    PERFORMANCE = "performance"  # John Carmack, Casey Muratori
    DESIGN = "design"            # Jony Ive, Dieter Rams, Bret Victor
    ARCHITECTURE = "architecture"  # Martin Fowler, Rich Hickey
    SECURITY = "security"        # Bruce Schneier
    PRODUCT = "product"          # Julie Zhuo, Ryan Singer


@dataclass
class ScopeAnalysis:
    """Results of analyzing feature scope in the codebase."""
    files_affected: list[str] = field(default_factory=list)
    estimated_lines: int = 0
    existing_patterns: list[str] = field(default_factory=list)
    design_system_exists: bool = False
    test_coverage_needed: bool = False
    new_dependencies: list[str] = field(default_factory=list)


@dataclass
class FeatureIntelligence:
    """
    Complete intelligence analysis for a feature.

    This is the AGI-pilled output: everything the user needs to know
    about a feature before they decide to build it.
    """
    # Core classification
    title: str
    description: str
    complexity: Complexity
    estimated_hours: float
    confidence: float  # 0.0 to 1.0 - how confident is the analysis

    # Scope details
    files_affected: list[str] = field(default_factory=list)
    scope_analysis: Optional[ScopeAnalysis] = None

    # Strategic scoring
    foundation_score: int = 5  # 1-10, how foundational to future work
    foundation_reasoning: str = ""

    # Parallelization
    parallelizable: bool = True
    parallel_conflicts: list[str] = field(default_factory=list)

    # Dependencies
    blocks: list[str] = field(default_factory=list)  # Feature IDs this enables
    blocked_by: list[str] = field(default_factory=list)  # Feature IDs this depends on

    # Expert routing
    needs_expert: bool = False
    expert_domain: ExpertDomain = ExpertDomain.STANDARD
    expert_reasoning: str = ""

    # Shippability
    shippable_today: bool = False
    scope_creep_detected: bool = False
    scope_creep_warning: str = ""
    suggested_breakdown: list[str] = field(default_factory=list)

    # Suggested tags
    suggested_tags: list[str] = field(default_factory=list)


class FeatureAnalyzer:
    """
    The AGI-pilled feature analyzer.

    Takes natural language feature descriptions and outputs structured
    intelligence about scope, complexity, and strategic importance.
    """

    def __init__(
        self,
        project_root: Path,
        claude_command: str = "claude",
    ):
        self.project_root = project_root
        self.claude_command = claude_command

    def _call_claude(self, prompt: str, timeout: int = 90) -> str:
        """Call Claude CLI with a prompt and return the response."""
        try:
            result = subprocess.run(
                [self.claude_command, "--print", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return '{"error": "Claude CLI timed out"}'
        except FileNotFoundError:
            return '{"error": "Claude CLI not found"}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def _scan_codebase_context(self) -> str:
        """Get a summary of the codebase for context."""
        # Get list of source files
        extensions = ['.py', '.swift', '.ts', '.tsx', '.js', '.jsx']
        files = []

        for ext in extensions:
            files.extend(self.project_root.rglob(f'*{ext}'))

        # Filter out common non-source directories
        filtered = [
            f for f in files
            if not any(p in str(f) for p in [
                'node_modules', '.git', '__pycache__',
                'venv', '.venv', 'build', 'dist'
            ])
        ]

        # Get relative paths
        relative_paths = [
            str(f.relative_to(self.project_root))
            for f in filtered[:100]  # Limit to 100 files for prompt size
        ]

        return "\n".join(relative_paths)

    def analyze_feature(
        self,
        title: str,
        description: str = "",
        existing_features: list[str] = None,
    ) -> FeatureIntelligence:
        """
        Analyze a feature and return complete intelligence.

        This is the main entry point for the AGI-pilled analysis.
        """
        codebase_context = self._scan_codebase_context()
        existing = existing_features or []

        prompt = f"""You are an expert software architect analyzing a feature request for intelligent classification.

PROJECT CODEBASE FILES:
{codebase_context}

EXISTING FEATURES IN PROGRESS:
{chr(10).join(f'- {f}' for f in existing) if existing else 'None'}

FEATURE TO ANALYZE:
Title: {title}
Description: {description if description else '(no description provided)'}

Analyze this feature and respond with a JSON object containing:

{{
  "complexity": "small|medium|large|epic",
  "estimated_hours": <number>,
  "confidence": <0.0-1.0>,
  "files_affected": ["file1.py", "file2.swift"],
  "existing_patterns": ["pattern1", "pattern2"],
  "foundation_score": <1-10>,
  "foundation_reasoning": "Why this is/isn't foundational",
  "parallelizable": true|false,
  "parallel_conflicts": ["conflicting feature if any"],
  "needs_expert": true|false,
  "expert_domain": "standard|performance|design|architecture|security|product",
  "expert_reasoning": "Why expert is/isn't needed",
  "shippable_today": true|false,
  "scope_creep_detected": true|false,
  "scope_creep_warning": "Warning message if detected",
  "suggested_breakdown": ["sub-feature 1", "sub-feature 2"],
  "suggested_tags": ["ui", "backend", "api"]
}}

CLASSIFICATION CRITERIA:

Complexity:
- SMALL: Single file change, clear pattern exists, <1 hour
- MEDIUM: 3-5 files, some decisions needed, 2-4 hours
- LARGE: 6+ files, architectural decisions, multi-day
- EPIC: Cross-cutting, should be broken into smaller features

Foundation Score (1-10):
- 10: Core infrastructure that many features depend on
- 7-9: Establishes patterns others will follow
- 4-6: Useful but isolated feature
- 1-3: Leaf feature with no dependencies

Expert Domains:
- standard: Normal implementation, patterns exist
- performance: Speed-critical, optimization needed
- design: UX-critical, design system impact
- architecture: New patterns, structural decisions
- security: Auth, encryption, sensitive data
- product: Strategic decisions, user psychology

Shippable Today:
- Only true if complexity is small/medium AND no blockers

Scope Creep Detection:
- Look for "and also", "plus", "additionally"
- Look for multiple distinct features combined
- Flag if >100 chars and seems to contain multiple ideas

Return ONLY valid JSON, no markdown formatting or explanation."""

        response = self._call_claude(prompt)

        try:
            # Try to parse JSON, handling potential markdown code blocks
            json_str = response
            if "```" in response:
                # Extract JSON from code block
                lines = response.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block:
                        json_lines.append(line)
                json_str = "\n".join(json_lines)

            data = json.loads(json_str)

            # Handle error response
            if "error" in data:
                return self._fallback_analysis(title, description, data.get("error", "Unknown error"))

            return FeatureIntelligence(
                title=title,
                description=description,
                complexity=Complexity(data.get("complexity", "medium")),
                estimated_hours=float(data.get("estimated_hours", 2.0)),
                confidence=float(data.get("confidence", 0.5)),
                files_affected=data.get("files_affected", []),
                foundation_score=int(data.get("foundation_score", 5)),
                foundation_reasoning=data.get("foundation_reasoning", ""),
                parallelizable=data.get("parallelizable", True),
                parallel_conflicts=data.get("parallel_conflicts", []),
                needs_expert=data.get("needs_expert", False),
                expert_domain=ExpertDomain(data.get("expert_domain", "standard")),
                expert_reasoning=data.get("expert_reasoning", ""),
                shippable_today=data.get("shippable_today", False),
                scope_creep_detected=data.get("scope_creep_detected", False),
                scope_creep_warning=data.get("scope_creep_warning", ""),
                suggested_breakdown=data.get("suggested_breakdown", []),
                suggested_tags=data.get("suggested_tags", []),
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return self._fallback_analysis(title, description, str(e))

    def _fallback_analysis(
        self,
        title: str,
        description: str,
        error: str
    ) -> FeatureIntelligence:
        """Provide a fallback analysis when Claude fails."""
        # Simple heuristics for fallback
        text = f"{title} {description}".lower()

        # Complexity heuristics
        complexity = Complexity.MEDIUM
        if len(text) > 200 or " and " in text.lower():
            complexity = Complexity.LARGE
        elif len(text) < 50:
            complexity = Complexity.SMALL

        # Scope creep detection
        scope_creep = any(phrase in text for phrase in [
            " and also ", " plus ", " additionally ", " as well as "
        ])

        return FeatureIntelligence(
            title=title,
            description=description,
            complexity=complexity,
            estimated_hours=2.0 if complexity == Complexity.SMALL else 4.0,
            confidence=0.3,  # Low confidence for fallback
            files_affected=[],
            foundation_score=5,
            foundation_reasoning=f"Fallback analysis (error: {error})",
            parallelizable=True,
            shippable_today=complexity == Complexity.SMALL,
            scope_creep_detected=scope_creep,
            scope_creep_warning="Multiple features detected" if scope_creep else "",
        )

    def quick_scope_check(self, text: str) -> dict:
        """
        Fast, local-only scope creep detection for as-you-type feedback.

        This runs instantly without calling Claude, for the VibeInput component.
        """
        text_lower = text.lower()
        warnings = []

        # Length check
        if len(text) > 100:
            warnings.append({
                "type": "length",
                "message": "This might be too big for one feature. Consider breaking it down.",
                "severity": "warning"
            })

        # Scope creep phrases
        creep_phrases = [
            (" and also ", "Scope creep detected. Focus on one thing."),
            (" plus ", "Multiple additions detected. Pick the most important."),
            (" additionally ", "Multiple features detected. Ship one first."),
            (" as well as ", "Combined scope detected. Break it down."),
        ]

        for phrase, message in creep_phrases:
            if phrase in text_lower:
                warnings.append({
                    "type": "scope_creep",
                    "message": message,
                    "severity": "warning"
                })
                break  # Only show one scope creep warning

        # Complexity indicators
        complex_words = ["refactor", "redesign", "migrate", "overhaul", "rewrite"]
        if any(word in text_lower for word in complex_words):
            warnings.append({
                "type": "complexity",
                "message": "This sounds like a large undertaking. Make sure scope is clear.",
                "severity": "info"
            })

        return {
            "has_warnings": len(warnings) > 0,
            "warnings": warnings,
            "suggested_complexity": self._heuristic_complexity(text)
        }

    def _heuristic_complexity(self, text: str) -> str:
        """Quick heuristic complexity estimate."""
        text_lower = text.lower()

        # Epic indicators
        epic_words = ["entire", "complete", "all", "everything", "whole"]
        if any(word in text_lower for word in epic_words):
            return "epic"

        # Large indicators
        large_words = ["refactor", "redesign", "migrate", "system", "architecture"]
        if any(word in text_lower for word in large_words) or len(text) > 150:
            return "large"

        # Small indicators
        small_words = ["fix", "typo", "add button", "update text", "tweak"]
        if any(word in text_lower for word in small_words) or len(text) < 40:
            return "small"

        return "medium"
