# Audit Session

> **Refactor**: major-refactor-mode-phase-1
> **Sessions Under Review**: 4.1
> **Generated**: 2026-01-03 22:16

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

## Session 4.1

## Output from Session 4.1


# Session 4.1 Output

> **Completed**: 2026-01-03 22:14

## Summary

Added workflow handoff cues to session template

## Accomplishments

- See commit for details

## Issues Encountered

- None

## Handoff Notes

Added workflow handoff cues to session template


## Session 4.1 Instructions


# Execution Session: Phase Agent

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.1
> **Generated**: 2026-01-03 21:46

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md.
Look at existing patterns in forge/worktree.py and forge/agents/executor.py.

Implement Phase Agent:

1. Create forge/refactor/phase_agent.py with PhaseAgent class:
   - __init__(refactor_id, phase_id)
   - prepare() - Create worktree for this phase
   - generate_prompt() - Build Claude prompt from phase spec
   - run() - Launch Claude Code session in worktree
   - complete() - Write output.md and signal phase_complete

2. Phase workflow:
   a. Read .forge/refactors/{id}/phases/{phase-id}/spec.md
   b. Create worktree at .forge-worktrees/refactor-{id}-phase-{phase-id}/
   c. Generate CLAUDE.md for the phase session
   d. Launch Warp with Claude Code in that worktree
   e. When Claude is done (user confirms), write output.md
   f. Write signal file: signals/phase-{id}.signal

3. Add CLI: forge refactor start-phase {refactor-id} {phase-id}
   - Creates worktree
   - Opens Warp with Claude session
   - Claude reads the phase spec and works

4. Use existing WorktreeManager from forge/worktree.py

Test: Create a dummy phase spec, run start-phase, verify worktree created.

---

## Scope

**IN scope**: Phase agent that runs in worktree, signals completion

**OUT of scope**: Audit agent (4.2)

---

## When to Ask the User

- The worktree naming convention is right
- You need help understanding existing worktree patterns
- The phase completion flow is unclear

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge refactor start-phase {id} {phase}` creates worktree
- [ ] Warp opens with Claude session for the phase
- [ ] Phase spec is read and included in prompt
- [ ] After work, output.md can be written
- [ ] Signal file is created on completion

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/phase_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.1 - Phase agent

- Add PhaseAgent for worktree-based phase execution
- Integrates with WorktreeManager
- CLI: forge refactor start-phase {id} {phase}
- Signals completion to orchestrator"
```

---

## Signaling Ready for Review

When you've completed ALL exit criteria and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done 4.1
   ```

2. Tell the user:
   > "Session 4.1 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for integration:
- How worktrees are named
- How signals are written
- How orchestrator should read these signals


## Session 4.1 Notes


Added workflow handoff cues to session template

---

## Code Changes Made

These are the actual commits from the sessions:

### Commit 0e2ce63 (Session 4.1)

commit 0e2ce63e4ee20bc284ef24666b392757f25babdf
Author: W1ndR1dr <W1ndR1dr@users.noreply.github.com>
Date:   Sat Jan 3 22:14:35 2026 -0800

    feat(refactor): Add workflow handoff cues to session template
    
    Builders now get clear instructions for communicating back to the user:
    - After completing work → direct user to orchestrator for audit
    - After fixing audit issues → direct user to re-audit
    - If blocked → ask user to check with orchestrator
    
    The user is the message bus between agents - each agent should signal
    "I'm done, here's what happens next" so the user knows where to go.
    
    🤖 Generated with [Claude Code](https://claude.com/claude-code)
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
---
 forge/refactor/session.py | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)

diff --git a/forge/refactor/session.py b/forge/refactor/session.py
index 7b299ee..af64738 100644
--- a/forge/refactor/session.py
+++ b/forge/refactor/session.py
@@ -315,6 +315,23 @@ When you've completed ALL exit criteria, self-audited, and committed:
 
 ---
 
+## Communicating Back to User
+
+You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.
+
+**After completing work (or a revision cycle):**
+> "Session {self.session_id} complete. Return to the orchestrator to run audit and close out."
+
+**After fixing issues from audit:**
+> "Fixes applied and committed. Return to orchestrator for re-audit."
+
+**If you're blocked or need a decision:**
+> "I need guidance on [X]. Please check with the orchestrator or decide directly."
+
+Always end your work with a clear next-step for the user.
+
+---
+
 ## Key Principles (from PHILOSOPHY.md)
 
 - **Docs ARE the memory** - Read from files, don't accumulate context


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
   # Audit Issues - 4.1

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail major-refactor-mode-phase-1 4.1 --issues "Brief summary of issues"
   ```

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass major-refactor-mode-phase-1 4.1
   ```

2. Tell the user:
   > "Audit PASSED for sessions 4.1. Work aligns with philosophy."

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
