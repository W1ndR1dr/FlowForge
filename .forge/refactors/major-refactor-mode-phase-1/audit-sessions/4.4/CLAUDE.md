# Audit Session

> **Refactor**: major-refactor-mode-phase-1
> **Sessions Under Review**: 4.4
> **Generated**: 2026-01-03 23:19

---

## Your Role: Guardian of Idea Fidelity

You are the **Audit Agent** - your job is to prevent drift and ensure the implementation
aligns with the original vision and principles.

**Key insight**: You're catching structural issues. The user will also do a "vibes check"
to catch feel/intent issues. Together, you form a two-layer validation system.

---

## FIRST: Read Philosophy Carefully

> **Source**: `/Users/Brian/Projects/Active/Forge/docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md`

This is the STABLE ANCHOR - the principles that must not be violated:

# Major Refactor Mode - Philosophy

> **Status**: STABLE ANCHOR - Core principles (change requires explicit pivot)
> **Purpose**: Guiding principles that govern all implementation decisions

---

## The Core Problem

Claude Code sessions have ~200k token context. A fresh session starts at ~67k (33%) just from system prompts, tools, and CLAUDE.md. Major refactors require more context than one session can hold, and **context compaction kills nuance and idea fidelity**.

This feature exists to break that barrier.

---

## The AGI-Pilled Vision

### 1. Unhobble the Model
Let Claude decide when something is too big for one session. Don't impose rigid heuristics - trust model judgment. This approach improves as models improve.

### 2. Forward-Looking Architecture
Design as if "this is the worst the models will ever be." Avoid scaffolding that assumes current limitations are permanent. Tag temporary constraints with `CONTEXT_LIMIT` so they can be removed later.

### 3. Docs as Memory, Not Conversation
The planning documents ARE the persistent context. Agents start fresh, read docs, do work, update docs. No accumulated conversation to compact.

### 4. Orchestrator as Supervisor, Not Daemon
The orchestrator is your interactive team lead - available to chat, modify plans, make decisions. Not a polling script running in the background.

---

## Key Insight: Your Bandwidth is the Bottleneck

The dependency graph doesn't determine parallelization - **YOU do**.

Even if phases could run in parallel, sometimes you only have mental bandwidth for one thing. The system should ask "run these in parallel or one at a time?" and respect your answer.

Never automate away human agency. Enable it.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Do This Instead |
|--------------|----------------|-----------------|
| Polling daemon | Adds complexity, uses resources, not interactive | Interactive supervisor that waits for signals |
| Hardcoded approval gates | Real approvals are dynamic, based on audit findings | Audit-based approval that adapts |
| Single audit agent for whole refactor | Context compaction over long refactor | Hybrid: one per phase group, fresh for milestones |
| Fixed parallelization | User bandwidth varies, should be runtime choice | Ask user at runtime |
| Implementation details in brainstorm | Refine is for WHAT and WHY, not HOW | Keep brainstorm focused on user intent |
| Assuming current model limits are permanent | Design for capability improvement | Tag limits, design for removal |
| Complex IPC/message queues | Fragile, hard to debug | Simple file-based signals |

---

## What We're NOT Building

| Explicitly Rejected | Rationale |
|---------------------|-----------|
| Project management tool | This is agent orchestration, not Jira |
| Automatic everything | Human remains in control, can pause/modify anytime |
| WebSocket/IPC communication | Files are simpler, debuggable, survive crashes |
| IDE integration | Terminal-native, Warp-first |
| Hardcoded complexity thresholds | Model judgment is better and improves |

---

## The Vibecoder Promise

Forge users work extensively with AI but may not be Git experts. Major Refactor Mode should feel like having a capable team lead who:

- Understands the big picture
- Coordinates the agents doing the work
- Keeps you informed without overwhelming
- Lets you pause, rethink, and change direction anytime
- Never loses track of where you are

**The user should never feel lost or out of control.**

---

## User as Fidelity Sensor (The Vibes Check)

Formal audits catch structural issues. **User intuition catches "feels wrong."**

The vibecoder doesn't debug code - they notice when:
- Something feels too risky to yolo
- The language is too prescriptive (not AGI-pilled)
- The approach has drifted from original intent
- "MVP acceptable" is lazy thinking

This is irreplaceable. No audit agent replicates it. Formalize it:

| Layer | What It Catches |
|-------|-----------------|
| Builder self-check | Obvious bugs, missing features |
| Formal auditor | Spec compliance, edge cases |
| **User vibes check** | Fidelity drift, philosophy violations, "feels off" |

**When vibes are off, pause.** The user's instinct is a signal. Trust it.

---

## Sessions Are Iterative, Not One-Shot

The spec assumes: build → commit → done.

Reality: build → audit → fix → audit → polish → done.

**Expect 1-3 revision passes per session.** This is normal, not failure. Build agents should welcome audit feedback and iterate until polished.

---

## Testing in AI-Assisted Development

Tests are **one signal among many**, not the source of truth.

| Layer | What It Catches | Gameable? |
|-------|-----------------|-----------|
| Builder self-check | Obvious bugs | Yes - same model, same blindspots |
| Formal auditor | Spec compliance | Harder - fresh context |
| **User vibes** | "Feels wrong" | **Ungameable** - human intuition |

The user vibes layer is the key. It's the oracle that can't be optimized against because it emerges from human intuition, not a formal specification.

**Where tests fit:**
- **Spec-first tests**: Written BEFORE implementation (defines target, not hackable)
- **Regression tests**: Catches breaks over time (safety net)
- **Integration tests**: Validates system behavior (harder to game)

**Anti-pattern**: Treating "tests pass" as proof of correctness. LLMs can optimize for metrics (coverage, green checkmarks) rather than actual correctness. This is reward hacking.

**The synthesis:**
```
Three-Layer Audit (alignment, intent)
        +
Spec-First Tests (behavior, regression)
        =
Complete quality picture
```

---

## Quality for Vibecoders

You don't need to understand tests. Your job is simpler:

1. **Describe what you want** (natural language)
2. **Vibes check** - does the result feel right?
3. **Pause when something feels off** (trust your instinct)

The three-layer audit handles the rest:

| Layer | Who Does It | Your Role |
|-------|-------------|-----------|
| Builder self-check | AI | None - handled for you |
| Formal auditor | AI | None - validates technical correctness |
| **User vibes** | You | Does this match your intent? |

Tests are an implementation detail you never see. The AI might generate them internally for regression safety, but that's not your concern.

**Your intuition is the ungameable oracle. Trust it.**

---

## Design Principles (Reference)

1. **Docs ARE the memory** - No accumulated context, agents read from files
2. **File-based communication** - Survives crashes, human-inspectable
3. **Hybrid audit lifecycle** - Fresh per phase group, avoids compaction
4. **Vibecoders first** - Hide complexity, show progress
5. **Pause anywhere** - User can always stop, rethink, modify
6. **Forward-looking** - Model unhobbling, assume capabilities improve
7. **Three-layer audit** - Builder self-check → Formal auditor → User vibes
8. **Iteration is expected** - Sessions polish through revision, not one-shot


---

## Architecture Decisions

> **Source**: `/Users/Brian/Projects/Active/Forge/docs/MAJOR_REFACTOR_MODE/DECISIONS.md`

Check that approved decisions from DECISIONS.md are followed:

# Major Refactor Mode - Implementation Decisions

> **Status**: Approved architecture
> **Created**: 2026-01-03
>
> ## For Claude Code Sessions
>
> This doc contains **approved architectural decisions**. Don't re-litigate unless user requests.
> For execution workflow, see `EXECUTION_PLAN.md`

---

## Executive Summary

Major Refactor Mode uses file-based agent coordination with "docs as memory" to enable multi-phase refactors that exceed single-session context limits. The orchestrator is an interactive supervisor (not a daemon), and you control parallelization at runtime.

---

## Key Decisions

### Decision 1: Orchestrator Model

**Rejected**: Polling daemon that runs in background, checks state every N seconds

**Why rejected**: Not interactive. Can't modify plans on the fly. Adds complexity without benefit.

**Approved**: Interactive supervisor in Warp terminal window that:
- Waits for signals from audit agents
- Asks you what to do next
- Lets you chat with it anytime to modify the plan
- Handles handoffs if context gets constrained

### Decision 2: Agent Communication

**Rejected**: WebSocket, IPC, message queues

**Why rejected**: Complex, fragile, hard to debug. Doesn't survive crashes.

**Approved**: File-based signals (JSON) in `.forge/refactors/{id}/signals/`:
- Human-inspectable and modifiable
- Survives crashes/restarts
- Works across Pi/Mac boundary
- Aligns with existing Forge patterns

### Decision 3: Memory Model

**Rejected**: Accumulated conversation context with summarization

**Why rejected**: Context compaction kills nuance. Summaries lose detail.

**Approved**: "Docs ARE the memory" - Agents start fresh, read from planning docs:
1. Read PHILOSOPHY.md (principles)
2. Read DECISIONS.md (architecture)
3. Read EXECUTION.md (current phase, exit criteria)
4. Do work
5. Write session log + handoff
6. Signal completion

### Decision 4: Audit Agent Lifecycle

**Rejected**: Per-phase audit agents (one per phase)

**Why rejected**: Too much context switching, loses coherence across related phases.

**Also rejected**: Single global audit agent for whole refactor

**Why rejected**: Context compaction over long refactor.

**Approved**: Hybrid - one audit agent per phase group:
- Related parallel phases share one audit (coherent review)
- New audit agent for each major milestone (fresh context)
- Best of both worlds

### Decision 5: Parallelization Control

**Rejected**: Automatic parallelization based on dependency graph

**Why rejected**: User bandwidth varies. Sometimes you want sequential even if parallel is possible.

**Approved**: User chooses at runtime:
- Orchestrator: "Phases 2 and 3 are ready. Run both in parallel, or one at a time?"
- System supports either mode
- Your attention is the bottleneck, not the dependency graph

### Decision 6: Approval Model

**Rejected**: Fixed approval gates at predetermined checkpoints

**Why rejected**: Real approvals depend on what audit finds, not arbitrary milestones.

**Approved**: Audit-based dynamic approval:
- Phase completes → Audit validates against philosophy
- If issues → Iterate with phase agent
- If passes → Signal orchestrator to advance
- You can intervene at any point via orchestrator chat

### Decision 7: Detection Trigger

**Rejected**: Hardcoded complexity thresholds (file count, line count, etc.)

**Why rejected**: Model judgment is better and improves over time.

**Approved**: Claude decides mid-conversation:
- During brainstorm, Claude realizes scope is too big
- Outputs recommendation: "This looks like a major architectural change..."
- AGI-pilled: trust the model, unhobble it

### Decision 8: iOS Handling

**Rejected**: Full Major Refactor Mode on iOS

**Why rejected**: Codebase analysis requires Mac-side file access.

**Approved**: Soft defer to Mac:
- iOS shows: "Major refactors need codebase analysis. Continue here for planning, or switch to Mac for full orchestration."
- Can still brainstorm and capture on iOS
- Execution happens on Mac

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FORGE APP (macOS)                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Brainstorm  │───▶│  Detection  │───▶│ Codebase Analysis   │ │
│  │    Chat     │    │   (Claude)  │    │ (PRE_REFACTOR.md)   │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│                                        ┌───────────▼──────────┐ │
│                                        │  Generate Planning   │ │
│                                        │       Docs           │ │
│                                        └───────────┬──────────┘ │
│                                                    │            │
└────────────────────────────────────────────────────┼────────────┘
                                                     │
┌────────────────────────────────────────────────────▼────────────┐
│                    .forge/refactors/{id}/                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │PHILOSOPHY.md │  │ DECISIONS.md │  │    EXECUTION.md      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │PRE_REFACTOR  │  │  ISSUES.md   │  │  signals/*.signal    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  ORCHESTRATOR │       │  PHASE AGENT  │       │  AUDIT AGENT  │
│    (Warp)     │◀──────│   (Worktree)  │──────▶│  (per group)  │
│  Supervisor   │       │  Does work    │       │  Validates    │
└───────────────┘       └───────────────┘       └───────────────┘
```

---

## What We're Building

| Component | Purpose | Phase |
|-----------|---------|-------|
| `forge/refactor/` module | Python backend for state, signals, CLI | 1 |
| Complexity detection | BrainstormAgent detects major refactors | 2 |
| Codebase analyzer | Generates PRE_REFACTOR.md | 2 |
| Orchestrator agent | Interactive supervisor in Warp | 3 |
| Phase agent | Worktree-based implementation | 4 |
| Audit agent | Philosophy validation | 4 |
| UI dashboard | Phase visualization in Forge app | 5 |
| Full integration | Pause/resume, Ship All, error handling | 6 |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-03 | File-based signals | Simpler than IPC, survives crashes, debuggable |
| 2026-01-03 | Docs as memory | Avoids context compaction |
| 2026-01-03 | Interactive orchestrator | Need to chat and modify plans |
| 2026-01-03 | Hybrid audit lifecycle | Balance coherence with compaction avoidance |
| 2026-01-03 | Runtime parallelization choice | User bandwidth is the bottleneck |
| 2026-01-03 | Claude decides detection | AGI-pilled, model judgment improves |
| 2026-01-03 | Three-layer audit | Builder self-check → Formal auditor → User vibes |
| 2026-01-03 | No hardcoded iteration limits | Model judges escalation, not MAX_ITERATIONS constant |
| 2026-01-03 | PRE_REFACTOR.md as planning byproduct | Planning Agent generates it, not separate analyze step |
| 2026-01-03 | Testing = signals, not source of truth | Three-layer audit + spec-first tests; user vibes ungameable |

---

## Resolved Questions

Questions that were open, now decided:

### Decision: PRE_REFACTOR.md Generation

**Rejected**: Separate `forge refactor analyze` step before planning

**Why rejected**: Clutters workflow, duplicates exploration, may miss nuance

**Approved**: Planning Agent generates PRE_REFACTOR.md as byproduct at end of planning

**Rationale**:
- Captures what Planning Agent actually understood (not a generic scan)
- No separate workflow step
- Becomes immutable "before" snapshot for audit comparison
- `forge refactor analyze` becomes optional fallback if Planning Agent didn't generate one

**Decided**: 2026-01-03 (via Prometheus consultation)

---

### Decision: Testing Strategy

**Rejected**: Automated tests as primary quality signal

**Why rejected**: Reward hacking - LLMs can optimize for metrics (green checkmarks) rather than actual correctness

**Approved**: Three-layer audit + spec-first tests for regression

**Rationale**:
- User vibes is the ungameable oracle (human intuition, not formal spec)
- Tests are one signal among many, not source of truth
- Spec-first tests (written BEFORE implementation) define target, can't be gamed
- Regression tests catch breaks over time (safety net)
- See PHILOSOPHY.md "Testing in AI-Assisted Development" for full framing

**Decided**: 2026-01-03 (via Prometheus consultation)


---

## What You're Validating

Review the following session work:

## Session 4.4

## Output from Session 4.4


# Session 4.4 Output

> **Completed**: 2026-01-03 23:17

## Summary

Session 4.4 completed

## Accomplishments

- See commit for details

## Issues Encountered

- None

## Handoff Notes

Ready for next session.


## Session 4.4 Instructions


# Execution Session: Planning Agent Robustness

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.4
> **Generated**: 2026-01-03 23:12

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md first.
Understand WHY this session exists (see EXECUTION_PLAN.md 4.4).

Add robustness to the Planning Agent so it can survive long sessions:

1. **PLANNING_HANDOFF.md pattern**:
   - Create template in planning_agent.py similar to orchestrator's handoff
   - Include: Generation number, conversation context, open questions, current doc state
   - Planning Agent should write this before handing off

2. **Generation tracking**:
   - Planner #1 → #2 → #3 (like orchestrator)
   - New planner reads handoff and announces continuity
   - "I'm Planner #3 for [refactor], continuing from #2"

3. **Handoff protocol in template**:
   - Add section: "## Handoff Protocol"
   - When to hand off: "When context is getting tight..."
   - What to preserve: conversation context, decisions in progress, user preferences discovered
   - Explicit "HANDS OFF" warning before launching new planner

4. **Resume capability**:
   - `forge refactor plan --resume <refactor-id>` command
   - Reads PLANNING_HANDOFF.md and launches planner with context
   - Generates new session in same refactor directory

5. **"Where were we" handler**:
   - When user returns: "Let me check PLANNING_HANDOFF.md..."
   - Summarize: "Last time we were discussing [X], deciding between [Y] and [Z]"

6. **Context-aware cues**:
   - Add guidance: "If you've been going for a while and context feels tight..."
   - Proactive: "We've covered a lot. Want me to do a handoff checkpoint?"

OUT OF SCOPE:
- Changing when/how PRE_REFACTOR.md is generated (separate concern)
- UI changes
- Codebase analyzer modifications

After implementing, test mentally: Can a complex refactor survive 3+ planner generations
without losing context or user having to repeat themselves?

---

## Scope

**IN scope**: Planning Agent handoff, iteration, resume

**OUT of scope**: Codebase analyzer changes, UI

---

## When to Ask the User

- The handoff template structure seems right before implementing
- Any specific conversation elements they want preserved (beyond what you infer)

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] PLANNING_HANDOFF.md template exists in planning_agent.py
- [ ] Generation tracking works (Planner #1 → #2 → #3)
- [ ] `forge refactor plan --resume <id>` command works
- [ ] Handoff section in Planning Agent template with clear instructions
- [ ] "Where were we" handler in template
- [ ] Proactive "want to checkpoint?" guidance in template
- [ ] All user-facing cues say which terminal to return to

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/planning_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.4 - Planning Agent robustness

- Add PLANNING_HANDOFF.md pattern for context preservation
- Add generation tracking (Planner #1 → #2 → #3)
- Add 'forge refactor plan --resume' command
- Add handoff protocol to template
- Planning can now survive 200k+ token sessions"
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
   forge refactor done 4.4
   ```

2. Tell the user:
   > "Session 4.4 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session 4.4 complete.
>
> **Go back to your orchestrator terminal** (a different window) and tell them I'm done. They'll run the audit."

**After fixing issues from audit:**
> "Fixes applied and committed.
>
> **Go back to your orchestrator terminal** and tell them to re-run the audit."

**If you're blocked or need a decision:**
> "I need guidance on [X].
>
> **Go back to your orchestrator terminal** and ask them - or make the call yourself and tell me."

Always end your work with a clear next-step that tells the user **which terminal window to go to**.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Phase 5:
- All agents now robust for long sessions
- Orchestrator has handoff ✓
- Planning Agent has handoff ✓
- Ready for UI work


---

## Code Changes Made

These are the actual commits from the sessions:

### Session 4.4 commits (4a192be..992542f):

**Commits made (1 total):**

- 992542f feat(refactor): Session 4.4 - Planning Agent robustness



#### Commit 992542f

commit 992542f8868357863711c8bb18968e9413229e66
Author: W1ndR1dr <W1ndR1dr@users.noreply.github.com>
Date:   Sat Jan 3 23:16:52 2026 -0800

    feat(refactor): Session 4.4 - Planning Agent robustness
    
    - Add PLANNING_HANDOFF.md pattern for context preservation
    - Add generation tracking (Planner #1 → #2 → #3)
    - Add 'forge refactor plan --resume' command
    - Add handoff protocol to template
    - Planning can now survive 200k+ token sessions
    
    🤖 Generated with [Claude Code](https://claude.com/claude-code)
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
---
 forge/cli.py                     |  44 ++++-
 forge/refactor/planning_agent.py | 365 +++++++++++++++++++++++++++++++++++++++
 2 files changed, 403 insertions(+), 6 deletions(-)

diff --git a/forge/cli.py b/forge/cli.py
index 628870d..73c59d4 100644
--- a/forge/cli.py
+++ b/forge/cli.py
@@ -1739,12 +1739,13 @@ app.add_typer(refactor_app, name="refactor")
 
 @refactor_app.command("plan")
 def refactor_plan(
-    title: str = typer.Argument(..., help="Title for the refactor"),
-    goal: str = typer.Option(..., "--goal", "-g", help="What you want to accomplish"),
+    title: Optional[str] = typer.Argument(None, help="Title for the refactor (required for new, ignored for --resume)"),
+    goal: Optional[str] = typer.Option(None, "--goal", "-g", help="What you want to accomplish"),
+    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume planning for existing refactor ID"),
     terminal: str = typer.Option("auto", "--terminal", "-t", help="Terminal: warp, iterm, terminal, auto"),
 ):
     """
-    🧠 Start a Planning Agent session for a major refactor.
+    🧠 Start or resume a Planning Agent session for a major refactor.
 
     The Planning Agent is an interactive Claude Code session that helps you:
     - Explore the codebase before proposing changes
@@ -1752,9 +1753,12 @@ def refactor_plan(
     - Debate alternatives and document decisions
     - Create complete planning docs (PHILOSOPHY, DECISIONS, EXECUTION)
 
-    Example:
+    Start new planning:
         forge refactor plan "API Restructure" --goal "Split monolith into microservices"
 
+    Resume existing planning:
+        forge refactor plan --resume api-restructure
+
     Naming tip: Avoid "Phase N" in titles - the refactor will have internal phases
     (sessions 1.x, 2.x, etc.) which creates confusing redundancy. Use descriptive
     names like "Auth Overhaul" or "API Restructure" instead.
@@ -1765,12 +1769,40 @@ def refactor_plan(
 
     from .refactor import PlanningAgent
 
+    agent = PlanningAgent(project_root)
+
+    # Resume mode: continue from PLANNING_HANDOFF.md
+    if resume:
+        console.print(f"\n🧠 [bold]Resuming Planning Session[/bold]: {resume}\n")
+        console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
+
+        success, message = agent.resume(
+            refactor_id=resume,
+            terminal=terminal,
+        )
+
+        if success:
+            console.print(f"[green]✓[/green] {message}")
+        else:
+            console.print(f"[red]✗[/red] {message}")
+            raise typer.Exit(1)
+        return
+
+    # New planning: require title and goal
+    if not title:
+        console.print("[red]✗[/red] Title is required for new planning sessions.")
+        console.print("[dim]Usage: forge refactor plan \"Title\" --goal \"...\"[/dim]")
+        console.print("[dim]Or resume: forge refactor plan --resume <refactor-id>[/dim]")
+        raise typer.Exit(1)
+
+    if not goal:
+        console.print("[red]✗[/red] Goal is required for new planning sessions (--goal).")
+        raise typer.Exit(1)
+
     console.print(f"\n🧠 [bold]Major Refactor Mode[/bold]: {title}\n")
     console.print(f"[dim]Goal: {goal}[/dim]\n")
     console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
 
-    agent = PlanningAgent(project_root)
-
     success, message, refactor_id = agent.launch(
         title=title,
         goal=goal,
diff --git a/forge/refactor/planning_agent.py b/forge/refactor/planning_agent.py
index c54a9de..e044063 100644
--- a/forge/refactor/planning_agent.py
+++ b/forge/refactor/planning_agent.py
@@ -13,6 +13,7 @@ all future execution agents will read.
 """
 
 import json
+import re
 import shutil
 from dataclasses import dataclass, field
 from datetime import datetime
@@ -20,6 +21,8 @@ from pathlib import Path
 from typing import Optional
 import subprocess
 
+from rich.console import Console
+
 from ..terminal import open_terminal_in_directory, Terminal
 
 
@@ -227,6 +230,74 @@ The user is a **vibecoder** - they work extensively with AI but are NOT a develo
 
 ---
 
+## Handoff Protocol
+
+**When to handoff:** When context is getting tight (~70%+ via `/context`), or if you've been at this for a while and feel things getting fuzzy.
+
+**Signs you might need a handoff:**
+- You're repeating yourself or asking clarifying questions you already asked
+- User mentions they've been at this for a while
+- You're uncertain about earlier decisions
+- Your responses are getting shorter or less nuanced
+
+**Proactive checkpoint:** If you've covered significant ground (multiple major decisions, substantial doc drafts), offer:
+> "We've covered a lot. Want me to do a handoff checkpoint? I'll save our progress to PLANNING_HANDOFF.md so nothing is lost, and you can continue fresh or pick up later."
+
+**HANDS OFF - Before handoff, you MUST:**
+
+1. **Update PLANNING_HANDOFF.md** with:
+   - Conversation context (key discussion points, NOT transcript)
+   - Open questions (what we haven't decided yet)
+   - Decisions in progress (what we're currently debating)
+   - Document status (which docs are not started/in progress/complete)
+   - User preferences discovered (their philosophy, what matters to them)
+   - Why you're handing off (context tight, natural break, etc.)
+
+2. **Tell the user exactly what to do:**
+   > "I've updated PLANNING_HANDOFF.md with our progress.
+   >
+   > **To continue in a new session:**
+   > 1. Open a **new terminal tab** in this same Warp window
+   > 2. Run: `forge refactor plan --resume {refactor_id}`
+   >
+   > The next planner will read the handoff and continue where we left off.
+   > You can close this tab after the new one is running."
+
+---
+
+## "Where Were We?" Handler
+
+If the user says "where were we?", "continue", "resume", or similar:
+
+1. **Check PLANNING_HANDOFF.md** - Read it to understand prior context
+2. **Announce continuity**: "I'm Planner #N for [refactor], continuing from #N-1. Let me review where we left off..."
+3. **Summarize**: "Last time we were discussing [X], deciding between [Y] and [Z]. We had completed [docs] and still need to work on [docs]."
+4. **Ask**: "Should we continue from there, or do you want to recap anything first?"
+
+If PLANNING_HANDOFF.md doesn't exist but user says "where were we?", they may be returning to an interrupted session:
+- Check which docs exist and their state
+- Summarize what's been written
+- Ask what they'd like to focus on
+
+---
+
+## Context-Aware Cues
+
+**At session start:** Note your generation number. If you're Planner #2+, read PLANNING_HANDOFF.md first.
+
+**During planning:** Periodically assess context usage mentally. If you feel things getting fuzzy or you've been going for a while, mention it:
+> "We've made good progress. My context is getting fuller - want me to checkpoint to PLANNING_HANDOFF.md?"
+
+**After major milestones:** When completing a doc draft or major decision round:
+> "PHILOSOPHY.md is drafted. Good checkpoint opportunity if you want to take a break - I can save progress to PLANNING_HANDOFF.md."
+
+**Always tell user which terminal:**
+- When handing off: "Open a **new terminal tab** and run..."
+- When done: "Go back to your **original terminal** (where you ran forge refactor plan)..."
+- When asking user to run commands: Be explicit about which window
+
+---
+
 ## Writing the Docs
 
 When the user approves (says "write it", "looks good", "yes", etc.):
@@ -437,3 +508,297 @@ Every session in EXECUTION.md should have:
         """Get the directory for a refactor."""
         refactor_dir = self.refactors_dir / refactor_id
         return refactor_dir if refactor_dir.exists() else None
+
+    def get_current_generation(self, refactor_dir: Path) -> int:
+        """
+        Parse PLANNING_HANDOFF.md to find current generation number.
+
+        Looks for "Generation: Planner #N → #N+1" and returns N+1
+        (the number AFTER the arrow, which is the incoming planner's number).
+
+        Returns 1 if no handoff file exists (first planner).
+        """
+        handoff_path = refactor_dir / "PLANNING_HANDOFF.md"
+        if not handoff_path.exists():
+            return 1
+
+        content = handoff_path.read_text()
+
+        # Look for "Generation: Planner #N → #N+1"
+        # The number after the arrow is the current/incoming generation
+        match = re.search(r"Generation:\s*Planner\s*#(\d+)\s*→\s*#(\d+)", content)
+        if match:
+            # Return the number AFTER the arrow (the incoming generation)
+            return int(match.group(2))
+
+        # Fallback: no generation info found, assume first
+        return 1
+
+    def update_handoff(
+        self,
+        refactor_id: str,
+        conversation_context: str = "",
+        open_questions: list[str] | None = None,
+        decisions_in_progress: list[str] | None = None,
+        docs_state: dict | None = None,
+        user_preferences: list[str] | None = None,
+        why_handoff: str = "",
+    ) -> Path:
+        """
+        Write current planning state to PLANNING_HANDOFF.md.
+
+        This is how Planning Agent context survives handoffs.
+        The next planner reads this file to continue.
+
+        Args:
+            refactor_id: The refactor ID
+            conversation_context: Summary of key discussion points (not transcript)
+            open_questions: Unresolved questions or pending decisions
+            decisions_in_progress: Decisions being debated but not yet final
+            docs_state: Status of each planning doc (not started/in progress/complete)
+            user_preferences: User preferences discovered during conversation
+            why_handoff: Reason for handoff (context tight, user requested, etc.)
+        """
+        console = Console()
+
+        # Path traversal protection
+        if ".." in refactor_id or refactor_id.startswith("/"):
+            raise ValueError(f"Invalid refactor ID: {refactor_id}")
+
+        refactor_dir = self.refactors_dir / refactor_id
+
+        # Additional check: ensure resolved path is under refactors_dir
+        try:
+            refactor_dir.resolve().relative_to(self.refactors_dir.resolve())
+        except ValueError:
+            raise ValueError(f"Invalid refactor ID: {refactor_id}")
+
+        if not refactor_dir.exists():
+            raise ValueError(f"Refactor not found: {refactor_id}")
+
+        # Warn if critical fidelity fields are empty
+        if not why_handoff:
+            console.print(
+                "[yellow]Warning: No handoff reason provided. "
+                "Consider adding context for the next planner.[/yellow]"
+            )
+
+        # Auto-detect generation from existing handoff (or 1 if first)
+        generation = self.get_current_generation(refactor_dir)
+
+        # Get metadata
+        metadata = self.get_refactor(refactor_id)
+        title = metadata.title if metadata else refactor_id
+        goal = metadata.goal if metadata else "Unknown"
+
+        # Build docs state section
+        docs_state = docs_state or {}
+        default_docs = ["PHILOSOPHY.md", "VISION.md", "DECISIONS.md", "PRE_REFACTOR.md", "EXECUTION_PLAN.md"]
+        docs_lines = []
+        for doc in default_docs:
+            status = docs_state.get(doc, "not started")
+            status_emoji = {
+                "not started": "⬜",
+                "in progress": "🔄",
+                "complete": "✅",
+                "draft": "📝",
+            }.get(status, "❓")
+            docs_lines.append(f"- {status_emoji} {doc}: {status}")
+
+        # Build open questions section
+        if open_questions:
+            questions_str = "\n".join(f"- {q}" for q in open_questions)
+        else:
+            questions_str = "No open questions."
+
+        # Build decisions in progress section
+        if decisions_in_progress:
+            decisions_str = "\n".join(f"- {d}" for d in decisions_in_progress)
+        else:
+            decisions_str = "No decisions pending."
+
+        # Build user preferences section
+        if user_preferences:
+            prefs_str = "\n".join(f"- {p}" for p in user_preferences)
+        else:
+            prefs_str = "None discovered yet."
+
+        # Build generation transition string
+        next_generation = generation + 1
+        generation_str = f"Planner #{generation} → #{next_generation}"
+
+        handoff_content = f'''# Planning Handoff - {refactor_id}
+
+> **Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
+> **Refactor**: {title}
+> **Goal**: {goal}
+> **Generation**: {generation_str}
+
+---
+
+## IMPORTANT: Read This Before Starting
+
+You are **Planner #{next_generation}** for the "{title}" refactor.
+A previous planner has handed off to you. Read this file carefully before continuing.
+
+Introduce yourself: "I'm Planner #{next_generation} for {title}, continuing from #{generation}. Let me review where we left off..."
+
+---
+
+## Why This Handoff
+
+{why_handoff if why_handoff else "No specific reason recorded."}
+
+---
+
+## Conversation Context
+
+{conversation_context if conversation_context else "No conversation context recorded."}
+
+---
+
+## Open Questions / Pending Decisions
+
+{questions_str}
+
+---
+
+## Decisions In Progress
+
+These decisions were being discussed but not yet finalized:
+
+{decisions_str}
+
+---
+
+## User Preferences Discovered
+
+The previous planner learned these about the user:
+
+{prefs_str}
+
+---
+
+## Document Status
+
+{chr(10).join(docs_lines)}
+
+---
+
+## Planning Commands
+
+**Resume planning:**
+```bash
+forge refactor plan --resume {refactor_id}
+```
+
+**Launch orchestrator (after planning complete):**
+```bash
+forge refactor orchestrate {refactor_id}
+```
+
+---
+
+## Key Files
+
+- `CLAUDE.md` - Planning session instructions (you're reading context from there too)
+- `metadata.json` - Refactor metadata
+
+Planning docs (in this directory):
+- `PHILOSOPHY.md` - Principles (IMMUTABLE once written)
+- `VISION.md` - Target state (IMMUTABLE once written)
+- `DECISIONS.md` - What we decided + rejected alternatives
+- `PRE_REFACTOR.md` - Codebase analysis
+- `EXECUTION_PLAN.md` - Phased sessions

... (93 more lines)

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
   # Audit Issues - 4.4

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail major-refactor-mode-phase-1 4.4 --issues "Brief summary of issues"
   ```

3. Tell the user:
   > "Audit FAILED for session 4.4.
   >
   > **Go back to your orchestrator terminal** and paste this output. The orchestrator will guide you through getting fixes from the builder."

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass major-refactor-mode-phase-1 4.4
   ```

2. Tell the user:
   > "Audit PASSED for session 4.4. Work aligns with philosophy.
   >
   > **Go back to your orchestrator terminal** and tell them the audit passed. They'll guide you to the next step."

### If Escalation is Needed:

If you observe recurring issues across iterations, fundamental architectural problems, or scope confusion that revision won't fix:

1. Run this command to signal escalation:
   ```bash
   forge refactor escalate major-refactor-mode-phase-1 4.4 --reason "Brief explanation"
   ```

2. Tell the user:
   > "Recommend ESCALATING session 4.4. This needs a human decision - the issue is too fundamental for automated revision.
   >
   > **Go back to your orchestrator terminal** and paste this output. We'll figure out the right path forward together."

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
