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

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..terminal import open_terminal_in_directory, Terminal
from .state import RefactorState, AuditResult
from .signals import (
    signal_audit_passed,
    signal_revision_needed,
    get_signals_dir,
)


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
        self.session_ids = session_ids
        self.project_root = project_root
        self.refactor_dir = project_root / ".forge" / "refactors" / refactor_id
        self.signals_dir = get_signals_dir(self.refactor_dir)

    def load_philosophy(self) -> Optional[str]:
        """
        Load PHILOSOPHY.md content.

        Checks multiple locations in priority order:
        1. Refactor-specific: .forge/refactors/{id}/PHILOSOPHY.md
        2. Project docs: docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md
        """
        paths = [
            self.refactor_dir / "PHILOSOPHY.md",
            self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "PHILOSOPHY.md",
        ]

        for path in paths:
            if path.exists():
                return path.read_text()

        return None

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
        """
        import subprocess

        # Get commits from these sessions
        changes = []

        state_path = self.refactor_dir / "state.json"
        if state_path.exists():
            state = RefactorState.load(state_path)

            for session_id in self.session_ids:
                session_state = state.get_session(session_id)
                if session_state and session_state.commit_hash:
                    commit_hash = session_state.commit_hash

                    # Get diff for this commit
                    try:
                        result = subprocess.run(
                            ["git", "show", "--stat", commit_hash],
                            capture_output=True,
                            text=True,
                            cwd=self.project_root,
                        )
                        if result.returncode == 0:
                            changes.append(f"### Commit {commit_hash} (Session {session_id})\n")
                            changes.append(result.stdout[:3000])  # Truncate long diffs
                    except Exception:
                        pass

        return "\n".join(changes) if changes else "No commit information available."

    def generate_audit_claude_md(self) -> str:
        """
        Generate CLAUDE.md for the audit session.

        This tells Claude:
        - Read PHILOSOPHY.md very carefully
        - Review the session outputs
        - Validate alignment with principles
        - Report specific issues or pass
        """
        philosophy = self.load_philosophy() or "(PHILOSOPHY.md not found)"
        outputs = self.load_session_outputs()
        code_changes = self.load_code_changes()

        sessions_str = ", ".join(self.session_ids)
        outputs_str = "\n\n---\n\n".join(
            f"## Session {sid}\n\n{content}"
            for sid, content in outputs.items()
        )

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

---

## FIRST: Read Philosophy Carefully

This is the STABLE ANCHOR - the principles that must not be violated:

{philosophy}

---

## What You're Validating

Review the following session work:

{outputs_str}

---

## Code Changes Made

These are the actual commits from the sessions:

{code_changes}

---

## Your Validation Checklist

For each session, verify:

1. **Principle Alignment**
   - Does the work follow the stated principles?
   - Are any anti-patterns present?
   - Does it match the vision?

2. **Scope Compliance**
   - Did the session stay within its defined scope?
   - Was anything built that was explicitly "NOT building"?

3. **Quality Check**
   - Is the implementation complete per exit criteria?
   - Are there obvious gaps or shortcuts?

4. **Drift Detection**
   - Has the implementation drifted from the original intent?
   - Are there concerning deviations?

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
- Reference specific principles from PHILOSOPHY.md
- Suggest how to fix issues, don't just point them out
- "Good enough" is not passing - work should align with principles
- However, don't be pedantic about minor style issues

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - The philosophy is authoritative
- **Anti-patterns matter** - Detecting what NOT to do is as important as what to do
- **Iteration is expected** - Revision is normal, not failure
- **Three-layer audit** - You + User vibes + Builder self-check

---

## Begin

1. Read the philosophy section above VERY carefully
2. Review each session's work
3. Check against principles
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

        1. Generate CLAUDE.md for audit
        2. Create audit directory
        3. Open terminal with Claude

        Returns (success, message).
        """
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

    # Update state
    audit_agent.update_state_audit_result(passed=True)

    # Write signal
    audit_agent.signal_passed(notes)

    sessions_str = ", ".join(session_ids)
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

    Updates state and writes signal.
    Called by CLI command after auditor finds problems.
    """
    audit_agent = AuditAgent(refactor_id, session_ids, project_root)

    # Update state
    audit_agent.update_state_audit_result(passed=False)

    # Write signal
    audit_agent.signal_failed(issues, suggestions)

    # Mark sessions as needing revision
    state_path = project_root / ".forge" / "refactors" / refactor_id / "state.json"
    if state_path.exists():
        from .state import RefactorState, SessionStatus
        state = RefactorState.load(state_path)
        for session_id in session_ids:
            state.mark_needs_revision(session_id, notes="; ".join(issues))
        state.save(state_path)

    sessions_str = ", ".join(session_ids)
    return True, f"Audit FAILED for sessions: {sessions_str}. Revision needed."
