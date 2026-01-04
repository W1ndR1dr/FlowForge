# Execution Session: Phase Agent

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.1
> **Generated**: 2026-01-03 21:46

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md.
Look at existing patterns in forge/worktree.py and forge/agents/executor.py.

Implement Phase Agent:

1. Create forge/refactor/phase_agent.py with PhaseAgent class:
   - __init__(refactor_id, phase_id)
   - prepare() - Create worktree for this phase
   - generate_prompt() - Build Claude prompt from phase spec
   - run() - Launch Claude Code session in worktree
   - complete() - Write output.md and signal phase_complete

2. Phase workflow:
   a. Read .forge/refactors/{id}/phases/{phase-id}/spec.md
   b. Create worktree at .forge-worktrees/refactor-{id}-phase-{phase-id}/
   c. Generate CLAUDE.md for the phase session
   d. Launch Warp with Claude Code in that worktree
   e. When Claude is done (user confirms), write output.md
   f. Write signal file: signals/phase-{id}.signal

3. Add CLI: forge refactor start-phase {refactor-id} {phase-id}
   - Creates worktree
   - Opens Warp with Claude session
   - Claude reads the phase spec and works

4. Use existing WorktreeManager from forge/worktree.py

Test: Create a dummy phase spec, run start-phase, verify worktree created.

---

## Scope

**IN scope**: Phase agent that runs in worktree, signals completion

**OUT of scope**: Audit agent (4.2)

---

## When to Ask the User

- The worktree naming convention is right
- You need help understanding existing worktree patterns
- The phase completion flow is unclear

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge refactor start-phase {id} {phase}` creates worktree
- [ ] Warp opens with Claude session for the phase
- [ ] Phase spec is read and included in prompt
- [ ] After work, output.md can be written
- [ ] Signal file is created on completion

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/phase_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.1 - Phase agent

- Add PhaseAgent for worktree-based phase execution
- Integrates with WorktreeManager
- CLI: forge refactor start-phase {id} {phase}
- Signals completion to orchestrator"
```

---

## Signaling Ready for Review

When you've completed ALL exit criteria and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done 4.1
   ```

2. Tell the user:
   > "Session 4.1 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for integration:
- How worktrees are named
- How signals are written
- How orchestrator should read these signals
