# Major Refactor Mode - Bootstrapping Strategy

> **Purpose**: Document how we build the orchestrator using the tools we're building.
> **Pattern**: Classic compiler bootstrapping - each step builds tools for the next step.

---

## The Ladder

```
Step 0: Human + Claude session (manual orchestration)
   ↓ builds
Step 1: Planning Agent (launches planning sessions)
   ↓ plans
Step 2: Phase 1 - Foundation (RefactorState, Signals, Phase Runner)
   ↓ enables
Step 3: Phase Runner orchestrates execution sessions
   ↓ builds
Step 4: Orchestrator Agent (replaces manual Claude session)
   ↓ becomes
Step 5: Self-sustaining system
```

---

## Current State (During Bootstrap)

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                          ↕                                   │
│     ┌─────────────────────────────────────────────┐         │
│     │      Claude Session (Manual Orchestrator)   │         │
│     │                                             │         │
│     │  • Coordinates between sessions             │         │
│     │  • Commits code                             │         │
│     │  • Iterates on tooling                      │         │
│     │  • THIS IS SCAFFOLDING - will be replaced   │         │
│     └─────────────────────────────────────────────┘         │
│                          ↕                                   │
│     ┌─────────────────────────────────────────────┐         │
│     │         Planning Agent (Warp window)        │         │
│     │                                             │         │
│     │  • Explores codebase                        │         │
│     │  • Asks user questions                      │         │
│     │  • Writes planning docs                     │         │
│     │  • PERMANENT - this is the tool             │         │
│     └─────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## What Gets Built When

### Session 0.1 ✅ (Manual)
**Built**: Planning Agent
**By**: Claude session with user (manual orchestration)
**Result**: `forge refactor plan` command works

### Phase 1 Planning 🔄 (Now)
**Built**: Planning docs for Phase 1
**By**: Planning Agent (dogfooding itself)
**Result**: PHILOSOPHY.md, DECISIONS.md, EXECUTION.md for Phase 1

### Phase 1 Execution (Next)
**Built**: RefactorState, Signals, Phase Runner
**By**: Claude sessions (still manually orchestrated)
**Result**: Infrastructure for orchestrating future sessions

### Phase 2+ (After Phase 1)
**Built**: Orchestrator Agent, Merge Coordinator
**By**: Phase Runner (now automated!)
**Result**: No more manual orchestration needed

---

## The Meta-Game

We're building the plane while flying it:

1. **Planning Agent plans its own foundation** - The tool we just built is now being used to plan the infrastructure that will support it.

2. **Manual orchestration is scaffolding** - The Claude session coordinating everything right now will be replaced by the Orchestrator Agent we're building.

3. **Dogfooding immediately** - We don't build in isolation then test. We use each tool the moment it exists.

4. **Each step reduces manual work** - After Phase 1, the Phase Runner handles session launching. After Phase 2, the Orchestrator handles coordination.

---

## Why This Pattern?

### The Bootstrap Problem
We need an orchestrator to manage multi-session refactors, but building an orchestrator IS a multi-session refactor. Chicken and egg.

### The Solution
Start with a human + Claude as the "orchestrator", then progressively automate:

| Phase | Orchestration Method |
|-------|---------------------|
| 0.x   | Human + Claude session (manual) |
| 1.x   | Human + Phase Runner (semi-auto) |
| 2.x   | Human + Orchestrator Agent (mostly auto) |
| 3.x+  | Orchestrator Agent (fully auto, human approves) |

### The Goal
Eventually, starting a major refactor is:
```bash
forge refactor start "Big Feature" --goal "..."
```

And the Orchestrator Agent:
1. Launches Planning Agent
2. Reviews planning docs with user
3. Executes phases (parallel where possible)
4. Handles signals and coordination
5. Reports progress
6. Asks user when decisions needed

The human just provides vision and approval. All orchestration is automated.

---

## For Future Claude Sessions

If you're reading this and wondering "who's orchestrating this refactor?":

1. **Check the phase** - Early phases (0.x, 1.x) are manually orchestrated
2. **Check for Orchestrator Agent** - If Phase 2+ is complete, it should be running
3. **If no orchestrator, you might BE the orchestrator** - Coordinate with user, launch agents, commit code

The bootstrapping is complete when you never have to read this paragraph because the Orchestrator Agent handles it all.
