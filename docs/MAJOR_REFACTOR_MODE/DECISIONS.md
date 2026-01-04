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
