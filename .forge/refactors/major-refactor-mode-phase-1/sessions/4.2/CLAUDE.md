# Execution Session: Audit Agent

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 4.2
> **Generated**: 2026-01-03 20:06

---

## FIRST: Read These Docs

Before doing ANYTHING, read these files to understand the context:

1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

---

## Your Mission

Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - this is what audit validates against!
The audit agent is the GUARDIAN of idea fidelity. It prevents drift.

Implement Audit Agent:

1. Create forge/refactor/audit_agent.py with AuditAgent class:
   - __init__(refactor_id, group_id)
   - load_philosophy() - Read PHILOSOPHY.md from refactor
   - load_phase_outputs() - Read output.md from each phase in group
   - validate() - Check outputs against philosophy
   - report() - Write audit report and signal

2. Validation checks:
   - Does the work align with stated principles?
   - Are any anti-patterns present?
   - Does the implementation match the vision?
   - Are there concerning deviations?

3. Output:
   - If issues found:
     - Write audit-groups/{group}/iterations/{n}/issues.md
     - Signal audit_complete with passed=false and issues list
   - If passes:
     - Signal audit_complete with passed=true

4. Add CLI: forge refactor audit {refactor-id} {group-id}
   - Opens Warp with audit Claude session
   - Claude reads philosophy + phase outputs
   - Claude writes validation report

5. The audit prompt should make Claude:
   - Read PHILOSOPHY.md carefully
   - Compare each phase output against principles
   - Be specific about what doesn't align
   - Suggest how to fix issues

Test: Create dummy phase output, run audit, see if it catches misalignment.

---

## Scope

**IN scope**: Audit agent that validates against philosophy

**OUT of scope**: Full iteration loop (comes with integration)

---

## When to Ask the User

- The validation criteria are too strict or too loose
- You're unsure what "alignment with philosophy" means concretely
- The audit feedback format needs adjustment

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] `forge refactor audit {id} {group}` launches audit session
- [ ] Audit reads PHILOSOPHY.md and phase outputs
- [ ] Can detect when work doesn't align with principles
- [ ] Writes issues.md with specific feedback
- [ ] Signals audit_complete with pass/fail status

---

## Git Instructions

When all exit criteria are met:

```bash
git add forge/refactor/audit_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.2 - Audit agent

- Add AuditAgent for philosophy validation
- Reads phase outputs, checks against principles
- CLI: forge refactor audit {id} {group}
- Guardian of idea fidelity"
```

---

## Signaling Ready for Review

When you've completed ALL exit criteria and committed:

1. **Run this command** to signal you're ready for review:
   ```bash
   forge refactor done 4.2
   ```

2. Tell the user:
   > "Session 4.2 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Key Principles (from PHILOSOPHY.md)

- **Docs ARE the memory** - Read from files, don't accumulate context
- **File-based communication** - Signals survive crashes
- **Vibecoders first** - User may not be a Git expert, guide them

---

## Handoff Notes

Note for integration:
- How audit reads philosophy
- What the issues format looks like
- How orchestrator should handle audit results
