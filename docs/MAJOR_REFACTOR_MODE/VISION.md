# Major Refactor Mode - Vision

> **Status**: STABLE ANCHOR - Target state (change requires explicit pivot)
> **Created**: 2026-01-03

---

## What This Feature Does

When you describe a feature that's too big for one Claude Code session, Forge:

1. **Detects** the scope mid-conversation (Claude decides, not a heuristic)
2. **Analyzes** your codebase to understand what exists
3. **Generates** planning docs (Philosophy, Decisions, Execution Plan)
4. **Orchestrates** multiple Claude Code sessions across phases
5. **Audits** each phase group against the philosophy to prevent drift
6. **Ships** everything cleanly when all phases pass

---

## User Experience

### Detection (In Brainstorm Chat)

You're refining an idea, and Claude says:

> "This looks like a major architectural change. I'd recommend breaking it into 4-5 phases that can be developed safely.
>
> Want me to analyze your codebase and create a refactor plan?"
>
> **[Switch to Major Refactor Mode]**

On iOS, you see a soft recommendation:
> "Major refactors need codebase analysis. Continue here for planning, or switch to Mac for full orchestration."

### Codebase Analysis

Full-screen modal with:
- Animated progress ring
- Step-by-step: "Scanning files... Mapping dependencies... Generating phases..."
- Live preview of the analysis being generated

### Phase Visualization

A "railroad track" diagram showing:
```
   =====[1]=====     =====[2]=====
         \               /           PARALLEL
          \             /
           \           /
            =====[3]=====            SEQUENTIAL
                 |
            =====[4]=====
                 |
              [SHIP]
```

Below: Phase cards with status, active worktrees, blockers.

### Orchestrator Interaction

A Warp terminal window where your "team lead" agent sits:
- Waits for signals from phase/audit agents
- Asks you: "Phases 2 and 3 are ready. Run both in parallel, or one at a time?"
- You can chat with it anytime to modify the plan

### Audit Loop

When a phase completes:
1. Audit agent reads the phase output
2. Validates against PHILOSOPHY.md
3. If issues: signals phase agent to iterate
4. If passes: signals orchestrator to advance

### Pause & Resume

At any point you can pause:
- All worktrees preserved
- State saved to files
- Resume continues exactly where you left off
- "Modify Plan" reopens brainstorm with context

---

## Agent Architecture

```
                    ┌─────────────────────────────────────┐
                    │       ORCHESTRATOR (Supervisor)     │
                    │  Interactive Warp window - your     │
                    │  team lead for the refactor.        │
                    └─────────────────┬───────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
    ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
    │   PHASE     │            │   PHASE     │            │   AUDIT     │
    │   AGENT     │            │   AGENT     │            │   AGENT     │
    │ (worktree)  │            │ (worktree)  │            │ (per group) │
    └─────────────┘            └─────────────┘            └─────────────┘
         │                          │                          │
         └──────────────────────────┴──────────────────────────┘
                              Signal Files (JSON)
```

**Orchestrator**: Interactive supervisor in Warp, waits for signals, chats with you
**Phase Agents**: Execute in worktrees, do the actual implementation work
**Audit Agents**: One per phase group, validate against philosophy, iterate if needed

---

## Document Structure (Generated)

```
.forge/refactors/{refactor-id}/
├── PHILOSOPHY.md       # Guiding principles, anti-patterns
├── VISION.md           # Target state, feature specs
├── DECISIONS.md        # Architectural choices + rationale
├── PRE_REFACTOR.md     # Codebase snapshot before changes
├── EXECUTION.md        # Session map, progress, handoffs
├── ISSUES.md           # Blockers, questions, deferred work
├── metadata.json       # Machine state
├── signals/            # Inter-agent communication
└── phases/             # Per-phase specs and outputs
```

---

## Success State

This feature is complete when:

1. Describe a big feature → Claude detects and suggests Major Refactor Mode
2. Codebase analysis generates useful planning docs
3. Orchestrator runs in Warp, coordinates phases, you can chat with it
4. Phase agents execute in worktrees, audit agents validate
5. You can pause/resume/modify plan at any point
6. Forge UI shows refactor progress, can launch terminals
7. Ship All merges everything cleanly to main
