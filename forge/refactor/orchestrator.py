"""
Orchestrator Agent for Major Refactor Mode.

The orchestrator is your interactive team lead - available to chat,
modify plans, and make decisions. NOT a polling daemon.

Key responsibilities:
- Check signal files from phase/audit agents
- Help user decide what to do next
- Advance phases when audits pass
- Modify plans conversationally
- Handle handoffs when context gets tight
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..terminal import open_terminal_in_directory, Terminal
from .state import RefactorState, RefactorStatus, SessionStatus, AuditResult
from .signals import (
    Signal,
    SignalType,
    read_signals,
    read_latest_signal,
    get_signals_dir,
)


@dataclass
class SignalEvent:
    """A single signal event with timestamp for chronological display."""

    timestamp: str
    signal_type: str
    session_id: str
    summary: str  # Human-readable summary

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "signal_type": self.signal_type,
            "session_id": self.session_id,
            "summary": self.summary,
        }


@dataclass
class SignalSummary:
    """Summary of signals for display."""

    total_signals: int
    sessions_started: list[str]
    sessions_done: list[str]
    audits_passed: list[str]
    revisions_needed: list[str]
    pending_questions: list[dict]
    latest_signal: Optional[Signal]
    # Chronological timeline of all signals
    timeline: list[SignalEvent] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Format as markdown for orchestrator display."""
        lines = ["## Signal Summary\n"]

        if not self.total_signals:
            lines.append("No signals found yet.\n")
            return "\n".join(lines)

        lines.append(f"**Total signals**: {self.total_signals}\n")

        if self.sessions_started:
            lines.append(f"**Sessions started**: {', '.join(self.sessions_started)}")
        if self.sessions_done:
            lines.append(f"**Sessions done**: {', '.join(self.sessions_done)}")
        if self.audits_passed:
            lines.append(f"**Audits passed**: {', '.join(self.audits_passed)}")
        if self.revisions_needed:
            lines.append(f"**Revisions needed**: {', '.join(self.revisions_needed)}")

        if self.pending_questions:
            lines.append("\n### Pending Questions")
            for q in self.pending_questions:
                lines.append(f"- **{q['session_id']}**: {q['question']}")

        # Show chronological timeline (most recent 10)
        if self.timeline:
            lines.append("\n### Timeline (most recent)")
            for event in self.timeline[-10:]:
                lines.append(f"- `{event.timestamp[:19]}` {event.session_id}: {event.summary}")

        if self.latest_signal:
            lines.append(f"\n**Latest**: {self.latest_signal.type.value} "
                        f"from {self.latest_signal.session_id} "
                        f"at {self.latest_signal.timestamp[:19]}")

        return "\n".join(lines)


class OrchestratorSession:
    """
    Interactive supervisor for a refactor.

    The orchestrator runs in its own Claude session and:
    - Monitors signals from execution/audit agents
    - Helps the user decide what to do next
    - Can modify plans through conversation
    - Handles handoffs when context gets tight
    """

    def __init__(self, refactor_id: str, project_root: Path):
        self.refactor_id = refactor_id
        self.project_root = project_root
        self.refactor_dir = project_root / ".forge" / "refactors" / refactor_id
        self.signals_dir = get_signals_dir(self.refactor_dir)
        self.console = Console()

    def get_current_generation(self) -> int:
        """
        Parse ORCHESTRATOR_HANDOFF.md to find current generation number.

        Looks for "Generation: Orchestrator #N → #N+1" and returns N+1
        (the number AFTER the arrow, which is the incoming orchestrator's number).

        Returns 1 if no handoff file exists (first orchestrator).
        """
        handoff_path = self.refactor_dir / "ORCHESTRATOR_HANDOFF.md"
        if not handoff_path.exists():
            return 1

        content = handoff_path.read_text()

        # Look for "Generation: Orchestrator #N → #N+1"
        # The number after the arrow is the current/incoming generation
        match = re.search(r"Generation:\s*Orchestrator\s*#(\d+)\s*→\s*#(\d+)", content)
        if match:
            # Return the number AFTER the arrow (the incoming generation)
            return int(match.group(2))

        # Fallback: no generation info found, assume first
        return 1

    def read_state(self) -> Optional[RefactorState]:
        """
        Load refactor state from files.

        Returns None if state doesn't exist yet.
        """
        state_path = self.refactor_dir / "state.json"
        if not state_path.exists():
            return None
        return RefactorState.load(state_path)

    def save_state(self, state: RefactorState) -> None:
        """Save refactor state to file."""
        state_path = self.refactor_dir / "state.json"
        state.save(state_path)

    def check_signals(self) -> SignalSummary:
        """
        Look for new signal files and summarize.

        Returns a summary of all signals for display, including chronological timeline.
        """
        signals = read_signals(self.signals_dir)

        sessions_started = []
        sessions_done = []
        audits_passed = []
        revisions_needed = []
        pending_questions = []
        timeline = []

        for signal in signals:
            # Build human-readable summary for timeline
            if signal.type == SignalType.SESSION_STARTED:
                sessions_started.append(signal.session_id)
                summary = "Session started"
            elif signal.type == SignalType.SESSION_DONE:
                sessions_done.append(signal.session_id)
                commit = signal.payload.get("commit_hash", "")
                summary = f"Session done (commit: {commit})" if commit else "Session done"
            elif signal.type == SignalType.AUDIT_PASSED:
                audits_passed.append(signal.session_id)
                summary = "Audit passed"
            elif signal.type == SignalType.REVISION_NEEDED:
                revisions_needed.append(signal.session_id)
                issues = signal.payload.get("issues", [])
                summary = f"Revision needed ({len(issues)} issue{'s' if len(issues) != 1 else ''})"
            elif signal.type == SignalType.QUESTION:
                pending_questions.append({
                    "session_id": signal.session_id,
                    "question": signal.payload.get("question", "Unknown question"),
                    "options": signal.payload.get("options", []),
                })
                summary = f"Question: {signal.payload.get('question', '?')[:50]}"
            else:
                summary = signal.type.value

            timeline.append(SignalEvent(
                timestamp=signal.timestamp,
                signal_type=signal.type.value,
                session_id=signal.session_id,
                summary=summary,
            ))

        return SignalSummary(
            total_signals=len(signals),
            sessions_started=sessions_started,
            sessions_done=sessions_done,
            audits_passed=audits_passed,
            revisions_needed=revisions_needed,
            pending_questions=pending_questions,
            latest_signal=signals[-1] if signals else None,
            timeline=timeline,
        )

    def handle_signal(self, signal: Signal) -> str:
        """
        Decide what to do based on a signal.

        Returns a recommendation string for the orchestrator to present.
        """
        if signal.type == SignalType.SESSION_DONE:
            session_id = signal.session_id
            commit_hash = signal.payload.get("commit_hash", "unknown")
            summary = signal.payload.get("summary", "")

            return (
                f"Session **{session_id}** completed! (commit: {commit_hash})\n"
                f"{summary}\n\n"
                f"**Options:**\n"
                f"1. Start the next session\n"
                f"2. Run an audit on this phase\n"
                f"3. Check the work before proceeding\n"
                f"4. Modify the plan\n"
            )

        elif signal.type == SignalType.AUDIT_PASSED:
            session_id = signal.session_id
            notes = signal.payload.get("notes", "")

            return (
                f"Audit **PASSED** for {session_id}! ✅\n"
                f"{notes}\n\n"
                f"Ready to advance to the next phase.\n"
            )

        elif signal.type == SignalType.REVISION_NEEDED:
            session_id = signal.session_id
            issues = signal.payload.get("issues", [])
            suggestions = signal.payload.get("suggestions", [])

            issues_str = "\n".join(f"- {i}" for i in issues) if issues else "- No specific issues listed"
            suggestions_str = "\n".join(f"- {s}" for s in suggestions) if suggestions else ""

            return (
                f"Audit found issues with {session_id}:\n\n"
                f"**Issues:**\n{issues_str}\n\n"
                f"**Suggestions:**\n{suggestions_str}\n\n"
                f"The session needs revision.\n"
            )

        elif signal.type == SignalType.QUESTION:
            question = signal.payload.get("question", "Unknown question")
            options = signal.payload.get("options", [])

            options_str = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options)) if options else ""

            return (
                f"Session **{signal.session_id}** has a question:\n\n"
                f"> {question}\n\n"
                f"{options_str}\n\n"
                f"Please answer so the session can continue.\n"
            )

        return f"Received signal: {signal.type.value} from {signal.session_id}"

    def advance_phase(self, from_session: str, to_session: str) -> tuple[bool, str]:
        """
        Move to the next phase/session.

        Updates state to reflect the transition.
        Returns (success, message).
        """
        state = self.read_state()
        if not state:
            return False, "No refactor state found"

        # Mark the from_session as completed if not already
        if from_session in state.sessions:
            session = state.sessions[from_session]
            if session.status != SessionStatus.COMPLETED:
                session.status = SessionStatus.COMPLETED
                session.completed_at = datetime.now().isoformat()

        # Update current session
        state.current_session = to_session

        self.save_state(state)

        return True, f"Advanced from {from_session} to {to_session}"

    def update_handoff(
        self,
        notes: str = "",
        open_questions: list[str] | None = None,
        conversation_context: str = "",
        why_handoff: str = "",
    ) -> Path:
        """
        Write current state to ORCHESTRATOR_HANDOFF.md.

        This is how orchestrator context survives handoffs.
        The next orchestrator reads this file to continue.

        Args:
            notes: General notes from this session
            open_questions: List of unresolved questions/pending decisions
            conversation_context: Summary of key discussion points (not transcript)
            why_handoff: Reason for handoff (context tight, user requested, etc.)

        Note: Generation number is auto-detected from existing handoff file.
        """
        # Warn if critical fidelity fields are empty
        if not why_handoff:
            self.console.print(
                "[yellow]Warning: No handoff reason provided. "
                "Consider adding context for the next orchestrator.[/yellow]"
            )

        # Auto-detect generation from existing handoff (or 1 if first)
        generation = self.get_current_generation()

        state = self.read_state()
        signals = self.check_signals()

        # Build session status
        session_lines = []
        if state and state.sessions:
            for sid, sess in sorted(state.sessions.items()):
                status_emoji = {
                    SessionStatus.PENDING: "⬜",
                    SessionStatus.IN_PROGRESS: "🔄",
                    SessionStatus.COMPLETED: "✅",
                    SessionStatus.NEEDS_REVISION: "⚠️",
                }.get(sess.status, "❓")
                session_lines.append(f"- {status_emoji} Session {sid}: {sess.status.value}")
        else:
            session_lines.append("- No sessions tracked yet")

        # Build phase status (extract from session IDs)
        phases = {}
        if state and state.sessions:
            for sid in state.sessions:
                phase = sid.split(".")[0]
                if phase not in phases:
                    phases[phase] = []
                phases[phase].append(state.sessions[sid])

        phase_lines = []
        for phase_num, sessions in sorted(phases.items()):
            all_done = all(s.status == SessionStatus.COMPLETED for s in sessions)
            all_passed = all(s.audit_result == AuditResult.PASSED for s in sessions)
            if all_done and all_passed:
                phase_lines.append(f"- ✅ Phase {phase_num}: Complete + Audited")
            elif all_done:
                phase_lines.append(f"- 🔄 Phase {phase_num}: Complete, awaiting audit")
            else:
                phase_lines.append(f"- 🔄 Phase {phase_num}: In progress")

        # Build open questions section
        if open_questions:
            questions_str = "\n".join(f"- {q}" for q in open_questions)
        else:
            questions_str = "No open questions."

        # Build generation transition string
        next_generation = generation + 1
        generation_str = f"Orchestrator #{generation} → #{next_generation}"

        handoff_content = f'''# Orchestrator Handoff - {self.refactor_id}

> **Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Refactor**: {self.refactor_id}
> **Status**: {state.status.value if state else "unknown"}
> **Generation**: {generation_str}

---

## Why This Handoff

{why_handoff if why_handoff else "No specific reason recorded."}

---

## Conversation Context

{conversation_context if conversation_context else "No conversation context recorded."}

---

## Open Questions / Pending Decisions

{questions_str}

---

## Current State

**Current Session**: {state.current_session if state else "None"}

### Phase Progress

{chr(10).join(phase_lines) if phase_lines else "No phases tracked yet."}

### Session Details

{chr(10).join(session_lines)}

---

## Signal Summary

{signals.to_markdown()}

---

## Orchestrator Commands

**Launch a session:**
```bash
forge refactor start {self.refactor_id} <session-id>
```

**Mark session complete:**
```bash
forge refactor done <session-id>
```

**Check status:**
```bash
forge refactor status {self.refactor_id}
```

---

## Handoff Protocol

**When to handoff:** User sees context getting tight (~70%+) via `/context`

**How to trigger:** Natural language - the orchestrator will infer intent. If unclear, it will ask.

**What happens:**
1. Orchestrator updates this ORCHESTRATOR_HANDOFF.md with current state
2. User opens new Claude tab in same Warp window
3. New orchestrator reads ORCHESTRATOR_HANDOFF.md and continues
4. Old tab preserved for reference

---

## Notes from This Session

{notes if notes else "No additional notes."}

---

## Key Files

- `PHILOSOPHY.md` - Principles (stable anchor, read first!)
- `DECISIONS.md` - Architecture decisions
- `EXECUTION_PLAN.md` - All session specs
- `state.json` - Runtime state
- `signals/` - Agent signals

All paths are relative to this refactor directory.

---

## Important Context

- User is AGI-pilled: trust model judgment over hardcoded rules
- Docs as memory: write things down, context compaction loses fidelity
- User is vibecoder: don't ask deep technical questions, make the call
- Commit after each session, push to main
'''

        handoff_path = self.refactor_dir / "ORCHESTRATOR_HANDOFF.md"
        handoff_path.write_text(handoff_content)

        return handoff_path

    def get_status_summary(self) -> str:
        """
        Get a summary of the current refactor status.

        Used when orchestrator starts or user asks "check status".
        """
        state = self.read_state()
        signals = self.check_signals()

        if not state:
            return (
                f"**Refactor**: {self.refactor_id}\n"
                f"**Status**: No state found - refactor may not be started yet\n"
            )

        # Count sessions by status
        pending = sum(1 for s in state.sessions.values() if s.status == SessionStatus.PENDING)
        in_progress = sum(1 for s in state.sessions.values() if s.status == SessionStatus.IN_PROGRESS)
        completed = sum(1 for s in state.sessions.values() if s.status == SessionStatus.COMPLETED)
        needs_revision = sum(1 for s in state.sessions.values() if s.status == SessionStatus.NEEDS_REVISION)

        summary = f'''**Refactor**: {self.refactor_id}
**Status**: {state.status.value}
**Current Session**: {state.current_session or "None"}

**Sessions**: {completed} completed, {in_progress} in progress, {pending} pending
'''

        if needs_revision:
            summary += f"**⚠️ Needs Revision**: {needs_revision} session(s)\n"

        if signals.pending_questions:
            summary += f"\n**❓ Pending Questions**: {len(signals.pending_questions)}\n"

        if signals.latest_signal:
            summary += (
                f"\n**Latest Signal**: {signals.latest_signal.type.value} "
                f"from {signals.latest_signal.session_id}\n"
            )

        return summary

    def generate_orchestrator_claude_md(self) -> str:
        """
        Generate CLAUDE.md for the orchestrator session.

        This tells Claude:
        - You are the team lead / supervisor
        - How to check signals and state
        - How to help user advance phases
        - Handoff protocol
        - Plan ownership rules
        """
        from .prompts import ORCHESTRATOR_PROMPT

        status = self.get_status_summary()
        generation = self.get_current_generation()
        previous_generation = generation - 1 if generation > 1 else 0

        return ORCHESTRATOR_PROMPT.format(
            refactor_id=self.refactor_id,
            refactor_dir=self.refactor_dir,
            current_status=status,
            generation_number=generation,
            previous_generation=previous_generation,
        )

    def launch(self, terminal: str = "auto") -> tuple[bool, str]:
        """
        Launch the orchestrator session in a terminal.

        1. Create orchestrator session directory
        2. Generate CLAUDE.md in that directory
        3. Update handoff file
        4. Open terminal with Claude

        Returns (success, message).
        """
        # Ensure refactor directory exists
        if not self.refactor_dir.exists():
            return False, f"Refactor not found: {self.refactor_id}"

        # Create orchestrator session directory
        # This keeps orchestrator CLAUDE.md separate from planning CLAUDE.md
        orchestrator_dir = self.refactor_dir / "orchestrator"
        orchestrator_dir.mkdir(parents=True, exist_ok=True)

        # Generate CLAUDE.md in orchestrator directory
        claude_md_content = self.generate_orchestrator_claude_md()
        claude_md_path = orchestrator_dir / "CLAUDE.md"
        claude_md_path.write_text(claude_md_content)

        # Only create handoff file if it doesn't exist
        # Don't clobber a manually-prepared handoff from previous orchestrator
        handoff_path = self.refactor_dir / "ORCHESTRATOR_HANDOFF.md"
        if not handoff_path.exists():
            self.update_handoff()

        # Launch terminal in orchestrator directory
        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO
        claude_command = f"claude --dangerously-skip-permissions"

        # Brief tab title: "Orchestrator"
        tab_title = "Orchestrator"

        success = open_terminal_in_directory(
            directory=orchestrator_dir,
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Let's begin!",
        )

        if success:
            return True, (
                f"Orchestrator launched for {self.refactor_id}!\n\n"
                f"The orchestrator will read its CLAUDE.md and introduce itself.\n"
                f"Ask it to 'check status' to see what's happening.\n"
            )
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {orchestrator_dir}\n"
                f"  {claude_command}\n"
            )
