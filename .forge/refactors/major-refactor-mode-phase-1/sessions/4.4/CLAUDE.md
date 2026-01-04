# Execution Session: Planning Agent Robustness

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.4
> **Generated**: 2026-01-03 23:12

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md first.
Understand WHY this session exists (see EXECUTION_PLAN.md 4.4).

Add robustness to the Planning Agent so it can survive long sessions:

1. **PLANNING_HANDOFF.md pattern**:
   - Create template in planning_agent.py similar to orchestrator's handoff
   - Include: Generation number, conversation context, open questions, current doc state
   - Planning Agent should write this before handing off

2. **Generation tracking**:
   - Planner #1 → #2 → #3 (like orchestrator)
   - New planner reads handoff and announces continuity
   - "I'm Planner #3 for [refactor], continuing from #2"

3. **Handoff protocol in template**:
   - Add section: "## Handoff Protocol"
   - When to hand off: "When context is getting tight..."
   - What to preserve: conversation context, decisions in progress, user preferences discovered
   - Explicit "HANDS OFF" warning before launching new planner

4. **Resume capability**:
   - `forge refactor plan --resume <refactor-id>` command
   - Reads PLANNING_HANDOFF.md and launches planner with context
   - Generates new session in same refactor directory

5. **"Where were we" handler**:
   - When user returns: "Let me check PLANNING_HANDOFF.md..."
   - Summarize: "Last time we were discussing [X], deciding between [Y] and [Z]"

6. **Context-aware cues**:
   - Add guidance: "If you've been going for a while and context feels tight..."
   - Proactive: "We've covered a lot. Want me to do a handoff checkpoint?"

OUT OF SCOPE:
- Changing when/how PRE_REFACTOR.md is generated (separate concern)
- UI changes
- Codebase analyzer modifications

After implementing, test mentally: Can a complex refactor survive 3+ planner generations
without losing context or user having to repeat themselves?

---

## Scope

**IN scope**: Planning Agent handoff, iteration, resume

**OUT of scope**: Codebase analyzer changes, UI

---

## When to Ask the User

- The handoff template structure seems right before implementing
- Any specific conversation elements they want preserved (beyond what you infer)

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] PLANNING_HANDOFF.md template exists in planning_agent.py
- [ ] Generation tracking works (Planner #1 → #2 → #3)
- [ ] `forge refactor plan --resume <id>` command works
- [ ] Handoff section in Planning Agent template with clear instructions
- [ ] "Where were we" handler in template
- [ ] Proactive "want to checkpoint?" guidance in template
- [ ] All user-facing cues say which terminal to return to

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/planning_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.4 - Planning Agent robustness

- Add PLANNING_HANDOFF.md pattern for context preservation
- Add generation tracking (Planner #1 → #2 → #3)
- Add 'forge refactor plan --resume' command
- Add handoff protocol to template
- Planning can now survive 200k+ token sessions"
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
   forge refactor done 4.4
   ```

2. Tell the user:
   > "Session 4.4 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session 4.4 complete.
>
> **Go back to your orchestrator terminal** (a different window) and tell them I'm done. They'll run the audit."

**After fixing issues from audit:**
> "Fixes applied and committed.
>
> **Go back to your orchestrator terminal** and tell them to re-run the audit."

**If you're blocked or need a decision:**
> "I need guidance on [X].
>
> **Go back to your orchestrator terminal** and ask them - or make the call yourself and tell me."

Always end your work with a clear next-step that tells the user **which terminal window to go to**.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Phase 5:
- All agents now robust for long sessions
- Orchestrator has handoff ✓
- Planning Agent has handoff ✓
- Ready for UI work
