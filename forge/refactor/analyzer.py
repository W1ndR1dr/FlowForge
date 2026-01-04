"""
Codebase Analyzer for Major Refactor Mode.

Generates a goal-focused PRE_REFACTOR.md that captures the current state
of the codebase relevant to the refactor goal. This becomes the "memory"
for future execution sessions.

Philosophy: Quality over quantity. Focus on the refactor goal, not a
full codebase dump. The output should be what a new developer would need
to understand before making changes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import subprocess
import json
import fnmatch


@dataclass
class AnalysisResult:
    """Result of a codebase analysis."""

    goal: str
    executive_summary: str
    current_architecture: str
    key_files: list[dict]  # [{path, purpose, key_lines}]
    patterns_in_use: list[str]
    known_gaps: list[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_markdown(self) -> str:
        """Convert to PRE_REFACTOR.md format."""
        lines = [
            "# Pre-Refactor Codebase Analysis",
            "",
            f"> **Goal**: {self.goal}",
            f"> **Generated**: {self.generated_at[:10]}",
            ">",
            "> ## ⚠️ FOR CLAUDE CODE AGENTS",
            ">",
            "> This is a **SNAPSHOT document**.",
            "> - Line numbers may shift after code changes",
            "> - Use for **architectural understanding**, not exact references",
            "> - For execution workflow: See EXECUTION.md",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            self.executive_summary,
            "",
            "---",
            "",
            "## Current Architecture",
            "",
            self.current_architecture,
            "",
            "---",
            "",
            "## Key Files",
            "",
        ]

        # Add key files table
        if self.key_files:
            lines.append("| File | Purpose | Key Lines |")
            lines.append("|------|---------|-----------|")
            for f in self.key_files:
                path = f.get("path", "")
                purpose = f.get("purpose", "")
                key_lines = f.get("key_lines", "")
                lines.append(f"| `{path}` | {purpose} | {key_lines} |")
        else:
            lines.append("*No key files identified.*")

        lines.extend([
            "",
            "---",
            "",
            "## Patterns in Use",
            "",
        ])

        if self.patterns_in_use:
            for pattern in self.patterns_in_use:
                lines.append(f"- {pattern}")
        else:
            lines.append("*No specific patterns identified.*")

        lines.extend([
            "",
            "---",
            "",
            "## Known Gaps / Issues",
            "",
        ])

        if self.known_gaps:
            for gap in self.known_gaps:
                lines.append(f"- {gap}")
        else:
            lines.append("*No known gaps identified.*")

        lines.extend([
            "",
            "---",
            "",
            "## Summary",
            "",
            "This analysis provides context for the refactor goal. Execution sessions should:",
            "1. Read this document to understand the current state",
            "2. Reference PHILOSOPHY.md for guiding principles",
            "3. Check DECISIONS.md for approved architecture",
            "",
        ])

        return "\n".join(lines)


class CodebaseAnalyzer:
    """
    Analyzes a codebase relative to a refactor goal.

    Uses Claude CLI to intelligently identify:
    - Which files are relevant to the goal
    - What architecture patterns exist
    - Known gaps or issues to address

    The output is focused and actionable, not a dump of the entire codebase.
    """

    def __init__(
        self,
        project_root: Path,
        claude_command: str = "claude",
    ):
        self.project_root = project_root
        self.claude_command = claude_command
        self.gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> list[str]:
        """Load .gitignore patterns."""
        gitignore_path = self.project_root / ".gitignore"
        patterns = [
            # Default patterns to always ignore
            ".git",
            "__pycache__",
            "*.pyc",
            "node_modules",
            ".venv",
            "venv",
            ".forge-worktrees",
            "*.egg-info",
            "build",
            "dist",
            ".DS_Store",
        ]

        if gitignore_path.exists():
            for line in gitignore_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)

        return patterns

    def _is_ignored(self, path: Path) -> bool:
        """Check if a path matches gitignore patterns."""
        rel_path = str(path.relative_to(self.project_root))

        for pattern in self.gitignore_patterns:
            # Skip negation patterns (not supported)
            if pattern.startswith("!"):
                continue

            # Handle root-only patterns (starting with /)
            root_only = pattern.startswith("/")
            if root_only:
                pattern = pattern[1:]

            # Handle directory patterns
            if pattern.endswith("/"):
                pattern = pattern[:-1]

            # For root-only patterns, only match at the root level
            if root_only:
                first_part = rel_path.split("/")[0]
                if fnmatch.fnmatch(first_part, pattern):
                    return True
                continue

            # Check if any part of the path matches
            parts = rel_path.split("/")
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

            # Check full path match
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            if fnmatch.fnmatch(rel_path, f"**/{pattern}"):
                return True

        return False

    def _scan_structure(self, max_files: int = 200) -> list[str]:
        """Scan project structure, respecting gitignore."""
        files = []

        for path in self.project_root.rglob("*"):
            if path.is_file() and not self._is_ignored(path):
                # Only include code files
                suffix = path.suffix.lower()
                if suffix in {
                    ".py", ".swift", ".ts", ".tsx", ".js", ".jsx",
                    ".go", ".rs", ".java", ".kt", ".rb", ".php",
                    ".c", ".cpp", ".h", ".hpp", ".cs",
                    ".md", ".json", ".yaml", ".yml", ".toml",
                }:
                    rel_path = str(path.relative_to(self.project_root))
                    files.append(rel_path)

                    if len(files) >= max_files:
                        break

        return sorted(files)

    def _call_claude(self, prompt: str, timeout: int = 120) -> str:
        """Call Claude CLI with a prompt."""
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
            return "Error: Claude CLI timed out"
        except FileNotFoundError:
            return "Error: Claude CLI not found"
        except Exception as e:
            return f"Error: {e}"

    def _read_file_sample(self, path: str, max_lines: int = 100) -> str:
        """Read a sample of a file for analysis."""
        try:
            full_path = self.project_root / path
            if not full_path.exists():
                return ""

            content = full_path.read_text()
            lines = content.split("\n")

            if len(lines) <= max_lines:
                return content

            # Return first portion with truncation notice
            return "\n".join(lines[:max_lines]) + f"\n\n... (truncated, {len(lines)} total lines)"

        except Exception:
            return ""

    def analyze(self, goal: str) -> AnalysisResult:
        """
        Analyze the codebase relative to a refactor goal.

        This is the main entry point. It:
        1. Scans the file structure
        2. Uses Claude to identify relevant files
        3. Analyzes architecture patterns
        4. Identifies gaps and issues

        Returns an AnalysisResult that can be written as PRE_REFACTOR.md.
        """
        # Step 1: Scan structure
        all_files = self._scan_structure()
        file_tree = "\n".join(f"  {f}" for f in all_files[:100])

        # Step 2: Ask Claude to identify relevant files
        identify_prompt = f"""You are analyzing a codebase for a refactor.

REFACTOR GOAL: {goal}

FILE STRUCTURE (partial):
{file_tree}

Based on the refactor goal, identify the 5-15 most relevant files that would need to be understood or modified. For each file, explain why it's relevant.

Respond in this JSON format only:
{{
  "relevant_files": [
    {{"path": "path/to/file.py", "relevance": "Why this file is relevant to the goal"}}
  ]
}}"""

        identify_response = self._call_claude(identify_prompt)

        # Parse relevant files
        relevant_files = []
        try:
            # Extract JSON from response
            json_start = identify_response.find("{")
            json_end = identify_response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(identify_response[json_start:json_end])
                relevant_files = data.get("relevant_files", [])
        except json.JSONDecodeError:
            # Fallback: use first 10 files
            relevant_files = [{"path": f, "relevance": "Found in codebase"} for f in all_files[:10]]

        # Step 3: Read samples of relevant files
        file_contents = {}
        for f in relevant_files[:15]:
            path = f.get("path", "")
            if path:
                content = self._read_file_sample(path, max_lines=80)
                if content:
                    file_contents[path] = content

        # Step 4: Deep analysis with file contents
        files_context = ""
        for path, content in list(file_contents.items())[:10]:
            files_context += f"\n\n### {path}\n```\n{content[:2000]}\n```"

        analysis_prompt = f"""You are analyzing a codebase before a major refactor.

REFACTOR GOAL: {goal}

KEY FILES AND THEIR CONTENT:
{files_context}

Analyze this codebase and provide:

1. EXECUTIVE SUMMARY (2-3 paragraphs):
   - What does the relevant code currently do?
   - How is it structured?
   - What would be most important to understand before making changes?

2. CURRENT ARCHITECTURE (bullet points):
   - Key components/modules involved
   - How they interact
   - Data flow if relevant

3. KEY FILES (for each relevant file):
   - Path
   - Purpose (1 line)
   - Key lines/functions to note

4. PATTERNS IN USE:
   - Architecture patterns (MVC, event-driven, etc.)
   - Coding conventions
   - Frameworks/libraries

5. KNOWN GAPS/ISSUES:
   - What's missing that the refactor might address?
   - Potential challenges or tech debt
   - Areas that need attention

Respond in this exact JSON format:
{{
  "executive_summary": "Your summary here...",
  "current_architecture": "Bullet points here...",
  "key_files": [
    {{"path": "file.py", "purpose": "What it does", "key_lines": "Lines X-Y"}}
  ],
  "patterns_in_use": ["Pattern 1", "Pattern 2"],
  "known_gaps": ["Gap 1", "Gap 2"]
}}"""

        analysis_response = self._call_claude(analysis_prompt, timeout=180)

        # Parse analysis
        try:
            json_start = analysis_response.find("{")
            json_end = analysis_response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(analysis_response[json_start:json_end])

                return AnalysisResult(
                    goal=goal,
                    executive_summary=data.get("executive_summary", "Analysis not available."),
                    current_architecture=data.get("current_architecture", "Architecture not analyzed."),
                    key_files=data.get("key_files", []),
                    patterns_in_use=data.get("patterns_in_use", []),
                    known_gaps=data.get("known_gaps", []),
                )
        except json.JSONDecodeError:
            pass

        # Fallback result - ensure we always have some files
        fallback_files = relevant_files[:10] if relevant_files else [
            {"path": f, "relevance": "Found in codebase"} for f in all_files[:10]
        ]

        return AnalysisResult(
            goal=goal,
            executive_summary=f"Scanned {len(all_files)} files for goal: {goal}. AI analysis incomplete - Claude CLI may have timed out or returned an error. The files listed below are potentially relevant based on file structure.",
            current_architecture="Manual analysis required. Consider re-running with a more specific goal.",
            key_files=[{"path": f.get("path", f) if isinstance(f, dict) else f, "purpose": f.get("relevance", "") if isinstance(f, dict) else "", "key_lines": ""} for f in fallback_files],
            patterns_in_use=["Unable to detect patterns - manual review needed"],
            known_gaps=["AI analysis incomplete - verify results manually", "Claude CLI may need to be checked"],
        )

    def save_analysis(
        self,
        result: AnalysisResult,
        output_dir: Path,
    ) -> Path:
        """Save analysis result as PRE_REFACTOR.md."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "PRE_REFACTOR.md"
        output_path.write_text(result.to_markdown())
        return output_path


def analyze_codebase(
    project_root: Path,
    goal: str,
    output_dir: Path,
    claude_command: str = "claude",
) -> tuple[bool, str, Optional[Path]]:
    """
    Convenience function to analyze a codebase and save results.

    Returns:
        (success, message, output_path)
    """
    try:
        analyzer = CodebaseAnalyzer(project_root, claude_command)
        result = analyzer.analyze(goal)
        output_path = analyzer.save_analysis(result, output_dir)
        return True, f"Analysis saved to {output_path}", output_path
    except Exception as e:
        return False, f"Analysis failed: {e}", None
