# Major Refactor Mode - Documentation

> **Status**: Planning complete, ready for implementation
> **Created**: 2026-01-03

---

## What Is This?

Major Refactor Mode transforms Forge from a single-feature tool into a multi-phase refactor orchestrator. When a feature is too big for one Claude Code session, Forge can break it into phases, coordinate multiple agents, and maintain idea fidelity across the entire refactor.

---

## Reading Order

For **Claude Code sessions** implementing this:

1. **PHILOSOPHY.md** - Read first, every session. Contains principles and anti-patterns.
2. **DECISIONS.md** - Architectural choices already made. Don't re-litigate.
3. **EXECUTION_PLAN.md** - Find your session, read the prompt, do the work.
4. **VISION.md** - Reference for target UX and architecture.

For **humans** understanding the feature:

1. **README.md** - You're here
2. **VISION.md** - What we're building and why
3. **PHILOSOPHY.md** - The principles guiding decisions
4. **DECISIONS.md** - What we decided and why
5. **EXECUTION_PLAN.md** - How we're building it

---

## Quick Start (For Implementation)

1. Open a new Claude Code session
2. Find the next PENDING session in EXECUTION_PLAN.md
3. Check the **Start When** prerequisite is met
4. Copy the **PROMPT** section into Claude Code
5. Work until all **EXIT CRITERIA** are checked
6. Follow **GIT INSTRUCTIONS** to commit
7. Update the **Session Log** at the bottom
8. Next session can begin!

### Session Format (What You'll See)

Each session has:
```
┌─────────────────────────────────────────────────┐
│ Worktree: YES/NO                                │
│ Scope: What's IN and OUT                        │
│ Start When: Prerequisites                       │
│ Stop When: Completion conditions                │
├─────────────────────────────────────────────────┤
│ PROMPT: Copy this into Claude Code              │
├─────────────────────────────────────────────────┤
│ ASK USER IF: When to pause and ask              │
├─────────────────────────────────────────────────┤
│ EXIT CRITERIA: Checkboxes to verify done        │
├─────────────────────────────────────────────────┤
│ GIT INSTRUCTIONS: Exact commit commands         │
├─────────────────────────────────────────────────┤
│ HANDOFF: What to write for next session         │
└─────────────────────────────────────────────────┘
```

---

## Document Purposes

| Document | Purpose | Mutable? |
|----------|---------|----------|
| README.md | Overview and reading order | Yes |
| PHILOSOPHY.md | Guiding principles, anti-patterns | No |
| VISION.md | Target state, success criteria | No |
| DECISIONS.md | Architectural choices with rationale | Yes (append-only) |
| EXECUTION_PLAN.md | Session prompts, progress tracking | Yes |

---

## Key Principles (Summary)

1. **Docs ARE the memory** - Agents read from files, not accumulated context
2. **Unhobble the model** - Let Claude decide when to suggest Major Refactor Mode
3. **Your bandwidth is the bottleneck** - You choose parallelization at runtime
4. **Orchestrator is your team lead** - Interactive, not a daemon
5. **Audit prevents drift** - Philosophy validation at phase boundaries

---

## Implementation Phases

| Phase | Sessions | Focus |
|-------|----------|-------|
| **0. Planning Agent** | **0.1** | **MOST CRITICAL - Build first! Replaces brainstorm for major refactors** |
| 1. Foundation | 1.1, 1.2 | State management, CLI, doc templates |
| 2. Detection | 2.1, 2.2 | Complexity detection, codebase analysis |
| 3. Orchestrator | 3.1 | Interactive supervisor agent |
| 4. Agents | 4.1, 4.2 | Phase agents, audit agents |
| 5. UI | 5.1, 5.2 | Dashboard, phase cards, notifications |
| 6. Integration | 6.1 | Pause/resume, Ship All, polish |

**Start with Session 0.1** - The Planning Agent is what creates all the docs that other agents read.

---

## Bootstrap Strategy

- **Phase 1-2**: Build normally in regular Claude Code sessions
- **Phase 3-6**: Use docs with you as manual orchestrator (dogfooding)
- Once Phase 3-4 work, the orchestrator agent can take over

This way we test the architecture before trusting full automation.
