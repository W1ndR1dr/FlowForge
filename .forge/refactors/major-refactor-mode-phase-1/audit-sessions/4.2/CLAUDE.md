# Audit Session

> **Refactor**: major-refactor-mode-phase-1
> **Sessions Under Review**: 4.2
> **Generated**: 2026-01-03 21:41

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


---

## What You're Validating

Review the following session work:

## Session 4.2


## Session 4.2 Instructions


# Execution Session: Audit Agent

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.2
> **Generated**: 2026-01-03 20:06

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - this is what audit validates against!
The audit agent is the GUARDIAN of idea fidelity. It prevents drift.

Implement Audit Agent:

1. Create forge/refactor/audit_agent.py with AuditAgent class:
   - __init__(refactor_id, group_id)
   - load_philosophy() - Read PHILOSOPHY.md from refactor
   - load_phase_outputs() - Read output.md from each phase in group
   - validate() - Check outputs against philosophy
   - report() - Write audit report and signal

2. Validation checks:
   - Does the work align with stated principles?
   - Are any anti-patterns present?
   - Does the implementation match the vision?
   - Are there concerning deviations?

3. Output:
   - If issues found:
     - Write audit-groups/{group}/iterations/{n}/issues.md
     - Signal audit_complete with passed=false and issues list
   - If passes:
     - Signal audit_complete with passed=true

4. Add CLI: forge refactor audit {refactor-id} {group-id}
   - Opens Warp with audit Claude session
   - Claude reads philosophy + phase outputs
   - Claude writes validation report

5. The audit prompt should make Claude:
   - Read PHILOSOPHY.md carefully
   - Compare each phase output against principles
   - Be specific about what doesn't align
   - Suggest how to fix issues

Test: Create dummy phase output, run audit, see if it catches misalignment.

---

## Scope

**IN scope**: Audit agent that validates against philosophy

**OUT of scope**: Full iteration loop (comes with integration)

---

## When to Ask the User

- The validation criteria are too strict or too loose
- You're unsure what "alignment with philosophy" means concretely
- The audit feedback format needs adjustment

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge refactor audit {id} {group}` launches audit session
- [ ] Audit reads PHILOSOPHY.md and phase outputs
- [ ] Can detect when work doesn't align with principles
- [ ] Writes issues.md with specific feedback
- [ ] Signals audit_complete with pass/fail status

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/audit_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.2 - Audit agent

- Add AuditAgent for philosophy validation
- Reads phase outputs, checks against principles
- CLI: forge refactor audit {id} {group}
- Guardian of idea fidelity"
```

---

## Signaling Ready for Review

When you've completed ALL exit criteria and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done 4.2
   ```

2. Tell the user:
   > "Session 4.2 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for integration:
- How audit reads philosophy
- What the issues format looks like
- How orchestrator should handle audit results


## Session 4.2 Notes


Revision complete: 8 audit fixes applied

---

## Code Changes Made

These are the actual commits from the sessions:

### Commit dabd9fa (Session 4.2)

commit dabd9fa961f73feb36bc18f0809a4cea796daced
Author: W1ndR1dr <W1ndR1dr@users.noreply.github.com>
Date:   Sat Jan 3 21:39:03 2026 -0800

    fix(audit): Session 4.2 revision - consolidated audit fixes
    
    Infrastructure:
    - Add iteration_count to SessionState (tracks audit iterations)
    - Add ESCALATION_NEEDED signal type
    - Increment iteration on audit fail
    - Include actual diffs in load_code_changes() (not just stats)
    - Load and include DECISIONS.md in audit context
    - Report which philosophy file was used
    
    Prompt improvements:
    - Make iteration visible to auditor with escalation guidance
    - Reframe checklist as "What to Check" (guide, not gate)
    - Let model judge severity and when to escalate
    
    CLI:
    - Add forge refactor escalate command
    
    Key principle: Build infrastructure (data, signals). Let the model judge.
    
    🤖 Generated with [Claude Code](https://claude.com/claude-code)
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
---
 .../20260103_201206_009669_session_done.json       |   9 +
 .../20260103_211516_167943_audit_passed.json       |   8 +
 .../major-refactor-mode-phase-1/state.json         |  21 +-
 forge/cli.py                                       |  50 +++++
 forge/refactor/__init__.py                         |   4 +
 forge/refactor/audit_agent.py                      | 239 +++++++++++++++++----
 forge/refactor/signals.py                          |  26 +++
 forge/refactor/state.py                            |  21 ++
 8 files changed, 329 insertions(+), 49 deletions(-)

diff --git a/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_201206_009669_session_done.json b/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_201206_009669_session_done.json
new file mode 100644
index 0000000..7d32346
--- /dev/null
+++ b/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_201206_009669_session_done.json
@@ -0,0 +1,9 @@
+{
+  "type": "session_done",
+  "session_id": "4.2",
+  "timestamp": "2026-01-03T20:12:06.009669",
+  "payload": {
+    "commit_hash": "ce05999",
+    "summary": "Audit agent implementation with CLI commands"
+  }
+}
\ No newline at end of file
diff --git a/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_211516_167943_audit_passed.json b/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_211516_167943_audit_passed.json
new file mode 100644
index 0000000..a41cc2d
--- /dev/null
+++ b/.forge/refactors/major-refactor-mode-phase-1/signals/20260103_211516_167943_audit_passed.json
@@ -0,0 +1,8 @@
+{
+  "type": "audit_passed",
+  "session_id": "4.2",
+  "timestamp": "2026-01-03T21:15:16.167943",
+  "payload": {
+    "notes": "Clean implementation. Follows all principles: file-based signals, model judgment, vibecoders-friendly CLI. No anti-patterns detected."
+  }
+}
\ No newline at end of file
diff --git a/.forge/refactors/major-refactor-mode-phase-1/state.json b/.forge/refactors/major-refactor-mode-phase-1/state.json
index de23bf2..3bc92e2 100644
--- a/.forge/refactors/major-refactor-mode-phase-1/state.json
+++ b/.forge/refactors/major-refactor-mode-phase-1/state.json
@@ -41,16 +41,16 @@
     },
     "4.2": {
       "session_id": "4.2",
-      "status": "in_progress",
+      "status": "completed",
       "started_at": "2026-01-03T20:06:56.881760",
-      "completed_at": null,
-      "commit_hash": null,
-      "audit_result": "pending",
-      "notes": ""
+      "completed_at": "2026-01-03T20:12:06.009211",
+      "commit_hash": "ce05999",
+      "audit_result": "passed",
+      "notes": "Audit agent implementation with CLI commands"
     }
   },
   "started_at": "2026-01-03T15:01:58.258740",
-  "updated_at": "2026-01-03T20:11:03.741613",
+  "updated_at": "2026-01-03T21:15:16.167719",
   "completed_at": null,
   "history": [
     {
@@ -120,6 +120,15 @@
         "old_status": "pending",
         "new_status": "in_progress"
       }
+    },
+    {
+      "timestamp": "2026-01-03T20:12:06.009245",
+      "action": "session_completed",
+      "details": {
+        "session_id": "4.2",
+        "old_status": "in_progress",
+        "commit_hash": "ce05999"
+      }
     }
   ]
 }
\ No newline at end of file
diff --git a/forge/cli.py b/forge/cli.py
index 4335e8b..afe2d10 100644
--- a/forge/cli.py
+++ b/forge/cli.py
@@ -1755,6 +1755,10 @@ def refactor_plan(
     Example:
         forge refactor plan "API Restructure" --goal "Split monolith into microservices"
 
+    Naming tip: Avoid "Phase N" in titles - the refactor will have internal phases
+    (sessions 1.x, 2.x, etc.) which creates confusing redundancy. Use descriptive
+    names like "Auth Overhaul" or "API Restructure" instead.
+
     The planning docs become the "memory" for all future execution sessions.
     """
     project_root, config, registry = get_context()
@@ -1763,6 +1767,7 @@ def refactor_plan(
 
     console.print(f"\n🧠 [bold]Major Refactor Mode[/bold]: {title}\n")
     console.print(f"[dim]Goal: {goal}[/dim]\n")
+    console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
 
     agent = PlanningAgent(project_root)
 
@@ -1928,6 +1933,7 @@ def refactor_start(
     from .refactor.session import ExecutionSession
 
     console.print(f"\n🚀 [bold]Starting Session {session_id}[/bold]\n")
+    console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
 
     session = ExecutionSession(
         refactor_id=refactor_id,
@@ -2118,6 +2124,7 @@ def refactor_orchestrate(
     from .refactor.orchestrator import OrchestratorSession
 
     console.print(f"\n🎯 [bold]Launching Orchestrator[/bold]: {refactor_id}\n")
+    console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
 
     orchestrator = OrchestratorSession(
         refactor_id=refactor_id,
@@ -2206,6 +2213,7 @@ def refactor_audit(
 
     console.print(f"\n🔍 [bold]Launching Audit[/bold]: {refactor_id}\n")
     console.print(f"[dim]Sessions: {', '.join(sessions)}[/dim]\n")
+    console.print("[yellow]⚠️  HANDS OFF KEYBOARD AND MOUSE until the new agent is running.[/yellow]\n")
 
     audit_agent = AuditAgent(
         refactor_id=refactor_id,
@@ -2307,5 +2315,47 @@ def refactor_audit_fail(
         raise typer.Exit(1)
 
 
+@refactor_app.command("escalate")
+def refactor_escalate(
+    refactor_id: str = typer.Argument(..., help="Refactor ID"),
+    session_ids: str = typer.Argument(..., help="Session ID(s) needing escalation (comma-separated)"),
+    reason: str = typer.Option(..., "--reason", "-r", help="Why escalation is needed"),
+):
+    """
+    🚨 Signal that human intervention is needed.
+
+    Called by the auditor when revision cycles aren't fixing the issue:
+    - Same issues recurring across iterations
+    - Fundamental architectural mismatch with philosophy
+    - Scope confusion that revision won't fix
+
+    Example:
+        forge refactor escalate major-refactor-mode-phase-1 1.1 --reason "Recurring anti-pattern despite 3 iterations"
+    """
+    project_root, config, registry = get_context()
+
+    from .refactor.audit_agent import record_escalation
+
+    # Parse session IDs
+    sessions = [s.strip() for s in session_ids.split(",")]
+
+    success, message = record_escalation(
+        refactor_id=refactor_id,
+        session_ids=sessions,
+        project_root=project_root,
+        reason=reason,
+    )
+
+    if success:
+        console.print(f"\n[red]🚨[/red] {message}")
+
+        # Show what happens next
+        console.print("\n[dim]The orchestrator will notify the user.[/dim]")
+        console.print("[dim]Human intervention required to proceed.[/dim]")
+    else:
+        console.print(f"[red]✗[/red] {message}")
+        raise typer.Exit(1)
+
+
 if __name__ == "__main__":
     app()
diff --git a/forge/refactor/__init__.py b/forge/refactor/__init__.py
index b564ad5..8e7380f 100644
--- a/forge/refactor/__init__.py
+++ b/forge/refactor/__init__.py
@@ -33,6 +33,7 @@ from .signals import (
     signal_audit_passed,
     signal_revision_needed,
     signal_question,
+    signal_escalation_needed,
 )
 from .session import (
     ExecutionSession,
@@ -55,6 +56,7 @@ from .audit_agent import (
     AuditIssue,
     record_audit_pass,
     record_audit_fail,
+    record_escalation,
 )
 
 __all__ = [
@@ -80,6 +82,7 @@ __all__ = [
     "signal_audit_passed",
     "signal_revision_needed",
     "signal_question",
+    "signal_escalation_needed",
     # Execution Sessions
     "ExecutionSession",
     "SessionSpec",
@@ -98,4 +101,5 @@ __all__ = [
     "AuditIssue",
     "record_audit_pass",
     "record_audit_fail",
+    "record_escalation",
 ]
diff --git a/forge/refactor/audit_agent.py b/forge/refactor/audit_agent.py
index 181f320..c64bfe6 100644
--- a/forge/refactor/audit_agent.py
+++ b/forge/refactor/audit_agent.py
@@ -22,6 +22,7 @@ from .state import RefactorState, AuditResult
 from .signals import (
     signal_audit_passed,
     signal_revision_needed,
+    signal_escalation_needed,
     get_signals_dir,
 )
 
@@ -95,13 +96,16 @@ class AuditAgent:
         """Check if the refactor exists."""
         return validate_refactor_exists(self.refactor_dir)
 
-    def load_philosophy(self) -> Optional[str]:
+    def load_philosophy(self) -> tuple[Optional[str], Optional[Path]]:
         """
-        Load PHILOSOPHY.md content.
+        Load PHILOSOPHY.md content and report which file was used.
 
         Checks multiple locations in priority order:
         1. Refactor-specific: .forge/refactors/{id}/PHILOSOPHY.md
         2. Project docs: docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md
+
+        Returns:
+            (content, source_path) tuple. Both None if not found.
         """
         paths = [
             self.refactor_dir / "PHILOSOPHY.md",
@@ -110,9 +114,31 @@ class AuditAgent:
 
         for path in paths:
             if path.exists():
-                return path.read_text()
+                return path.read_text(), path
+
+        return None, None
+
+    def load_decisions(self) -> tuple[Optional[str], Optional[Path]]:
+        """
+        Load DECISIONS.md content and report which file was used.
+
+        Checks multiple locations in priority order:
+        1. Refactor-specific: .forge/refactors/{id}/DECISIONS.md
+        2. Project docs: docs/MAJOR_REFACTOR_MODE/DECISIONS.md
+
+        Returns:
+            (content, source_path) tuple. Both None if not found.
+        """
+        paths = [
+            self.refactor_dir / "DECISIONS.md",
+            self.project_root / "docs" / "MAJOR_REFACTOR_MODE" / "DECISIONS.md",
+        ]
+
+        for path in paths:
+            if path.exists():
+                return path.read_text(), path
 
-        return None
+        return None, None
 
     def load_session_outputs(self) -> dict[str, str]:
         """
@@ -165,37 +191,74 @@ class AuditAgent:
 
         Uses git to find what was changed, so the audit can validate
         the actual implementation, not just documented outputs.
+
+        Includes both stats AND actual patches so auditor can see the code.
         """
         import subprocess
 
         # Get commits from these sessions
         changes = []
+        max_lines_per_commit = 500  # Intelligent truncation per commit
+        total_lines = 0
+        max_total_lines = 1500  # Cap total output
 
         state_path = self.refactor_dir / "state.json"
         if state_path.exists():
             state = RefactorState.load(state_path)
 
             for session_id in self.session_ids:
+                if total_lines >= max_total_lines:
+                    changes.append("\n... (truncated, too many changes to show)")
+                    break
+
                 session_state = state.get_session(session_id)
                 if session_state and session_state.commit_hash:
                     commit_hash = session_state.commit_hash
 
-                    # Get diff for this commit
+                    # Get diff with actual patch content
                     try:
                         result = subprocess.run(
-                            ["git", "show", "--stat", commit_hash],
+                            ["git", "show", "--stat", "--patch", commit_hash],
                             capture_output=True,
                             text=True,
                             cwd=self.project_root,
                         )
                         if result.returncode == 0:
                             changes.append(f"### Commit {commit_hash} (Session {session_id})\n")
-                            changes.append(result.stdout[:3000])  # Truncate long diffs
+                            # Truncate per-commit but show actual code
+                            lines = result.stdout.split('\n')
+                            truncated = lines[:max_lines_per_commit]
+                            changes.append('\n'.join(truncated))
+                            if len(lines) > max_lines_per_commit:
+                                changes.append(f"\n... ({len(lines) - max_lines_per_commit} more lines)")
+                            total_lines += min(len(lines), max_lines_per_commit)
                     except Exception:
                         pass
 
         return "\n".join(changes) if changes else "No commit information available."
 
+    def _get_iteration_context(self) -> tuple[int, str]:
+        """
+        Get iteration count and context string for audit.
+
+        Returns:
+            (max_iteration_count, context_string)
+        """
+        state_path = self.refactor_dir / "state.json"
+        max_iter = 0
+        iter_details = []
+
+        if state_path.exists():
+            state = RefactorState.load(state_path)
+            for session_id in self.session_ids:
+                session = state.get_session(session_id)
+                if session:
+                    iter_details.append(f"- Session {session_id}: iteration #{session.iteration_count}")
+                    max_iter = max(max_iter, session.iteration_count)
+
+        context = "\n".join(iter_details) if iter_details else "- No iteration data available"
+        return max_iter, context
+
     def generate_audit_claude_md(self) -> str:
         """
         Generate CLAUDE.md for the audit session.
@@ -206,16 +269,50 @@ class AuditAgent:
         - Validate alignment with principles
         - Report specific issues or pass
         """
-        philosophy = self.load_philosophy() or "(PHILOSOPHY.md not found)"
+        philosophy, philosophy_path = self.load_philosophy()
+        philosophy_content = philosophy or "(PHILOSOPHY.md not found)"
+        philosophy_source = str(philosophy_path) if philosophy_path else "not found"
+
+        decisions, decisions_path = self.load_decisions()
+        decisions_content = decisions or "(DECISIONS.md not found)"
+        decisions_source = str(decisions_path) if decisions_path else "not found"
+
         outputs = self.load_session_outputs()
         code_changes = self.load_code_changes()
 
+        max_iteration, iteration_details = self._get_iteration_context()
+
         sessions_str = ", ".join(self.session_ids)
         outputs_str = "\n\n---\n\n".join(
             f"## Session {sid}\n\n{content}"
             for sid, content in outputs.items()
         )
 
+        # Build escalation guidance based on iteration count
+        escalation_section = ""
+        if max_iteration > 0:
+            escalation_section = f"""
+---
+
+## Iteration Context
+
+**This is audit iteration #{max_iteration + 1}** for these sessions.
+
+{iteration_details}
+
+If you observe:
+- Same issues recurring across iterations
+- Fundamental architectural mismatch with philosophy
+- Scope confusion that revision won't fix
+
+...you may signal escalation instead of another revision:
+```bash
+forge refactor escalate {self.refactor_id} {sessions_str} --reason "Brief explanation"
+```
+
+Use your judgment. Escalation is not failure - it means human intervention is needed.
+"""
+
         return f'''# Audit Session
 
 > **Refactor**: {self.refactor_id}
@@ -231,14 +328,26 @@ aligns with the original vision and principles.
 
 **Key insight**: You're catching structural issues. The user will also do a "vibes check"
 to catch feel/intent issues. Together, you form a two-layer validation system.
-
+{escalation_section}
 ---
 
 ## FIRST: Read Philosophy Carefully
 
+> **Source**: `{philosophy_source}`
+
 This is the STABLE ANCHOR - the principles that must not be violated:
 
-{philosophy}
+{philosophy_content}
+
+---
+
+## Architecture Decisions
+
+> **Source**: `{decisions_source}`
+
+Check that approved decisions from DECISIONS.md are followed:
+
+{decisions_content}
 
 ---
 
@@ -258,26 +367,26 @@ These are the actual commits from the sessions:
 
 ---
 
-## Your Validation Checklist
+## What to Check
 
-For each session, verify:
+Review against these areas, using your judgment on what matters for THIS session:
 
-1. **Principle Alignment**
-   - Does the work follow the stated principles?
-   - Are any anti-patterns present?
-   - Does it match the vision?
+**From PHILOSOPHY.md:**
+- Docs as memory (updates files, not just conversation?)
+- File-based signals (no IPC/WebSocket complexity?)
+- Iteration-friendly (handles revision gracefully?)
+- Anti-patterns avoided?
 
-2. **Scope Compliance**
-   - Did the session stay within its defined scope?
-   - Was anything built that was explicitly "NOT building"?
+**From DECISIONS.md:**
+- Follows approved architecture decisions?
+- Avoids explicitly rejected approaches?
 
-3. **Quality Check**
-   - Is the implementation complete per exit criteria?
-   - Are there obvious gaps or shortcuts?
+**Quality:**
+- Complete per exit criteria?
+- Obvious gaps or shortcuts?
+- Does the code match the documented intent?

... (213 more lines)

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
   # Audit Issues - 4.2

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail major-refactor-mode-phase-1 4.2 --issues "Brief summary of issues"
   ```

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass major-refactor-mode-phase-1 4.2
   ```

2. Tell the user:
   > "Audit PASSED for sessions 4.2. Work aligns with philosophy."

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
