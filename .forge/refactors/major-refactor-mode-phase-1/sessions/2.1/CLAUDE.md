# Execution Session: Complexity Detection

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 2.1
> **Generated**: 2026-01-03 15:15

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - especially the AGI-pilled vision.
Key principle: Let Claude decide when something is too big. No hardcoded thresholds.

Add complexity detection to BrainstormAgent:

1. Modify forge/agents/prompts.py - Add to REFINE_SYSTEM_PROMPT:

   "If the user's request is a major architectural change that would take
   multiple implementation sessions (not just one focused task), you should
   recommend Major Refactor Mode. Output:

   MAJOR_REFACTOR_RECOMMENDED

   This looks like a major architectural change. I'd recommend breaking it
   into multiple phases for safer implementation.

   **Affected Areas:**
   - [area 1]
   - [area 2]

   **Estimated Phases:** [number]

   Would you like to switch to Major Refactor Mode?"

2. The detection should be based on Claude's judgment, not rules like
   "if more than 5 files" - that's against our philosophy.

3. Test by starting a brainstorm and describing something big like
   "I want to completely restructure the data layer"

Don't modify Swift code yet - that's Session 5.2.

---

## Scope

**IN scope**: Detection logic in Python, prompt updates

**OUT of scope**: Swift UI (that's 5.2)

---

## When to Ask the User

- The prompt wording feels right (show it first)
- You're unsure what constitutes "major" (but err on the side of trusting Claude)
- The marker format should be different

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] REFINE_SYSTEM_PROMPT updated with detection guidance
- [ ] Tested: describe a major refactor, Claude outputs MAJOR_REFACTOR_RECOMMENDED
- [ ] Tested: describe a small feature, Claude does NOT trigger detection
- [ ] Detection is judgment-based, not rule-based

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/agents/prompts.py forge/agents/brainstorm.py
git commit -m "feat(refactor): Session 2.1 - Major refactor detection

- Add complexity detection to BrainstormAgent
- Claude decides when to recommend Major Refactor Mode
- AGI-pilled: model judgment, not hardcoded rules"
```

---

## Signaling Completion

When you've completed ALL exit criteria and committed, tell the user:

> "Session 2.1 complete! All exit criteria verified and committed."

The orchestrator will handle the rest.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Session 2.2:
- What the marker looks like
- How to parse it (if needed)
- Any edge cases discovered
