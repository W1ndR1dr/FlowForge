"""
Execution Session management for Major Refactor Mode.

An ExecutionSession represents a single implementation session within a refactor.
It handles:
- Loading session specs from EXECUTION_PLAN.md
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
    part of the refactor plan.
    """

    def __init__(self, refactor_id: str, session_id: str, project_root: Path):
        self.refactor_id = refactor_id
        self.session_id = session_id
        self.project_root = project_root
        self.refactor_dir = project_root / ".forge" / "refactors" / refactor_id
        self.sessions_dir = self.refactor_dir / "sessions"

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

## Signaling Completion

When you've completed ALL exit criteria and committed:

1. **Run this command** to signal completion to the orchestrator:
   ```bash
   forge refactor done {self.session_id}
   ```

2. Tell the user:
   > "Session {self.session_id} complete! All exit criteria verified and committed."

The orchestrator monitors signals and will know you're done.

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
        4. Write SESSION_STARTED signal
        5. Generate CLAUDE.md
        6. Open terminal with Claude

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

        # Start the session in state
        state.start_session(self.session_id)
        state.save(state_path)

        # Write SESSION_STARTED signal
        signals_dir = get_signals_dir(self.refactor_dir)
        signal_session_started(signals_dir, self.session_id)

        # Create session directory and CLAUDE.md
        session_dir = self.sessions_dir / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        claude_md_content = self.generate_execution_claude_md(spec)
        claude_md_path = session_dir / "CLAUDE.md"
        claude_md_path.write_text(claude_md_content)

        # Launch terminal
        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO
        claude_command = "claude --dangerously-skip-permissions"

        # Brief tab title showing phase + role
        # Format: "2.2 Builder" for execution sessions
        tab_title = f"{self.session_id} Builder"

        success = open_terminal_in_directory(
            directory=session_dir,
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Let's begin!",
        )

        if success:
            return True, (
                f"Session {self.session_id} launched!\n\n"
                f"Claude will read the CLAUDE.md and begin working.\n"
                f"When done, the session will signal completion."
            )
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {session_dir}\n"
                f"  {claude_command}\n"
            )


def complete_session(
    refactor_id: str,
    session_id: str,
    project_root: Path,
    commit_hash: Optional[str] = None,
    notes: str = "",
) -> tuple[bool, str]:
    """
    Mark a session as complete.

    1. Update RefactorState
    2. Write SESSION_DONE signal
    3. Return status

    This is typically called by the execution agent when it finishes,
    or manually by the orchestrator.
    """
    refactor_dir = project_root / ".forge" / "refactors" / refactor_id
    state_path = refactor_dir / "state.json"

    if not state_path.exists():
        return False, f"No state found for refactor {refactor_id}"

    state = RefactorState.load(state_path)

    # Get commit hash from git if not provided
    if not commit_hash:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=project_root,
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

    # Write SESSION_DONE signal
    signals_dir = get_signals_dir(refactor_dir)
    signal_session_done(
        signals_dir,
        session_id,
        commit_hash=commit_hash,
        summary=notes or f"Session {session_id} completed",
    )

    return True, f"Session {session_id} marked complete (commit: {commit_hash or 'unknown'})"
