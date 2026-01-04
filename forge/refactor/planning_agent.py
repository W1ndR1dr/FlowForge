"""
Planning Agent for Major Refactor Mode.

The Planning Agent replaces brainstorm/refine for major refactors. Instead of
generating a spec, it launches an interactive Claude Code session that:
1. Explores the codebase
2. Asks clarifying questions (2-3 at a time, not 10)
3. Debates alternatives
4. Creates complete planning docs

Philosophy: "Docs ARE the memory" - the Planning Agent creates the docs that
all future execution agents will read.
"""

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import subprocess

from rich.console import Console

from ..terminal import open_terminal_in_directory, Terminal


@dataclass
class RefactorMetadata:
    """Metadata for a refactor planning session."""
    id: str
    title: str
    goal: str
    status: str = "planning"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RefactorMetadata":
        return cls(**data)


class PlanningAgent:
    """
    Launches and manages Planning Agent sessions for major refactors.

    The Planning Agent is an interactive Claude Code session that collaboratively
    creates refactor planning documentation with the user.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.refactors_dir = project_root / ".forge" / "refactors"

    def generate_id(self, title: str) -> str:
        """Generate a URL-safe ID from a title."""
        # Simple slug generation
        slug = title.lower()
        slug = slug.replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        slug = "-".join(filter(None, slug.split("-")))  # Remove double dashes
        return slug[:50]  # Limit length

    def create_refactor(self, title: str, goal: str) -> tuple[str, Path]:
        """
        Create a new refactor and its directory structure.

        Returns (refactor_id, refactor_dir).
        """
        refactor_id = self.generate_id(title)
        refactor_dir = self.refactors_dir / refactor_id

        if refactor_dir.exists():
            raise ValueError(f"Refactor already exists: {refactor_id}")

        # Create directory structure
        refactor_dir.mkdir(parents=True)
        (refactor_dir / "signals").mkdir()
        (refactor_dir / "phases").mkdir()

        # Create metadata
        metadata = RefactorMetadata(
            id=refactor_id,
            title=title,
            goal=goal,
        )

        metadata_path = refactor_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata.to_dict(), indent=2))

        return refactor_id, refactor_dir

    def generate_planning_claude_md(
        self,
        refactor_id: str,
        title: str,
        goal: str,
        refactor_dir: Path,
    ) -> str:
        """
        Generate a CLAUDE.md for the planning session.

        This combines:
        1. The PLANNING_PROCESS_CLAUDE.md template (the "soul")
        2. Project-specific context
        3. Output directory instructions

        The CLAUDE.md tells Claude exactly how to start - no user prompt needed.
        User just launches `claude` and it begins.
        """
        # Try to read the planning process guide
        planning_guide_path = self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "PLANNING_PROCESS_CLAUDE.md"

        if planning_guide_path.exists():
            planning_guide = planning_guide_path.read_text()
        else:
            # Fallback to embedded version if file doesn't exist
            planning_guide = self._get_embedded_planning_guide()

        # Build the session-specific CLAUDE.md
        # NOTE: This is in .forge/refactors/{id}/, so Claude also inherits
        # the project's root CLAUDE.md automatically (Claude reads parent dirs)
        claude_md = f'''# Planning Session: {title}

> **Refactor ID**: {refactor_id}
> **Goal**: {goal}
> **Output Directory**: {refactor_dir}
> **Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## IMPORTANT: How to Start This Session

When you start, **immediately begin with this**:

1. Say: "I'll help you plan the {title} refactor. Let me first explore the codebase to understand what we're working with..."

2. Then start exploring - search for relevant files, read key code, understand the current architecture.

3. After exploring, summarize what you found and ask 2-3 clarifying questions.

**Do NOT wait for user input to begin. Start exploring immediately.**

**Thinking depth**: If after initial exploration you believe this refactor is architecturally significant or involves many systems, tell the user BEFORE deep planning:

> "This refactor is complex - I'd recommend relaunching me with ultrathink enabled. Want to restart with that?"

If already appropriate for the task, just proceed.

---

## Your Mission

You are a **Planning Agent** for a major refactor. Through conversation, you will create:

1. **PHILOSOPHY.md** - Guiding principles, anti-patterns (IMMUTABLE once written)
2. **VISION.md** - Target state, success criteria
3. **DECISIONS.md** - What we decided + rejected alternatives
4. **PRE_REFACTOR.md** - Codebase analysis relevant to goal
5. **EXECUTION.md** - Phased sessions with standardized format

Write all docs to: `{refactor_dir}/`

---

## The Goal

**{goal}**

---

## Planning Flow

1. **EXPLORE FIRST** - Read the codebase before proposing anything
2. **ASK 2-3 QUESTIONS** - Not 10, not open-ended. Give options with tradeoffs.
3. **DEBATE ALTERNATIVES** - Document what you rejected and why
4. **DRAFT DOCS** - Show content, get user approval, then write
5. **END CLEARLY** - "Planning complete! Ready for Phase 1."

---

## CRITICAL: Use These Tools Liberally

**Explore Agents** - Launch multiple in parallel to understand the codebase:
```
Use Task tool with subagent_type="Explore" for:
- Understanding the feature area being modified
- Finding existing patterns and conventions
- Mapping dependencies and data flow
- Looking at reference examples
```

**AskUserQuestion Tool** - Use this frequently, not just once:
```
- Round 1: High-level vision (what should happen?)
- Round 2: User experience (how should it feel?)
- Round 3: Priorities and tradeoffs (what matters most?)
- Whenever you're uncertain about INTENT - ASK
```

---

## IMPORTANT: The User is Non-Technical

The user is a **vibecoder** - they work extensively with AI but are NOT a developer. They have strong product intuitions but can't answer deep technical questions.

**DO ask about:**
- Vision and intent ("What should happen when...")
- User experience ("How should this feel...")
- Priorities ("Is X more important than Y...")
- Business logic ("When should we...")

**DON'T ask about:**
- Implementation details ("Should we use a dict or dataclass...")
- Architecture specifics ("Should this be async or sync...")
- Code structure ("Where should this function live...")

**For technical decisions: Make the call yourself, explain your reasoning briefly, and move on.** The user trusts your technical judgment. Only ask them about intent and experience.

---

{planning_guide}

---

## Handoff Protocol

**When to handoff:** When context is getting tight (~70%+ via `/context`), or if you've been at this for a while and feel things getting fuzzy.

**Signs you might need a handoff:**
- You're repeating yourself or asking clarifying questions you already asked
- User mentions they've been at this for a while
- You're uncertain about earlier decisions
- Your responses are getting shorter or less nuanced

**Proactive checkpoint:** If you've covered significant ground (multiple major decisions, substantial doc drafts), offer:
> "We've covered a lot. Want me to do a handoff checkpoint? I'll save our progress to PLANNING_HANDOFF.md so nothing is lost, and you can continue fresh or pick up later."

**HANDS OFF - Before handoff, you MUST:**

1. **Update PLANNING_HANDOFF.md** with:
   - Conversation context (key discussion points, NOT transcript)
   - Open questions (what we haven't decided yet)
   - Decisions in progress (what we're currently debating)
   - Document status (which docs are not started/in progress/complete)
   - User preferences discovered (their philosophy, what matters to them)
   - Why you're handing off (context tight, natural break, etc.)

2. **Tell the user exactly what to do:**
   > "I've updated PLANNING_HANDOFF.md with our progress.
   >
   > **To continue in a new session:**
   > 1. Open a **new terminal tab** in this same Warp window
   > 2. Run: `forge refactor plan --resume {refactor_id}`
   >
   > The next planner will read the handoff and continue where we left off.
   > You can close this tab after the new one is running."

---

## "Where Were We?" Handler

If the user says "where were we?", "continue", "resume", or similar:

1. **Check PLANNING_HANDOFF.md** - Read it to understand prior context
2. **Announce continuity**: "I'm Planner #N for [refactor], continuing from #N-1. Let me review where we left off..."
3. **Summarize**: "Last time we were discussing [X], deciding between [Y] and [Z]. We had completed [docs] and still need to work on [docs]."
4. **Ask**: "Should we continue from there, or do you want to recap anything first?"

If PLANNING_HANDOFF.md doesn't exist but user says "where were we?", they may be returning to an interrupted session:
- Check which docs exist and their state
- Summarize what's been written
- Ask what they'd like to focus on

---

## Context-Aware Cues

**At session start:** Note your generation number. If you're Planner #2+, read PLANNING_HANDOFF.md first.

**During planning:** Periodically assess context usage mentally. If you feel things getting fuzzy or you've been going for a while, mention it:
> "We've made good progress. My context is getting fuller - want me to checkpoint to PLANNING_HANDOFF.md?"

**After major milestones:** When completing a doc draft or major decision round:
> "PHILOSOPHY.md is drafted. Good checkpoint opportunity if you want to take a break - I can save progress to PLANNING_HANDOFF.md."

**Always tell user which terminal:**
- When handing off: "Open a **new terminal tab** and run..."
- When done: "Go back to your **original terminal** (where you ran forge refactor plan)..."
- When asking user to run commands: Be explicit about which window

---

## Writing the Docs

When the user approves (says "write it", "looks good", "yes", etc.):

1. Show the content you'll write
2. Get explicit confirmation
3. Write files to `{refactor_dir}/`
4. Confirm what was written

**End with:**
> "Planning complete! Docs are in `{refactor_dir}/`.
>
> **What happens next:**
> You'll run a command that opens a **new terminal window** with the orchestrator - your guide through execution.
>
> **To launch the orchestrator (recommended):**
> ```
> forge refactor orchestrate {refactor_id}
> ```
>
> After it launches, you can close this planning terminal - the orchestrator has everything it needs.
>
> (Or to skip the orchestrator and start Phase 1 directly: `forge refactor start {refactor_id} 1.1`)"

---

## Key Principles

- **Explore before proposing** - Actually read the code, don't guess
- **Ask 2-3 questions at a time** - Iterate, don't overwhelm
- **Document rejected alternatives** - Future sessions need to know what NOT to do
- **Be conversational** - This is collaborative, not a lecture
- **Trust your judgment** - You decide what's too complex (AGI-pilled, no hardcoded thresholds)
'''

        return claude_md

    def _get_embedded_planning_guide(self) -> str:
        """Fallback planning guide if PLANNING_PROCESS_CLAUDE.md doesn't exist."""
        return '''## The Planning Process

### Phase 1: Understand the Current State

Before designing anything, explore what exists:
- Read the codebase extensively
- Understand current architecture
- Find existing patterns
- Identify what we're changing

**Key**: Don't assume. Read the code. Understand patterns.

### Phase 2: Collaborative Brainstorming

Ask questions iteratively:
- Round 1: High-level vision questions
- Round 2: Architecture questions (give 2-3 options with tradeoffs)
- Round 3: Detail questions

**Key principles**:
- Ask 2-3 questions at a time, not 10
- Give options with descriptions, not open-ended questions
- When they say "I don't know", offer your recommendation

### Phase 3: Design

For complex features, think through different aspects:
- Architecture design (how components interact)
- State/data management (what persists, how)
- UX/flow design (what user sees and does)

### Phase 4: Synthesize and Document

Create layered documentation:
1. PHILOSOPHY.md - Principles and anti-patterns (IMMUTABLE)
2. VISION.md - Target state (IMMUTABLE)
3. DECISIONS.md - What we decided and why
4. EXECUTION.md - How to build it

### Phase 5: Standardize Session Format

Every session in EXECUTION.md should have:
- Worktree: YES/NO with reasoning
- Scope: What's IN and OUT
- Start When / Stop When
- PROMPT: Copy-paste ready
- EXIT CRITERIA: Checkboxes
- GIT INSTRUCTIONS: Exact commands
- HANDOFF: What to write for next session

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Do This Instead |
|--------------|----------------|-----------------|
| Asking 10 questions at once | Overwhelming | 2-3 questions, iterate |
| Open-ended questions only | User does all thinking | Offer options with tradeoffs |
| Jumping to implementation | Misses the "why" | Document philosophy first |
| Not documenting rejected ideas | Future re-discovery | Explicit rejected alternatives |
| Vague session descriptions | Unclear execution | Standardized format |
'''

    def launch(
        self,
        title: str,
        goal: str,
        terminal: str = "auto",
    ) -> tuple[bool, str, Optional[str]]:
        """
        Launch a Planning Agent session in Warp.

        Creates the refactor directory, generates a session-specific CLAUDE.md,
        and opens a new terminal with Claude Code.

        The CLAUDE.md tells Claude exactly how to start - no user prompt needed.
        Claude reads it automatically and begins exploring.

        Returns (success, message, refactor_id).
        """
        try:
            # Create refactor
            refactor_id, refactor_dir = self.create_refactor(title, goal)
        except ValueError as e:
            return False, str(e), None

        # Generate the planning session CLAUDE.md
        claude_md_content = self.generate_planning_claude_md(
            refactor_id=refactor_id,
            title=title,
            goal=goal,
            refactor_dir=refactor_dir,
        )

        # Write CLAUDE.md to the refactor directory
        # Claude Code will read this automatically when launched in this directory
        # It also inherits the project's root CLAUDE.md (Claude reads parent dirs)
        session_claude_md = refactor_dir / "CLAUDE.md"
        session_claude_md.write_text(claude_md_content)

        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO

        # Launch Claude in the refactor directory
        # Claude reads CLAUDE.md automatically and starts immediately
        claude_command = 'claude --dangerously-skip-permissions'

        # Brief tab title: "[ShortTitle] Planner"
        # Take first 1-2 words, skip common words like "Mode", "Phase", "Implementation"
        skip_words = {'mode', 'phase', 'implementation', 'the', 'a', 'an', 'for'}
        words = [w for w in title.split() if w.lower() not in skip_words][:2]
        short_title = ''.join(words) if words else 'Refactor'
        tab_title = f"{short_title} Planner"

        success = open_terminal_in_directory(
            directory=refactor_dir,  # Launch IN the refactor dir so Claude reads its CLAUDE.md
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Let's begin!",  # Enthusiastic trigger - Claude decides thinking depth from CLAUDE.md
        )

        if success:
            return True, (
                f"Planning session launched in Warp!\n\n"
                f"Claude will read the CLAUDE.md and start exploring automatically.\n"
                f"Just wait for it to begin, then collaborate on the plan."
            ), refactor_id
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {refactor_dir}\n"
                f"  {claude_command}\n\n"
                f"Claude will read the CLAUDE.md and start automatically."
            ), refactor_id

    def list_refactors(self) -> list[RefactorMetadata]:
        """List all refactors."""
        refactors = []

        if not self.refactors_dir.exists():
            return refactors

        for refactor_dir in self.refactors_dir.iterdir():
            if not refactor_dir.is_dir():
                continue

            metadata_path = refactor_dir / "metadata.json"
            if metadata_path.exists():
                try:
                    data = json.loads(metadata_path.read_text())
                    refactors.append(RefactorMetadata.from_dict(data))
                except (json.JSONDecodeError, KeyError):
                    continue

        return refactors

    def get_refactor(self, refactor_id: str) -> Optional[RefactorMetadata]:
        """Get a specific refactor by ID."""
        metadata_path = self.refactors_dir / refactor_id / "metadata.json"

        if not metadata_path.exists():
            return None

        try:
            data = json.loads(metadata_path.read_text())
            return RefactorMetadata.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def get_refactor_dir(self, refactor_id: str) -> Optional[Path]:
        """Get the directory for a refactor."""
        refactor_dir = self.refactors_dir / refactor_id
        return refactor_dir if refactor_dir.exists() else None

    def get_current_generation(self, refactor_dir: Path) -> int:
        """
        Parse PLANNING_HANDOFF.md to find current generation number.

        Looks for "Generation: Planner #N → #N+1" and returns N+1
        (the number AFTER the arrow, which is the incoming planner's number).

        Returns 1 if no handoff file exists (first planner).
        """
        handoff_path = refactor_dir / "PLANNING_HANDOFF.md"
        if not handoff_path.exists():
            return 1

        content = handoff_path.read_text()

        # Look for "Generation: Planner #N → #N+1"
        # The number after the arrow is the current/incoming generation
        match = re.search(r"Generation:\s*Planner\s*#(\d+)\s*→\s*#(\d+)", content)
        if match:
            # Return the number AFTER the arrow (the incoming generation)
            return int(match.group(2))

        # Fallback: no generation info found, assume first
        return 1

    def update_handoff(
        self,
        refactor_id: str,
        conversation_context: str = "",
        open_questions: list[str] | None = None,
        decisions_in_progress: list[str] | None = None,
        docs_state: dict | None = None,
        user_preferences: list[str] | None = None,
        why_handoff: str = "",
    ) -> Path:
        """
        Write current planning state to PLANNING_HANDOFF.md.

        This is how Planning Agent context survives handoffs.
        The next planner reads this file to continue.

        Args:
            refactor_id: The refactor ID
            conversation_context: Summary of key discussion points (not transcript)
            open_questions: Unresolved questions or pending decisions
            decisions_in_progress: Decisions being debated but not yet final
            docs_state: Status of each planning doc (not started/in progress/complete)
            user_preferences: User preferences discovered during conversation
            why_handoff: Reason for handoff (context tight, user requested, etc.)
        """
        console = Console()

        # Path traversal protection
        if ".." in refactor_id or refactor_id.startswith("/"):
            raise ValueError(f"Invalid refactor ID: {refactor_id}")

        refactor_dir = self.refactors_dir / refactor_id

        # Additional check: ensure resolved path is under refactors_dir
        try:
            refactor_dir.resolve().relative_to(self.refactors_dir.resolve())
        except ValueError:
            raise ValueError(f"Invalid refactor ID: {refactor_id}")

        if not refactor_dir.exists():
            raise ValueError(f"Refactor not found: {refactor_id}")

        # Warn if critical fidelity fields are empty
        if not why_handoff:
            console.print(
                "[yellow]Warning: No handoff reason provided. "
                "Consider adding context for the next planner.[/yellow]"
            )

        # Auto-detect generation from existing handoff (or 1 if first)
        generation = self.get_current_generation(refactor_dir)

        # Get metadata
        metadata = self.get_refactor(refactor_id)
        title = metadata.title if metadata else refactor_id
        goal = metadata.goal if metadata else "Unknown"

        # Build docs state section
        docs_state = docs_state or {}
        default_docs = ["PHILOSOPHY.md", "VISION.md", "DECISIONS.md", "PRE_REFACTOR.md", "EXECUTION_PLAN.md"]
        docs_lines = []
        for doc in default_docs:
            status = docs_state.get(doc, "not started")
            status_emoji = {
                "not started": "⬜",
                "in progress": "🔄",
                "complete": "✅",
                "draft": "📝",
            }.get(status, "❓")
            docs_lines.append(f"- {status_emoji} {doc}: {status}")

        # Build open questions section
        if open_questions:
            questions_str = "\n".join(f"- {q}" for q in open_questions)
        else:
            questions_str = "No open questions."

        # Build decisions in progress section
        if decisions_in_progress:
            decisions_str = "\n".join(f"- {d}" for d in decisions_in_progress)
        else:
            decisions_str = "No decisions pending."

        # Build user preferences section
        if user_preferences:
            prefs_str = "\n".join(f"- {p}" for p in user_preferences)
        else:
            prefs_str = "None discovered yet."

        # Build generation transition string
        next_generation = generation + 1
        generation_str = f"Planner #{generation} → #{next_generation}"

        handoff_content = f'''# Planning Handoff - {refactor_id}

> **Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Refactor**: {title}
> **Goal**: {goal}
> **Generation**: {generation_str}

---

## IMPORTANT: Read This Before Starting

You are **Planner #{next_generation}** for the "{title}" refactor.
A previous planner has handed off to you. Read this file carefully before continuing.

Introduce yourself: "I'm Planner #{next_generation} for {title}, continuing from #{generation}. Let me review where we left off..."

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

## Decisions In Progress

These decisions were being discussed but not yet finalized:

{decisions_str}

---

## User Preferences Discovered

The previous planner learned these about the user:

{prefs_str}

---

## Document Status

{chr(10).join(docs_lines)}

---

## Planning Commands

**Resume planning:**
```bash
forge refactor plan --resume {refactor_id}
```

**Launch orchestrator (after planning complete):**
```bash
forge refactor orchestrate {refactor_id}
```

---

## Key Files

- `CLAUDE.md` - Planning session instructions (you're reading context from there too)
- `metadata.json` - Refactor metadata

Planning docs (in this directory):
- `PHILOSOPHY.md` - Principles (IMMUTABLE once written)
- `VISION.md` - Target state (IMMUTABLE once written)
- `DECISIONS.md` - What we decided + rejected alternatives
- `PRE_REFACTOR.md` - Codebase analysis
- `EXECUTION_PLAN.md` - Phased sessions

---

## Important Context

- User is AGI-pilled: trust model judgment over hardcoded rules
- Docs as memory: write things down, context compaction loses fidelity
- User is vibecoder: don't ask deep technical questions, make the call
- Ask 2-3 questions at a time, not 10
- Document rejected alternatives - future sessions need to know what NOT to do
'''

        handoff_path = refactor_dir / "PLANNING_HANDOFF.md"
        handoff_path.write_text(handoff_content)

        return handoff_path

    def resume(
        self,
        refactor_id: str,
        terminal: str = "auto",
    ) -> tuple[bool, str]:
        """
        Resume a Planning Agent session from PLANNING_HANDOFF.md.

        Launches a new Claude session that reads the handoff and continues
        where the previous planner left off.

        Returns (success, message).
        """
        # Path traversal protection: ensure refactor_id doesn't escape refactors_dir
        if ".." in refactor_id or refactor_id.startswith("/"):
            return False, f"Invalid refactor ID: {refactor_id}"

        refactor_dir = self.refactors_dir / refactor_id

        # Additional check: ensure resolved path is under refactors_dir
        try:
            refactor_dir.resolve().relative_to(self.refactors_dir.resolve())
        except ValueError:
            return False, f"Invalid refactor ID: {refactor_id}"

        if not refactor_dir.exists():
            return False, f"Refactor not found: {refactor_id}"

        handoff_path = refactor_dir / "PLANNING_HANDOFF.md"
        if not handoff_path.exists():
            return False, (
                f"No PLANNING_HANDOFF.md found for {refactor_id}.\n"
                f"Either this is a fresh planning session (use 'forge refactor plan' instead),\n"
                f"or the previous planner didn't create a handoff."
            )

        # Get generation number for display
        generation = self.get_current_generation(refactor_dir)

        # Get metadata for tab title
        metadata = self.get_refactor(refactor_id)
        title = metadata.title if metadata else refactor_id

        terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO

        # Launch Claude in the refactor directory
        claude_command = 'claude --dangerously-skip-permissions'

        # Tab title shows generation: "[ShortTitle] Planner #N"
        skip_words = {'mode', 'phase', 'implementation', 'the', 'a', 'an', 'for'}
        words = [w for w in title.split() if w.lower() not in skip_words][:2]
        short_title = ''.join(words) if words else 'Refactor'
        tab_title = f"{short_title} Planner #{generation}"

        success = open_terminal_in_directory(
            directory=refactor_dir,
            terminal=terminal_enum,
            command=claude_command,
            title=tab_title,
            initial_input="Where were we?",  # This triggers the "where were we" handler
        )

        if success:
            return True, (
                f"Planning session resumed for {refactor_id}!\n\n"
                f"Planner #{generation} will read PLANNING_HANDOFF.md and continue.\n"
                f"It will summarize where you left off."
            )
        else:
            return False, (
                f"Could not open terminal. Start manually:\n\n"
                f"  cd {refactor_dir}\n"
                f"  {claude_command}\n\n"
                f"Then say: 'Where were we?'"
            )
