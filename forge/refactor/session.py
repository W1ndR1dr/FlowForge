"""
Execution Session management for Major Refactor Mode.

An ExecutionSession represents a single implementation session within a refactor.
It handles:
- Loading session specs from EXECUTION_PLAN.md
- Creating worktrees for isolated work (when spec.worktree == True)
- Generating session-specific CLAUDE.md
- Launching Claude in terminal
- Updating RefactorState and writing signals
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..terminal import open_terminal_in_directory, Terminal
from ..worktree import WorktreeManager
from .state import RefactorState, RefactorStatus, SessionStatus
from .signals import signal_session_started, signal_session_done, get_signals_dir


@dataclass
class SessionSpec:
    """Parsed specification for an execution session."""

    session_id: str
    title: str
    worktree: bool
    scope_in: list[str]
    scope_out: list[str]
    start_when: str
    stop_when: str
    prompt: str
    ask_user_if: list[str]
    exit_criteria: list[str]
    git_instructions: str
    handoff: str

    @classmethod
    def from_markdown(cls, session_id: str, content: str) -> Optional["SessionSpec"]:
        """
        Parse a session spec from markdown content.

        Expected format matches EXECUTION_PLAN.md session structure.
        """
        # Extract title from header like "### Session 1.1: Core State & Signals"
        title_match = re.search(r"###\s+Session\s+[\d.]+:\s*(.+)", content)
        title = title_match.group(1).strip() if title_match else f"Session {session_id}"

        # Extract worktree (YES/NO)
        worktree_match = re.search(r"\*\*Worktree\*\*\s*\|\s*(YES|NO)", content, re.IGNORECASE)
        worktree = worktree_match.group(1).upper() == "YES" if worktree_match else False

        # Extract scope
        scope_match = re.search(r"\*\*Scope\*\*\s*\|\s*IN:\s*([^|]+)\.\s*OUT:\s*([^|]+)", content)
        scope_in = [scope_match.group(1).strip()] if scope_match else []
        scope_out = [scope_match.group(2).strip()] if scope_match else []

        # Extract start/stop conditions
        start_match = re.search(r"\*\*Start When\*\*\s*\|\s*([^|]+)", content)
        start_when = start_match.group(1).strip() if start_match else ""

        stop_match = re.search(r"\*\*Stop When\*\*\s*\|\s*([^|]+)", content)
        stop_when = stop_match.group(1).strip() if stop_match else ""

        # Extract prompt (between ```  blocks after **PROMPT**)
        prompt_match = re.search(
            r"\*\*PROMPT\*\*.*?```\s*\n(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE
        )
        prompt = prompt_match.group(1).strip() if prompt_match else ""

        # Extract ASK USER IF items
        ask_match = re.search(
            r"\*\*ASK USER IF\.{0,3}\*\*\s*\n((?:[-*]\s+.+\n?)+)",
            content,
            re.IGNORECASE
        )
        ask_user_if = []
        if ask_match:
            for line in ask_match.group(1).strip().split("\n"):
                line = re.sub(r"^[-*]\s+", "", line.strip())
                if line:
                    ask_user_if.append(line)

        # Extract EXIT CRITERIA items
        exit_match = re.search(
            r"\*\*EXIT CRITERIA\*\*\s*\n((?:[-*]\s+\[.\]\s+.+\n?)+)",
            content,
            re.IGNORECASE
        )
        exit_criteria = []
        if exit_match:
            for line in exit_match.group(1).strip().split("\n"):
                # Extract the text after the checkbox
                item_match = re.search(r"\[.\]\s+(.+)", line)
                if item_match:
                    exit_criteria.append(item_match.group(1).strip())

        # Extract git instructions
        git_match = re.search(
            r"\*\*GIT INSTRUCTIONS\*\*.*?```(?:bash)?\s*\n(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE
        )
        git_instructions = git_match.group(1).strip() if git_match else ""

        # Extract handoff
        handoff_match = re.search(
            r"\*\*HANDOFF\*\*\s*\n(.*?)(?=---|\*\*Files|$)",
            content,
            re.DOTALL | re.IGNORECASE
        )
        handoff = handoff_match.group(1).strip() if handoff_match else ""

        return cls(
            session_id=session_id,
            title=title,
            worktree=worktree,
            scope_in=scope_in,
            scope_out=scope_out,
            start_when=start_when,
            stop_when=stop_when,
            prompt=prompt,
            ask_user_if=ask_user_if,
            exit_criteria=exit_criteria,
            git_instructions=git_instructions,
            handoff=handoff,
        )


class ExecutionSession:
    """
    Manages execution sessions for a refactor.

    An execution session is a single Claude Code session that implements
    part of the refactor plan. When spec.worktree is True, the session
    runs in an isolated git worktree for safe parallel development.
    """

    def __init__(self, refactor_id: str, session_id: str, project_root: Path):
        self.refactor_id = refactor_id
        self.session_id = session_id
        self.project_root = project_root
        self.refactor_dir = project_root / ".forge" / "refactors" / refactor_id
        self.sessions_dir = self.refactor_dir / "sessions"
        self.worktree_manager = WorktreeManager(project_root)

    def get_worktree_id(self) -> str:
        """
        Get the worktree ID for this session.

        Format: refactor-{refactor_id}-{session_id}
        Example: refactor-major-refactor-mode-phase-1-1.1
        """
        return f"refactor-{self.refactor_id}-{self.session_id}"

    def get_worktree_path(self) -> Optional[Path]:
        """Get the worktree path if it exists."""
        return self.worktree_manager.get_worktree_path(self.get_worktree_id())

    def create_worktree(self, base_branch: str = "main") -> Path:
        """
        Create a worktree for this session.

        Returns the path to the worktree.
        """
        worktree_id = self.get_worktree_id()

        # Check if worktree already exists
        existing_path = self.worktree_manager.get_worktree_path(worktree_id)
        if existing_path:
            return existing_path

        # Create the worktree
        return self.worktree_manager.create_for_feature(
            feature_id=worktree_id,
            base_branch=base_branch,
        )

    def load_session_spec(self) -> Optional[SessionSpec]:
        """
        Load session specification from EXECUTION_PLAN.md or per-session file.

        First checks for per-session spec at sessions/{session_id}/spec.md,
        then falls back to parsing EXECUTION_PLAN.md.
        """
        # Try per-session spec file first
        session_spec_path = self.sessions_dir / self.session_id / "spec.md"
        if session_spec_path.exists():
            content = session_spec_path.read_text()
            return SessionSpec.from_markdown(self.session_id, content)

        # Fall back to EXECUTION_PLAN.md
        # Check refactor dir first, then docs/MAJOR_REFACTOR_MODE
        execution_plan_paths = [
            self.refactor_dir / "EXECUTION.md",
            self.refactor_dir / "EXECUTION_PLAN.md",
            self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "EXECUTION_PLAN.md",
        ]

        for plan_path in execution_plan_paths:
            if plan_path.exists():
                content = plan_path.read_text()
                # Find the section for this session
                session_pattern = rf"(###\s+Session\s+{re.escape(self.session_id)}.*?)(?=###\s+Session|\Z)"
                match = re.search(session_pattern, content, re.DOTALL)
                if match:
                    return SessionSpec.from_markdown(self.session_id, match.group(1))

        return None

    def generate_execution_claude_md(self, spec: SessionSpec) -> str:
        """
        Generate CLAUDE.md for this execution session.

        This tells Claude:
        - Read PHILOSOPHY.md and DECISIONS.md first
        - The session prompt and scope
        - Exit criteria to verify
        - Git instructions
        - How to signal completion
        """
        exit_criteria_str = "\n".join(f"- [ ] {item}" for item in spec.exit_criteria)
        ask_user_str = "\n".join(f"- {item}" for item in spec.ask_user_if) if spec.ask_user_if else "- No specific pause triggers for this session"

        claude_md = f'''# Execution Session: {spec.title}

> **Refactor**: {self.refactor_id}
> **Session**: {self.session_id}
> **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

{spec.prompt}

---

## Scope

**IN scope**: {", ".join(spec.scope_in) if spec.scope_in else "See prompt above"}

**OUT of scope**: {", ".join(spec.scope_out) if spec.scope_out else "See prompt above"}

---

## When to Ask the User

{ask_user_str}

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

{exit_criteria_str}

---

## Git Instructions

When all exit criteria are met:

```bash
{spec.git_instructions}
```

---

## Before Signaling Done

Perform adversarial self-review of your own code:

- [ ] **Invalid inputs**: What happens with empty, null, malicious input?
- [ ] **Path traversal**: Can `../../../` break assumptions?
- [ ] **Error paths**: What if dependencies fail? Are errors handled or swallowed?
- [ ] **Edge cases**: What if file doesn't exist? What if it's empty?
- [ ] **Dead code**: Any unused variables or unreachable branches?

Fix any issues you find. THEN signal done.

---

## Signaling Ready for Review

When you've completed ALL exit criteria, self-audited, and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done {self.session_id}
   ```

2. Tell the user:
   > "Session {self.session_id} ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session {self.session_id} complete. Return to the orchestrator to run audit and close out."

**After fixing issues from audit:**
> "Fixes applied and committed. Return to orchestrator for re-audit."

**If you're blocked or need a decision:**
> "I need guidance on [X]. Please check with the orchestrator or decide directly."

Always end your work with a clear next-step for the user.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

{spec.handoff}
'''

        return claude_md

    def launch(self, terminal: str = "auto") -> tuple[bool, str]:
        """
        Launch the execution session in a terminal.

        1. Load RefactorState
        2. Validate session can start
        3. Update state: current_session, status = executing
        4. Create worktree if spec.worktree is True
        5. Write SESSION_STARTED signal
        6. Generate CLAUDE.md (in worktree or session dir)
        7. Open terminal with Claude

        Returns (success, message).
        """
        # Load spec
        spec = self.load_session_spec()
        if not spec:
            return False, f"Could not find session spec for {self.session_id}"

        # Load or create state
        state_path = self.refactor_dir / "state.json"
        if state_path.exists():
            state = RefactorState.load(state_path)
        else:
            state = RefactorState(refactor_id=self.refactor_id)

        # Determine working directory - worktree or session dir
        worktree_path: Optional[Path] = None
        if spec.worktree:
            try:
                worktree_path = self.create_worktree()
            except (ValueError, subprocess.CalledProcessError) as e:
                error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
                return False, f"Failed to create worktree: {error_msg}"

        # Start the session in state
        state.start_session(self.session_id)
        state.save(state_path)

        # Write SESSION_STARTED signal
        signals_dir = get_signals_dir(self.refactor_dir)
        signal_session_started(
            signals_dir,
            self.session_id,
            worktree_path=str(worktree_path) if worktree_path else None,
        )

        # Create session directory for metadata/CLAUDE.md
        session_dir = self.sessions_dir / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Generate CLAUDE.md
        claude_md_content = self.generate_execution_claude_md(spec)

        # Determine where to write CLAUDE.md and launch terminal
        if worktree_path:
            # For worktree sessions, write CLAUDE.md to both locations:
            # - Worktree root (Claude reads this)
            # - Session dir (for reference/archival)
            work_dir = worktree_path
            worktree_claude_md = worktree_path / "CLAUDE.md"

            # Preserve existing CLAUDE.md if present (don't lose project instructions)
            if worktree_claude_md.exists():
                existing_content = worktree_claude_md.read_text()
                # Prepend session instructions, keep project instructions
                combined = (
                    claude_md_content +
                    "\n\n---\n\n# Original Project CLAUDE.md\n\n" +
                    existing_content
                )
                worktree_claude_md.write_text(combined)
            else:
                worktree_claude_md.write_text(claude_md_content)

            # Also save to session dir for reference
            (session_dir / "CLAUDE.md").write_text(claude_md_content)
        else:
            # For non-worktree sessions, use session directory
            work_dir = session_dir
            (session_dir / "CLAUDE.md").write_text(claude_md_content)

        # Launch terminal
        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO
        claude_command = "claude --dangerously-skip-permissions"

        # Brief tab title showing phase + role
        # Format: "2.2 Builder" for execution sessions
        tab_title = f"{self.session_id} Builder"

        success = open_terminal_in_directory(
            directory=work_dir,
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Let's begin!",
        )

        if success:
            return True, (
                f"Session {self.session_id} launched!\n\n"
                f"Working directory: {work_dir}\n"
                f"Claude will read the CLAUDE.md and begin working.\n"
                f"When done, run: forge refactor done {self.session_id}"
            )
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {work_dir}\n"
                f"  {claude_command}\n"
            )


def write_session_output(
    refactor_id: str,
    session_id: str,
    project_root: Path,
    summary: str = "",
    accomplishments: list[str] = None,
    issues: list[str] = None,
    handoff_notes: str = "",
) -> Path:
    """
    Write output.md for a completed session.

    This documents what the session accomplished for audit review.
    Written to: .forge/refactors/{id}/sessions/{session}/output.md

    Returns the path to the output file.
    """
    refactor_dir = project_root / ".forge" / "refactors" / refactor_id
    session_dir = refactor_dir / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    output_path = session_dir / "output.md"

    accomplishments_str = "\n".join(f"- {a}" for a in (accomplishments or []))
    issues_str = "\n".join(f"- {i}" for i in (issues or []))

    content = f"""# Session {session_id} Output

> **Completed**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Summary

{summary or "Session completed."}

## Accomplishments

{accomplishments_str or "- See commit for details"}

## Issues Encountered

{issues_str or "- None"}

## Handoff Notes

{handoff_notes or "Ready for next session."}
"""

    output_path.write_text(content)
    return output_path


def complete_session(
    refactor_id: str,
    session_id: str,
    project_root: Path,
    commit_hash: Optional[str] = None,
    notes: str = "",
    write_output: bool = True,
) -> tuple[bool, str]:
    """
    Mark a session as complete.

    1. Update RefactorState
    2. Write output.md (if write_output=True)
    3. Write SESSION_DONE signal
    4. Return status

    This is typically called by the execution agent when it finishes,
    or manually by the orchestrator.
    """
    refactor_dir = project_root / ".forge" / "refactors" / refactor_id
    state_path = refactor_dir / "state.json"

    if not state_path.exists():
        return False, f"No state found for refactor {refactor_id}"

    state = RefactorState.load(state_path)

    # Check for worktree and get commit hash from there if applicable
    session = ExecutionSession(refactor_id, session_id, project_root)
    worktree_path = session.get_worktree_path()
    git_cwd = worktree_path if worktree_path else project_root

    # Get commit hash from git if not provided
    if not commit_hash:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=git_cwd,
            )
            if result.returncode == 0:
                commit_hash = result.stdout.strip()[:7]
        except Exception:
            pass

    # Complete the session
    try:
        state.complete_session(session_id, commit_hash=commit_hash, notes=notes)
        state.save(state_path)
    except ValueError as e:
        return False, str(e)

    # Write output.md
    if write_output:
        write_session_output(
            refactor_id=refactor_id,
            session_id=session_id,
            project_root=project_root,
            summary=notes or f"Session {session_id} completed",
            handoff_notes=notes,
        )

    # Write SESSION_DONE signal
    signals_dir = get_signals_dir(refactor_dir)
    signal_session_done(
        signals_dir,
        session_id,
        commit_hash=commit_hash,
        summary=notes or f"Session {session_id} completed",
    )

    worktree_msg = f" (worktree: {worktree_path.name})" if worktree_path else ""
    return True, f"Session {session_id} marked complete (commit: {commit_hash or 'unknown'}){worktree_msg}"
