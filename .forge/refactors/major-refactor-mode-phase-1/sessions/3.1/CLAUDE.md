# Execution Session: Interactive Supervisor

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 3.1
> **Generated**: 2026-01-03 18:25

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - especially the orchestrator section.
Key: Orchestrator is your INTERACTIVE TEAM LEAD, not a daemon.

Implement the Orchestrator Agent:

1. Create forge/refactor/orchestrator.py with:
   - OrchestratorSession class
   - read_state() - Load refactor state from files
   - check_signals() - Look for new signal files
   - handle_signal(signal) - Decide what to do
   - advance_phase() - Move to next phase
   - update_handoff() - Write current state to ORCHESTRATOR_HANDOFF.md

2. Create forge/refactor/prompts.py with ORCHESTRATOR_PROMPT:
   - Explain the orchestrator role (you are the team lead)
   - Reference PHILOSOPHY.md and DECISIONS.md from the refactor
   - Instructions for:
     - Checking signals when user asks "check status"
     - Advancing phases when audit passes
     - Asking user about parallelization
     - Modifying plan when user requests (update DECISIONS.md with rationale)
   - Make it conversational and helpful

3. Add CLI: forge refactor orchestrate {id}
   - Generates a CLAUDE.md for the orchestrator session
   - Opens Warp with claude command pointing to refactor directory
   - Tab title: "Orchestrator" (brief, using ANSI escape sequence)
   - The session should start with "I'm your orchestrator for [refactor].
     Current status: [phase]. What would you like to do?"

4. Test flow:
   - Run forge refactor orchestrate test
   - Warp opens with orchestrator session
   - Type "check status" - it reads state and reports
   - Type "I want to modify the plan" - it engages conversationally

5. Handoff Protocol (CRITICAL - add to ORCHESTRATOR_PROMPT):
   - Orchestrator CANNOT see its own context usage - user monitors via /context
   - User will indicate when handoff is needed (plain English - infer intent, don't require specific phrases)
   - If unclear what user wants, ask for clarification
   - When handoff is triggered:
     a. Update ORCHESTRATOR_HANDOFF.md with current state
     b. Tell user to open new Claude tab in same Warp window
     c. New orchestrator reads ORCHESTRATOR_HANDOFF.md and continues
   - Old tab preserved for posterity/reference

6. Plan Ownership (add to ORCHESTRATOR_PROMPT):
   - Orchestrator CAN modify: EXECUTION_PLAN.md, DECISIONS.md
   - Orchestrator CANNOT modify: PHILOSOPHY.md, VISION.md (these are IMMUTABLE)
   - If philosophy/vision needs to change → re-invoke Planning Agent
   - Always document changes with rationale in DECISIONS.md
   - Builders do NOT modify plans - they signal issues, orchestrator decides

---

## Scope

**IN scope**: Orchestrator that runs in Warp, handles signals

**OUT of scope**: Phase/audit agents (Phase 4)

---

## When to Ask the User

- The orchestrator personality feels right
- The Warp launch mechanism works (may need osascript on Mac)
- You're unsure how to generate the session-specific CLAUDE.md

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge refactor orchestrate {id}` opens Warp with Claude session
- [ ] Tab title shows "Orchestrator" (brief)
- [ ] Orchestrator introduces itself and shows current status
- [ ] "check status" shows refactor state from files
- [ ] Can have a conversation about modifying the plan
- [ ] check_signals() can read signal files
- [ ] Handoff protocol in ORCHESTRATOR_PROMPT (infer intent, ask if unclear)
- [ ] Plan ownership rules in ORCHESTRATOR_PROMPT (what's mutable vs immutable)
- [ ] update_handoff() writes to ORCHESTRATOR_HANDOFF.md

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/orchestrator.py forge/refactor/prompts.py forge/cli.py
git commit -m "feat(refactor): Session 3.1 - Interactive orchestrator agent

- Add OrchestratorSession for managing refactor state
- Add ORCHESTRATOR_PROMPT with handoff protocol and plan ownership rules
- CLI: forge refactor orchestrate {id}
- Tab title: 'Orchestrator'
- Handoff via natural language (infer intent)
- Launches interactive supervisor in Warp"
```

---

## Signaling Completion

When you've completed ALL exit criteria and committed, tell the user:

> "Session 3.1 complete! All exit criteria verified and committed."

The orchestrator will handle the rest.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for Phase 4:
- How to launch orchestrator: `forge refactor orchestrate {id}`
- How signals are checked: check_signals() reads from signals/ directory
- How the conversation model works: Plain English, orchestrator responds helpfully
- Handoff protocol: User triggers, orchestrator updates ORCHESTRATOR_HANDOFF.md
- Plan ownership: Orchestrator modifies EXECUTION_PLAN.md and DECISIONS.md
- PHILOSOPHY.md and VISION.md are IMMUTABLE

This is the "team lead" - Phase 4 agents will signal back to it.
