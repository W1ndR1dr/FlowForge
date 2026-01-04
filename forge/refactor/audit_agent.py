"""
Audit Agent for Major Refactor Mode.

The Audit Agent is the GUARDIAN of idea fidelity. It prevents drift by:
- Reading PHILOSOPHY.md (the stable anchor)
- Reading phase/session outputs
- Validating that work aligns with principles
- Signaling pass/fail with specific feedback

Key insight: Audits catch structural issues. Combined with user's "vibes check",
this creates a two-layer validation system.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..terminal import open_terminal_in_directory, Terminal
from .state import RefactorState, AuditResult
from .signals import (
    signal_audit_passed,
    signal_revision_needed,
    signal_escalation_needed,
    get_signals_dir,
)


def sanitize_session_id(session_id: str) -> str:
    """
    Sanitize a session ID to prevent path traversal and injection.

    Only allows: alphanumeric, dots, dashes, underscores.
    """
    # Remove any path traversal attempts
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', session_id)
    # Prevent .. sequences
    sanitized = re.sub(r'\.\.+', '.', sanitized)
    return sanitized


def validate_refactor_exists(refactor_dir: Path) -> bool:
    """Check if a refactor directory exists and has a state file."""
    return refactor_dir.exists() and (refactor_dir / "state.json").exists()


@dataclass
class AuditSpec:
    """Specification for an audit session."""

    refactor_id: str
    session_ids: list[str]  # Sessions to audit (a "group")
    philosophy_path: Path
    outputs: dict[str, str]  # session_id -> output content


@dataclass
class AuditIssue:
    """A specific issue found during audit."""

    session_id: str
    principle_violated: str
    description: str
    severity: str  # "critical" | "warning" | "note"
    suggestion: str


class AuditAgent:
    """
    Validates completed session work against PHILOSOPHY.md.

    The audit agent runs as a fresh Claude session that:
    1. Reads PHILOSOPHY.md carefully
    2. Reads output from completed sessions
    3. Validates alignment with principles
    4. Reports issues or passes the audit

    Design: One audit agent per phase group (related sessions share context).
    """

    def __init__(
        self,
        refactor_id: str,
        session_ids: list[str],
        project_root: Path
    ):
        self.refactor_id = refactor_id
        # Sanitize session IDs to prevent path traversal
        self.session_ids = [sanitize_session_id(sid) for sid in session_ids if sid.strip()]
        self.project_root = project_root
        self.refactor_dir = project_root / ".forge" / "refactors" / refactor_id
        self.signals_dir = get_signals_dir(self.refactor_dir)

    def exists(self) -> bool:
        """Check if the refactor exists."""
        return validate_refactor_exists(self.refactor_dir)

    def load_philosophy(self) -> tuple[Optional[str], Optional[Path]]:
        """
        Load PHILOSOPHY.md content and report which file was used.

        Checks multiple locations in priority order:
        1. Refactor-specific: .forge/refactors/{id}/PHILOSOPHY.md
        2. Project docs: docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md

        Returns:
            (content, source_path) tuple. Both None if not found.
        """
        paths = [
            self.refactor_dir / "PHILOSOPHY.md",
            self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "PHILOSOPHY.md",
        ]

        for path in paths:
            if path.exists():
                return path.read_text(), path

        return None, None

    def load_decisions(self) -> tuple[Optional[str], Optional[Path]]:
        """
        Load DECISIONS.md content and report which file was used.

        Checks multiple locations in priority order:
        1. Refactor-specific: .forge/refactors/{id}/DECISIONS.md
        2. Project docs: docs/MAJOR_REFACTOR_MODE/DECISIONS.md

        Returns:
            (content, source_path) tuple. Both None if not found.
        """
        paths = [
            self.refactor_dir / "DECISIONS.md",
            self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "DECISIONS.md",
        ]

        for path in paths:
            if path.exists():
                return path.read_text(), path

        return None, None

    def load_session_outputs(self) -> dict[str, str]:
        """
        Load outputs from completed sessions.

        Looks for:
        1. sessions/{session_id}/output.md
        2. sessions/{session_id}/CLAUDE.md (for context)
        3. Git commits/changes made by the session

        Returns dict of session_id -> combined output content.
        """
        outputs = {}

        for session_id in self.session_ids:
            session_dir = self.refactor_dir / "sessions" / session_id
            content_parts = []

            # Check for output.md (explicit session output)
            output_path = session_dir / "output.md"
            if output_path.exists():
                content_parts.append(f"## Output from Session {session_id}\n\n")
                content_parts.append(output_path.read_text())

            # Check for session CLAUDE.md (what was the mission)
            claude_md_path = session_dir / "CLAUDE.md"
            if claude_md_path.exists():
                content_parts.append(f"\n## Session {session_id} Instructions\n\n")
                content_parts.append(claude_md_path.read_text())

            # Check state.json for session notes
            state_path = self.refactor_dir / "state.json"
            if state_path.exists():
                state = RefactorState.load(state_path)
                session_state = state.get_session(session_id)
                if session_state and session_state.notes:
                    content_parts.append(f"\n## Session {session_id} Notes\n\n")
                    content_parts.append(session_state.notes)

            if content_parts:
                outputs[session_id] = "\n".join(content_parts)
            else:
                outputs[session_id] = f"No output found for session {session_id}"

        return outputs

    def load_code_changes(self) -> str:
        """
        Load actual code changes made by the sessions.

        Uses git to find what was changed, so the audit can validate
        the actual implementation, not just documented outputs.

        Includes both stats AND actual patches so auditor can see the code.
        """
        import subprocess

        # Get commits from these sessions
        changes = []
        max_lines_per_commit = 500  # Intelligent truncation per commit
        total_lines = 0
        max_total_lines = 1500  # Cap total output

        state_path = self.refactor_dir / "state.json"
        if state_path.exists():
            state = RefactorState.load(state_path)

            for session_id in self.session_ids:
                if total_lines >= max_total_lines:
                    changes.append("\n... (truncated, too many changes to show)")
                    break

                session_state = state.get_session(session_id)
                if session_state and session_state.commit_hash:
                    commit_hash = session_state.commit_hash

                    # Get diff with actual patch content
                    try:
                        result = subprocess.run(
                            ["git", "show", "--stat", "--patch", commit_hash],
                            capture_output=True,
                            text=True,
                            cwd=self.project_root,
                        )
                        if result.returncode == 0:
                            changes.append(f"### Commit {commit_hash} (Session {session_id})\n")
                            # Truncate per-commit but show actual code
                            lines = result.stdout.split('\n')
                            truncated = lines[:max_lines_per_commit]
                            changes.append('\n'.join(truncated))
                            if len(lines) > max_lines_per_commit:
                                changes.append(f"\n... ({len(lines) - max_lines_per_commit} more lines)")
                            total_lines += min(len(lines), max_lines_per_commit)
                    except Exception:
                        pass

        return "\n".join(changes) if changes else "No commit information available."

    def _get_iteration_context(self) -> tuple[int, str]:
        """
        Get iteration count and context string for audit.

        Returns:
            (max_iteration_count, context_string)
        """
        state_path = self.refactor_dir / "state.json"
        max_iter = 0
        iter_details = []

        if state_path.exists():
            state = RefactorState.load(state_path)
            for session_id in self.session_ids:
                session = state.get_session(session_id)
                if session:
                    iter_details.append(f"- Session {session_id}: iteration #{session.iteration_count}")
                    max_iter = max(max_iter, session.iteration_count)

        context = "\n".join(iter_details) if iter_details else "- No iteration data available"
        return max_iter, context

    def generate_audit_claude_md(self) -> str:
        """
        Generate CLAUDE.md for the audit session.

        This tells Claude:
        - Read PHILOSOPHY.md very carefully
        - Review the session outputs
        - Validate alignment with principles
        - Report specific issues or pass
        """
        philosophy, philosophy_path = self.load_philosophy()
        philosophy_content = philosophy or "(PHILOSOPHY.md not found)"
        philosophy_source = str(philosophy_path) if philosophy_path else "not found"

        decisions, decisions_path = self.load_decisions()
        decisions_content = decisions or "(DECISIONS.md not found)"
        decisions_source = str(decisions_path) if decisions_path else "not found"

        outputs = self.load_session_outputs()
        code_changes = self.load_code_changes()

        max_iteration, iteration_details = self._get_iteration_context()

        sessions_str = ", ".join(self.session_ids)
        outputs_str = "\n\n---\n\n".join(
            f"## Session {sid}\n\n{content}"
            for sid, content in outputs.items()
        )

        # Build escalation guidance based on iteration count
        escalation_section = ""
        if max_iteration > 0:
            escalation_section = f"""
---

## Iteration Context

**This is audit iteration #{max_iteration + 1}** for these sessions.

{iteration_details}

If you observe:
- Same issues recurring across iterations
- Fundamental architectural mismatch with philosophy
- Scope confusion that revision won't fix

...you may signal escalation instead of another revision:
```bash
forge refactor escalate {self.refactor_id} {sessions_str} --reason "Brief explanation"
```

Use your judgment. Escalation is not failure - it means human intervention is needed.
"""

        return f'''# Audit Session

> **Refactor**: {self.refactor_id}
> **Sessions Under Review**: {sessions_str}
> **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Your Role: Guardian of Idea Fidelity

You are the **Audit Agent** - your job is to prevent drift and ensure the implementation
aligns with the original vision and principles.

**Key insight**: You're catching structural issues. The user will also do a "vibes check"
to catch feel/intent issues. Together, you form a two-layer validation system.
{escalation_section}
---

## FIRST: Read Philosophy Carefully

> **Source**: `{philosophy_source}`

This is the STABLE ANCHOR - the principles that must not be violated:

{philosophy_content}

---

## Architecture Decisions

> **Source**: `{decisions_source}`

Check that approved decisions from DECISIONS.md are followed:

{decisions_content}

---

## What You're Validating

Review the following session work:

{outputs_str}

---

## Code Changes Made

These are the actual commits from the sessions:

{code_changes}

---

## What to Check

Review against these areas, using your judgment on what matters for THIS session:

**From PHILOSOPHY.md:**
- Docs as memory (updates files, not just conversation?)
- File-based signals (no IPC/WebSocket complexity?)
- Iteration-friendly (handles revision gracefully?)
- Anti-patterns avoided?

**From DECISIONS.md:**
- Follows approved architecture decisions?
- Avoids explicitly rejected approaches?

**Quality:**
- Complete per exit criteria?
- Obvious gaps or shortcuts?
- Does the code match the documented intent?

This is a guide, not a gate. Use your judgment on severity and relevance.

---

## How to Report

### If Issues Found:

1. Create `audit-results/issues.md` with specific issues:
   ```markdown
   # Audit Issues - {sessions_str}

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail {self.refactor_id} {sessions_str} --issues "Brief summary of issues"
   ```

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass {self.refactor_id} {sessions_str}
   ```

2. Tell the user:
   > "Audit PASSED for sessions {sessions_str}. Work aligns with philosophy."

---

## Important Notes

- Be specific about what doesn't align and WHY
- Reference specific principles from PHILOSOPHY.md or DECISIONS.md
- Suggest how to fix issues, don't just point them out
- Don't be pedantic about minor style issues
- Iteration is expected - revision is normal, not failure

---

## Begin

1. Read the philosophy and decisions sections above CAREFULLY
2. Review each session's work and code changes
3. Check against principles using your judgment
4. Report your findings
'''

    def write_issues(
        self,
        issues: list[AuditIssue],
        iteration: int = 1
    ) -> Path:
        """
        Write issues.md with audit findings.

        Organized by severity: Critical → Warnings → Notes
        """
        # Create audit-results directory
        results_dir = self.refactor_dir / "audit-results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Group by severity
        critical = [i for i in issues if i.severity == "critical"]
        warnings = [i for i in issues if i.severity == "warning"]
        notes = [i for i in issues if i.severity == "note"]

        sessions_str = ", ".join(self.session_ids)

        content = f'''# Audit Issues - Sessions {sessions_str}

> **Iteration**: {iteration}
> **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Sessions**: {sessions_str}

---

'''

        if critical:
            content += "## Critical Issues\n\n"
            content += "These MUST be fixed before proceeding:\n\n"
            for issue in critical:
                content += f"### [{issue.session_id}] {issue.principle_violated}\n\n"
                content += f"{issue.description}\n\n"
                content += f"**Suggestion:** {issue.suggestion}\n\n"

        if warnings:
            content += "## Warnings\n\n"
            content += "These should be addressed:\n\n"
            for issue in warnings:
                content += f"- **[{issue.session_id}]** {issue.description}\n"
                content += f"  - Principle: {issue.principle_violated}\n"
                content += f"  - Suggestion: {issue.suggestion}\n\n"

        if notes:
            content += "## Notes\n\n"
            content += "Minor observations:\n\n"
            for issue in notes:
                content += f"- [{issue.session_id}] {issue.description}\n"

        if not issues:
            content += "No issues found! Audit passed.\n"

        # Write to iteration-specific file
        issues_path = results_dir / f"issues-iteration-{iteration}.md"
        issues_path.write_text(content)

        # Also write to latest issues.md
        latest_path = results_dir / "issues.md"
        latest_path.write_text(content)

        return issues_path

    def signal_passed(self, notes: str = "") -> Path:
        """Signal that the audit passed."""
        sessions_str = ", ".join(self.session_ids)
        return signal_audit_passed(
            self.signals_dir,
            sessions_str,
            notes=notes or f"Audit passed for sessions: {sessions_str}",
        )

    def signal_failed(self, issues: list[str], suggestions: list[str] = None) -> Path:
        """Signal that the audit found issues requiring revision."""
        sessions_str = ", ".join(self.session_ids)
        return signal_revision_needed(
            self.signals_dir,
            sessions_str,
            issues=issues,
            suggestions=suggestions or [],
        )

    def update_state_audit_result(self, passed: bool) -> None:
        """Update session states with audit result."""
        state_path = self.refactor_dir / "state.json"
        if not state_path.exists():
            return

        state = RefactorState.load(state_path)

        for session_id in self.session_ids:
            session = state.get_session(session_id)
            if session:
                session.audit_result = AuditResult.PASSED if passed else AuditResult.FAILED

        state.save(state_path)

    def launch(self, terminal: str = "auto") -> tuple[bool, str]:
        """
        Launch the audit session in a terminal.

        1. Validate refactor exists
        2. Generate CLAUDE.md for audit
        3. Create audit directory
        4. Open terminal with Claude

        Returns (success, message).
        """
        # Validate refactor exists
        if not self.exists():
            return False, f"Refactor not found: {self.refactor_id}"

        # Validate we have sessions to audit
        if not self.session_ids:
            return False, "No valid session IDs provided"

        # Create audit session directory
        sessions_str = "-".join(self.session_ids)
        audit_dir = self.refactor_dir / "audit-sessions" / sessions_str
        audit_dir.mkdir(parents=True, exist_ok=True)

        # Generate CLAUDE.md
        claude_md_content = self.generate_audit_claude_md()
        claude_md_path = audit_dir / "CLAUDE.md"
        claude_md_path.write_text(claude_md_content)

        # Launch terminal
        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO
        claude_command = "claude --dangerously-skip-permissions"

        # Tab title: "Audit X.Y"
        tab_title = f"Audit {sessions_str}"

        success = open_terminal_in_directory(
            directory=audit_dir,
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Let's begin the audit!",
        )

        if success:
            return True, (
                f"Audit session launched for {sessions_str}!\n\n"
                f"Claude will read PHILOSOPHY.md and validate the work.\n"
                f"It will signal pass/fail when complete."
            )
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {audit_dir}\n"
                f"  {claude_command}\n"
            )


def record_audit_pass(
    refactor_id: str,
    session_ids: list[str],
    project_root: Path,
    notes: str = "",
) -> tuple[bool, str]:
    """
    Record that an audit passed.

    Updates state and writes signal.
    Called by CLI command after auditor approves.
    """
    audit_agent = AuditAgent(refactor_id, session_ids, project_root)

    # Validate refactor exists
    if not audit_agent.exists():
        return False, f"Refactor not found: {refactor_id}"

    # Validate we have sessions to audit
    if not audit_agent.session_ids:
        return False, "No valid session IDs provided"

    # Update state
    audit_agent.update_state_audit_result(passed=True)

    # Write signal
    audit_agent.signal_passed(notes)

    sessions_str = ", ".join(audit_agent.session_ids)
    return True, f"Audit PASSED for sessions: {sessions_str}"


def record_audit_fail(
    refactor_id: str,
    session_ids: list[str],
    project_root: Path,
    issues: list[str],
    suggestions: list[str] = None,
) -> tuple[bool, str]:
    """
    Record that an audit found issues.

    Updates state, increments iteration count, and writes signal.
    Called by CLI command after auditor finds problems.
    """
    audit_agent = AuditAgent(refactor_id, session_ids, project_root)

    # Validate refactor exists
    if not audit_agent.exists():
        return False, f"Refactor not found: {refactor_id}"

    # Validate we have sessions to audit
    if not audit_agent.session_ids:
        return False, "No valid session IDs provided"

    # Update state
    audit_agent.update_state_audit_result(passed=False)

    # Write signal
    audit_agent.signal_failed(issues, suggestions)

    # Mark sessions as needing revision and increment iteration count
    state_path = project_root / ".forge" / "refactors" / refactor_id / "state.json"
    iteration_counts = []
    if state_path.exists():
        from .state import RefactorState, SessionStatus
        state = RefactorState.load(state_path)
        for session_id in audit_agent.session_ids:
            # Increment iteration count (auditor uses this to decide escalation)
            count = state.increment_iteration(session_id)
            iteration_counts.append(f"{session_id}→#{count}")
            state.mark_needs_revision(session_id, notes="; ".join(issues))
        state.save(state_path)

    sessions_str = ", ".join(audit_agent.session_ids)
    iter_str = ", ".join(iteration_counts) if iteration_counts else ""
    return True, f"Audit FAILED for sessions: {sessions_str}. Iteration: {iter_str}. Revision needed."


def record_escalation(
    refactor_id: str,
    session_ids: list[str],
    project_root: Path,
    reason: str,
) -> tuple[bool, str]:
    """
    Record that human escalation is needed.

    Called by auditor when:
    - Same issues keep recurring across iterations
    - Fundamental architectural mismatch with philosophy
    - Scope confusion that revision won't fix

    This signals that the issue can't be fixed by another revision cycle.
    """
    audit_agent = AuditAgent(refactor_id, session_ids, project_root)

    # Validate refactor exists
    if not audit_agent.exists():
        return False, f"Refactor not found: {refactor_id}"

    # Validate we have sessions
    if not audit_agent.session_ids:
        return False, "No valid session IDs provided"

    # Get current iteration count for context
    state_path = project_root / ".forge" / "refactors" / refactor_id / "state.json"
    max_iteration = 0
    if state_path.exists():
        state = RefactorState.load(state_path)
        for session_id in audit_agent.session_ids:
            session = state.get_session(session_id)
            if session:
                max_iteration = max(max_iteration, session.iteration_count)

    # Write escalation signal
    sessions_str = ", ".join(audit_agent.session_ids)
    signal_escalation_needed(
        audit_agent.signals_dir,
        sessions_str,
        iteration_count=max_iteration,
        reason=reason,
    )

    return True, f"ESCALATION signaled for sessions: {sessions_str}. Reason: {reason}"
