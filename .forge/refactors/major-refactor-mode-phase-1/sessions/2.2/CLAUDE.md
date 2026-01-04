# Execution Session: Codebase Analyzer

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 2.2
> **Generated**: 2026-01-03 15:39

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md.

Reference: Look at /Users/Brian/Projects/Active/AirFit/docs/MEMORY_PERSONA_PRE-REFACTOR_STATE.md
for an example of what good codebase analysis looks like.

Implement codebase analyzer:

1. Create forge/refactor/analyzer.py with CodebaseAnalyzer class

2. Analyzer should:
   - Take a project path and refactor goal as input
   - Scan file structure (respect .gitignore)
   - Identify key modules/components relevant to the goal
   - Note patterns used (architecture style, frameworks)
   - Summarize what exists before we change it

3. Output PRE_REFACTOR.md with sections:
   - Executive Summary
   - Current Architecture (relevant to goal)
   - Key Files (with purposes)
   - Patterns in Use
   - Known Gaps/Issues

4. Add CLI command:
   forge refactor analyze {id} --goal "description"

   This updates the refactor's PRE_REFACTOR.md

5. The analysis should be FOCUSED on the refactor goal, not a dump of
   the entire codebase. Quality over quantity.

Test on the Forge codebase itself with a sample goal.

---

## Scope

**IN scope**: Analyzer that generates PRE_REFACTOR.md

**OUT of scope**: Using it in UI flow

---

## When to Ask the User

- The output format looks right (show a sample first)
- Analysis is too shallow or too deep
- Certain file types should be included/excluded

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge/refactor/analyzer.py` exists with CodebaseAnalyzer class
- [ ] `forge refactor analyze test --goal "..."` produces PRE_REFACTOR.md
- [ ] Output is focused on the goal, not a codebase dump
- [ ] Output format matches AirFit example structure

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/analyzer.py forge/cli.py
git commit -m "feat(refactor): Session 2.2 - Codebase analyzer

- Add CodebaseAnalyzer for PRE_REFACTOR.md generation
- Goal-focused analysis, not full codebase dump
- CLI: forge refactor analyze {id} --goal '...'"
```

---

## Signaling Completion

When you've completed ALL exit criteria and committed, tell the user:

> "Session 2.2 complete! All exit criteria verified and committed."

The orchestrator will handle the rest.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Phase 3:
- How to invoke the analyzer
- What the output looks like
- Any improvements needed for quality
