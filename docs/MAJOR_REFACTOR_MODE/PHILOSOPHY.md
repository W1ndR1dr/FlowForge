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
