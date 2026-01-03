# Major Refactor Mode - Session Handoff

> **Created**: 2026-01-03
> **From**: Initial planning conversation with Brian
> **To**: Future Claude Code sessions implementing this feature

---

## What We Did

In a single extended conversation, we:

1. **Explored the current Forge codebase** - Understood BrainstormChatView, Feature model, existing agent patterns

2. **Studied AirFit's refactor documentation** - Analyzed MEMORY_PERSONA_*.md files for good multi-phase planning patterns

3. **Collaboratively designed Major Refactor Mode** through Q&A:
   - Detection: Claude decides mid-conversation (AGI-pilled, no hardcoded thresholds)
   - Memory model: Docs ARE the memory (no context compaction)
   - Orchestrator: Interactive supervisor, not polling daemon
   - Parallelization: User chooses at runtime (bandwidth is bottleneck)
   - Audit: Hybrid lifecycle (one per phase group)

4. **Created complete documentation**:
   - PHILOSOPHY.md - Guiding principles, anti-patterns
   - VISION.md - Target state, success criteria
   - DECISIONS.md - What we decided + rejected alternatives
   - EXECUTION_PLAN.md - 12 sessions with standardized format

5. **Identified missing piece**: The Planning Agent (Phase 0) that replicates THIS conversation for future refactors

---

## Key Insights (Preserve These)

### The AGI-Pilled Vision
- Trust model judgment for detection (not file counts)
- Design for capability improvement
- Unhobble, don't constrain

### Your Bandwidth is the Bottleneck
- Not the dependency graph
- System asks "parallel or sequential?" - you decide
- Never automate away human agency

### Docs as Memory Solves Context Compaction
- Agents start fresh, read from files
- No accumulated conversation to compress
- State survives agent restarts

### The Planning Agent is Critical
- Phase 0 must be built FIRST
- It replaces Refine for major refactors
- Replicates the collaborative planning we did here

---

## What's Ready

### Documentation Complete
```
docs/MAJOR_REFACTOR_MODE/
├── README.md           # Overview + Quick Start
├── PHILOSOPHY.md       # Principles (IMMUTABLE)
├── VISION.md           # Target state (IMMUTABLE)
├── DECISIONS.md        # Architecture decisions
├── EXECUTION_PLAN.md   # 12 sessions with prompts
└── HANDOFF.md          # This file
```

### Session Order
1. **Session 0.1**: Planning Agent (START HERE)
2. Session 1.1-1.2: Foundation (state, signals, CLI)
3. Session 2.1-2.2: Detection + codebase analysis
4. Session 3.1: Orchestrator
5. Session 4.1-4.2: Phase + Audit agents (parallelizable)
6. Session 5.1-5.2: UI Dashboard
7. Session 6.1: Integration + polish

### Standardized Session Format
Each session has:
- Worktree: YES/NO
- Scope: IN/OUT
- Start When / Stop When
- PROMPT (copy-paste ready)
- ASK USER IF (pause triggers)
- EXIT CRITERIA (checkboxes)
- GIT INSTRUCTIONS
- HANDOFF notes

---

## To Start Implementation

1. Open new Claude Code session
2. Run: `Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md`
3. Then: `Read docs/MAJOR_REFACTOR_MODE/EXECUTION_PLAN.md`
4. Find Session 0.1 and copy the PROMPT
5. Execute, verify EXIT CRITERIA, commit
6. Update Session Log with completion notes

---

## User Context

- Brian is a "vibecoder" - works with AI, not a Git expert
- Forge handles complexity so he can focus on features
- He's AGI-pilled and wants to unhobble models
- His attention/bandwidth is the limiting factor for parallelization
- He values nuance and idea fidelity (hates context compaction)

---

## Technical Context

- Forge: Python backend + SwiftUI macOS/iOS app
- Server runs on Raspberry Pi, connects to Mac via Tailscale
- Existing patterns: forge/registry.py, forge/worktree.py, forge/agents/
- Swift patterns: ForgeApp/Models/Feature.swift, ForgeApp/Design/

---

## Open Items (Future Enhancement)

1. Railroad track visualization (stretch goal - start with list view)
2. Orchestrator handoff mechanism (if context gets full)
3. iOS planning support (currently defers to Mac)
4. Automatic audit iteration limit handling

---

## The Most Important Thing

**The Planning Agent (Phase 0) creates the conditions for all other phases to succeed.**

Without good planning docs, execution drifts. The planning conversation we had here - the questions, the debates, the decisions - THAT's what needs to be replicated for every major refactor.

Build Phase 0 first. Everything else follows.
