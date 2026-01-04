# Execution Session: Workflow Polish

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.3
> **Generated**: 2026-01-03 22:23

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md for context.

This session adds workflow guidance to all agent templates so users always know what to do next. The user is the message bus between agents - every agent should end with a clear "here's what you do next" cue.

Update these files:

0. **State fix** (forge/refactor/state.py + session.py + audit_agent.py)
   - Add `start_commit` field to SessionState (captured when session starts)
   - In `start_session()`, record current HEAD as start_commit
   - In `load_code_changes()`, show ALL commits from start_commit to commit_hash:
     `git log --oneline start_commit..commit_hash` then `git show` each
   - This ensures audit sees ALL commits, not just the final one

1. **Planning Agent** (forge/refactor/planning_agent.py - generate_planning_claude_md)
   Add end-of-planning guidance:
   - "Planning complete! Docs are in {path}."
   - "To start execution: `forge refactor orchestrate {id}` or `forge refactor start {id} 1.1`"

2. **Builder/Session** (forge/refactor/session.py - generate_execution_claude_md)
   Add "Communicating Back to User" section:
   - After work complete: "Session [X.Y] ready for review. Return to orchestrator to run audit."
   - After fixes: "Fixes applied and committed. Return to orchestrator for re-audit."
   - If blocked: "I need guidance on [X]. Please check with orchestrator or decide directly."

3. **Audit Agent** (forge/refactor/audit_agent.py - generate_audit_claude_md)
   Add workflow cues after verdict:
   - After pass: "Audit PASSED. Return to orchestrator to close out and continue."
   - After fail: "Audit FAILED. Return to orchestrator to relay fixes to builder."
   - If escalating: "Recommend escalating. Return to orchestrator for human decision."

4. **Orchestrator** (forge/refactor/prompts.py - ORCHESTRATOR_PROMPT)
   Verify complete coverage exists for:
   - Before ANY agent launch: "HANDS OFF... say 'go'"
   - After launch: "Let me know when it signals done"
   - After audit passes: "You can close that terminal"
   - At handoff: Clear instructions for next orchestrator

Test by reading each generated CLAUDE.md and verifying the workflow is obvious to a user who forgot the process.

---

## Scope

**IN scope**: Cross-agent workflow cues in all templates

**OUT of scope**: New features

---

## When to Ask the User

- Any workflow transitions are missing
- The cue language is unclear

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] SessionState has `start_commit` field, captured on session start
- [ ] `load_code_changes()` shows ALL commits between start and end
- [ ] Planning agent template has clear end-of-planning cue
- [ ] Builder template has "Communicating Back to User" section
- [ ] Audit template has pass/fail/escalate cues
- [ ] Orchestrator prompt has complete transition coverage
- [ ] Each template ends with clear next-step for user

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/state.py forge/refactor/planning_agent.py forge/refactor/prompts.py forge/refactor/session.py forge/refactor/audit_agent.py
git commit -m "feat(refactor): Session 4.3 - Workflow polish & multi-commit audit fix

- Add start_commit tracking so audit sees ALL session commits
- Add user-facing workflow guidance to all agent templates
- Planning: clear 'next step' after completion
- Builder: 'return to orchestrator' cues
- Audit: pass/fail/escalate guidance
- User always knows what to do next"
```

---

## Before Signaling Done

Perform adversarial self-review of your own code:

- [ ] **Invalid inputs**: What happens with empty, null, malicious input?
- [ ] **Path traversal**: Can `../../../` break assumptions?
- [ ] **Error paths**: What if dependencies fail? Are errors handled or swallowed?
- [ ] **Edge cases**: What if file doesn't exist? What if it's empty?
- [ ] **Dead code**: Any unused variables or unreachable branches?

Fix any issues you find. THEN signal done.

---

## Signaling Ready for Review

When you've completed ALL exit criteria, self-audited, and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done 4.3
   ```

2. Tell the user:
   > "Session 4.3 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session 4.3 complete. Return to the orchestrator to run audit and close out."

**After fixing issues from audit:**
> "Fixes applied and committed. Return to orchestrator for re-audit."

**If you're blocked or need a decision:**
> "I need guidance on [X]. Please check with the orchestrator or decide directly."

Always end your work with a clear next-step for the user.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Phase 5:
- All agents now guide users through transitions
- Workflow is self-documenting
