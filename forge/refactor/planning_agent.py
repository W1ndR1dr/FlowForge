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
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import subprocess

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

{planning_guide}

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
> To start Phase 1, run: `forge refactor start {refactor_id} 1.1`"

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

        success = open_terminal_in_directory(
            directory=refactor_dir,  # Launch IN the refactor dir so Claude reads its CLAUDE.md
            terminal=terminal_enum,
            command=claude_command,
            title=f"Forge Planning: {title}",
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
