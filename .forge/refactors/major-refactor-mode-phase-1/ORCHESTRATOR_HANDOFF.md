# Orchestrator Handoff - Major Refactor Mode Phase 1

> **Updated**: 2026-01-03
> **From**: Orchestrator #4
> **To**: Next orchestrator (or self after context compaction)

---

## Current State

**Phase 1**: ✅ COMPLETE (Sessions 1.1 + 1.2)
**Phase 2**: 🔄 IN PROGRESS
- Session 2.1: ✅ COMPLETE (Complexity Detection)
- Session 2.2: 🔄 RUNNING (Codebase Analyzer)

**Git**: All pushed to origin/main

---

## What's Been Built

### Session 0.1 ✅
- Planning Agent (`forge refactor plan`)

### Session 1.1 ✅
- `forge/refactor/state.py` - RefactorState, SessionState dataclasses
- `forge/refactor/signals.py` - SignalType enum, atomic signal read/write

### Session 1.2 ✅
- `forge/refactor/session.py` - ExecutionSession class, session spec parsing
- `forge refactor start/done` CLI commands

### Session 2.1 ✅
- Added major refactor detection to BRAINSTORM and REFINE prompts
- Marker: `MAJOR_REFACTOR_RECOMMENDED`
- Helper methods: `is_major_refactor_detected()`, `get_major_refactor()`
- Commit: c7eae0b

### Session 2.2 🔄
- Codebase Analyzer - IN PROGRESS

**Audit**: Phase 1 passed all checks. Prometheus reviewing Phase 2.

---

## Orchestrator Commands

**Launch session:**
```bash
forge refactor start major-refactor-mode-phase-1 2.2
```

**Check session status:**
```bash
forge refactor status major-refactor-mode-phase-1
```

**When session completes, launch next:**
```bash
forge refactor start major-refactor-mode-phase-1 <next-session>
```

---

## Tab Title Scheme

Tabs are named for quick identification:
- `MajorRefactor Planner` - Planning sessions
- `2.2 Builder` - Execution sessions (phase.session + role)
- `2 Auditor` - Phase audits (phase + role)
- `Forge Ship` - Shipping operations

---

## Orchestrator Handoff Protocol

**When to handoff:** User sees context getting tight (~70%+) via `/context`

**How to trigger (plain English):**
- "context is getting tight, let's handoff"
- "spin up a new orchestrator"
- "time for a fresh orchestrator"

**What happens:**
1. Orchestrator updates this ORCHESTRATOR_HANDOFF.md with current state
2. Runs: `forge refactor handoff major-refactor-mode-phase-1` (when built)
3. New tab opens with fresh Claude
4. Old tab preserved for posterity

**Until handoff command exists:** Manually open new Claude Code tab and point it here.

---

## Bootstrapping Ladder

```
Step 0: Human + Claude (manual)     ✅ DONE
Step 1: Planning Agent              ✅ DONE
Step 2: Phase 1 Foundation          ✅ DONE
Step 3: Phase 2 Detection           🔄 IN PROGRESS (2.1 done, 2.2 running)
Step 4: Phase 3 Orchestrator        ⬜ Flywheel kicks in here
Step 5: Self-sustaining             ⬜
```

---

## Key Files

- `docs/MAJOR_REFACTOR_MODE/EXECUTION_PLAN.md` - All session specs
- `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Principles (read first!)
- `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions
- `forge/refactor/` - All the infrastructure

---

## Important Context

- User is AGI-pilled: trust model judgment over hardcoded rules
- Docs as memory: write things down, context compaction loses fidelity
- User is vibecoder: don't ask deep technical questions, make the call
- Commit after each session, push to main
- Tab titles help identify parallel sessions visually

---

## Notes from This Session

- Added tab title support for Warp (ANSI escape sequences)
- Standardized titles: `X.Y Builder`, `[Title] Planner`, `X Auditor`
- Added `session-resume` and `terminology-consistency-audit` to backlog
- Prometheus feedback: detection should flow to `forge refactor plan`, not directly to execution
