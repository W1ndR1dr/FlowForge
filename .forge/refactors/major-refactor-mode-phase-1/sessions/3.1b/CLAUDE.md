# Execution Session: Session 3.1b

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 3.1b
> **Generated**: 2026-01-03 19:20

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - especially "User as Fidelity Sensor".
Key insight: Handoff must preserve nuance, not just state.

Enhance the handoff workflow for fidelity:

1. In orchestrator.py update_handoff(), add these sections:
   - Orchestrator generation number (e.g., "Orchestrator #4 → #5")
   - "Open Questions / Pending Decisions" - things being discussed but not resolved
   - "Conversation Context" - key points from recent discussion (not transcript, summary)
   - "Why Handoff" - reason for handoff (context tight, user requested, etc.)

2. In ORCHESTRATOR_PROMPT, add instruction for orchestrator to:
   - Track its generation number (read from handoff, increment)
   - Announce continuity: "I'm Orchestrator #5, continuing from #4"
   - Before handoff, summarize any open discussions

3. Test by checking what update_handoff() generates - should include all new sections.

The goal: New orchestrator should know not just WHERE we are, but WHAT we were discussing.

---

## Scope

**IN scope**: Handoff doc enhancements for fidelity

**OUT of scope**: New features

---

## When to Ask the User

- No specific pause triggers for this session

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] update_handoff() includes orchestrator generation number
- [ ] update_handoff() includes "Open Questions / Pending Decisions" section
- [ ] update_handoff() includes "Conversation Context" summary
- [ ] update_handoff() includes "Why Handoff" reason
- [ ] ORCHESTRATOR_PROMPT tells orchestrator to track/announce generation
- [ ] New orchestrator announces continuity when starting

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/orchestrator.py forge/refactor/prompts.py
git commit -m "feat(refactor): Session 3.1b - Handoff fidelity enhancements

- Add orchestrator generation numbering
- Add open questions/pending decisions to handoff
- Add conversation context summary
- Add why handoff reason
- Orchestrator announces continuity on start"
```

---

## Signaling Completion

When you've completed ALL exit criteria and committed, tell the user:

> "Session 3.1b complete! All exit criteria verified and committed."

The orchestrator will handle the rest.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

This completes Phase 3 (Orchestrator). The orchestrator now:
- Coordinates sessions
- Tracks state and signals
- Preserves fidelity across handoffs

Ready for Phase 4 (Phase & Audit Agents).
