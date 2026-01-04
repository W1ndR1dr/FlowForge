# Audit Session

> **Refactor**: major-refactor-mode-phase-1
> **Sessions Under Review**: 4.3
> **Generated**: 2026-01-03 22:34

---

## Your Role: Guardian of Idea Fidelity

You are the **Audit Agent** - your job is to prevent drift and ensure the implementation
aligns with the original vision and principles.

**Key insight**: You're catching structural issues. The user will also do a "vibes check"
to catch feel/intent issues. Together, you form a two-layer validation system.

---

## FIRST: Read Philosophy Carefully

> **Source**: `/Users/Brian/Projects/Active/Forge/docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md`

This is the STABLE ANCHOR - the principles that must not be violated:

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

## Design Principles (Reference)

1. **Docs ARE the memory** - No accumulated context, agents read from files
2. **File-based communication** - Survives crashes, human-inspectable
3. **Hybrid audit lifecycle** - Fresh per phase group, avoids compaction
4. **Vibecoders first** - Hide complexity, show progress
5. **Pause anywhere** - User can always stop, rethink, modify
6. **Forward-looking** - Model unhobbling, assume capabilities improve
7. **Three-layer audit** - Builder self-check → Formal auditor → User vibes
8. **Iteration is expected** - Sessions polish through revision, not one-shot


---

## Architecture Decisions

> **Source**: `/Users/Brian/Projects/Active/Forge/docs/MAJOR_REFACTOR_MODE/DECISIONS.md`

Check that approved decisions from DECISIONS.md are followed:

# Major Refactor Mode - Implementation Decisions

> **Status**: Approved architecture
> **Created**: 2026-01-03
>
> ## For Claude Code Sessions
>
> This doc contains **approved architectural decisions**. Don't re-litigate unless user requests.
> For execution workflow, see `EXECUTION_PLAN.md`

---

## Executive Summary

Major Refactor Mode uses file-based agent coordination with "docs as memory" to enable multi-phase refactors that exceed single-session context limits. The orchestrator is an interactive supervisor (not a daemon), and you control parallelization at runtime.

---

## Key Decisions

### Decision 1: Orchestrator Model

**Rejected**: Polling daemon that runs in background, checks state every N seconds

**Why rejected**: Not interactive. Can't modify plans on the fly. Adds complexity without benefit.

**Approved**: Interactive supervisor in Warp terminal window that:
- Waits for signals from audit agents
- Asks you what to do next
- Lets you chat with it anytime to modify the plan
- Handles handoffs if context gets constrained

### Decision 2: Agent Communication

**Rejected**: WebSocket, IPC, message queues

**Why rejected**: Complex, fragile, hard to debug. Doesn't survive crashes.

**Approved**: File-based signals (JSON) in `.forge/refactors/{id}/signals/`:
- Human-inspectable and modifiable
- Survives crashes/restarts
- Works across Pi/Mac boundary
- Aligns with existing Forge patterns

### Decision 3: Memory Model

**Rejected**: Accumulated conversation context with summarization

**Why rejected**: Context compaction kills nuance. Summaries lose detail.

**Approved**: "Docs ARE the memory" - Agents start fresh, read from planning docs:
1. Read PHILOSOPHY.md (principles)
2. Read DECISIONS.md (architecture)
3. Read EXECUTION.md (current phase, exit criteria)
4. Do work
5. Write session log + handoff
6. Signal completion

### Decision 4: Audit Agent Lifecycle

**Rejected**: Per-phase audit agents (one per phase)

**Why rejected**: Too much context switching, loses coherence across related phases.

**Also rejected**: Single global audit agent for whole refactor

**Why rejected**: Context compaction over long refactor.

**Approved**: Hybrid - one audit agent per phase group:
- Related parallel phases share one audit (coherent review)
- New audit agent for each major milestone (fresh context)
- Best of both worlds

### Decision 5: Parallelization Control

**Rejected**: Automatic parallelization based on dependency graph

**Why rejected**: User bandwidth varies. Sometimes you want sequential even if parallel is possible.

**Approved**: User chooses at runtime:
- Orchestrator: "Phases 2 and 3 are ready. Run both in parallel, or one at a time?"
- System supports either mode
- Your attention is the bottleneck, not the dependency graph

### Decision 6: Approval Model

**Rejected**: Fixed approval gates at predetermined checkpoints

**Why rejected**: Real approvals depend on what audit finds, not arbitrary milestones.

**Approved**: Audit-based dynamic approval:
- Phase completes → Audit validates against philosophy
- If issues → Iterate with phase agent
- If passes → Signal orchestrator to advance
- You can intervene at any point via orchestrator chat

### Decision 7: Detection Trigger

**Rejected**: Hardcoded complexity thresholds (file count, line count, etc.)

**Why rejected**: Model judgment is better and improves over time.

**Approved**: Claude decides mid-conversation:
- During brainstorm, Claude realizes scope is too big
- Outputs recommendation: "This looks like a major architectural change..."
- AGI-pilled: trust the model, unhobble it

### Decision 8: iOS Handling

**Rejected**: Full Major Refactor Mode on iOS

**Why rejected**: Codebase analysis requires Mac-side file access.

**Approved**: Soft defer to Mac:
- iOS shows: "Major refactors need codebase analysis. Continue here for planning, or switch to Mac for full orchestration."
- Can still brainstorm and capture on iOS
- Execution happens on Mac

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FORGE APP (macOS)                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Brainstorm  │───▶│  Detection  │───▶│ Codebase Analysis   │ │
│  │    Chat     │    │   (Claude)  │    │ (PRE_REFACTOR.md)   │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│                                        ┌───────────▼──────────┐ │
│                                        │  Generate Planning   │ │
│                                        │       Docs           │ │
│                                        └───────────┬──────────┘ │
│                                                    │            │
└────────────────────────────────────────────────────┼────────────┘
                                                     │
┌────────────────────────────────────────────────────▼────────────┐
│                    .forge/refactors/{id}/                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │PHILOSOPHY.md │  │ DECISIONS.md │  │    EXECUTION.md      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │PRE_REFACTOR  │  │  ISSUES.md   │  │  signals/*.signal    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  ORCHESTRATOR │       │  PHASE AGENT  │       │  AUDIT AGENT  │
│    (Warp)     │◀──────│   (Worktree)  │──────▶│  (per group)  │
│  Supervisor   │       │  Does work    │       │  Validates    │
└───────────────┘       └───────────────┘       └───────────────┘
```

---

## What We're Building

| Component | Purpose | Phase |
|-----------|---------|-------|
| `forge/refactor/` module | Python backend for state, signals, CLI | 1 |
| Complexity detection | BrainstormAgent detects major refactors | 2 |
| Codebase analyzer | Generates PRE_REFACTOR.md | 2 |
| Orchestrator agent | Interactive supervisor in Warp | 3 |
| Phase agent | Worktree-based implementation | 4 |
| Audit agent | Philosophy validation | 4 |
| UI dashboard | Phase visualization in Forge app | 5 |
| Full integration | Pause/resume, Ship All, error handling | 6 |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-03 | File-based signals | Simpler than IPC, survives crashes, debuggable |
| 2026-01-03 | Docs as memory | Avoids context compaction |
| 2026-01-03 | Interactive orchestrator | Need to chat and modify plans |
| 2026-01-03 | Hybrid audit lifecycle | Balance coherence with compaction avoidance |
| 2026-01-03 | Runtime parallelization choice | User bandwidth is the bottleneck |
| 2026-01-03 | Claude decides detection | AGI-pilled, model judgment improves |


---

## What You're Validating

Review the following session work:

## Session 4.3

## Output from Session 4.3


# Session 4.3 Output

> **Completed**: 2026-01-03 22:30

## Summary

Session 4.3 completed

## Accomplishments

- See commit for details

## Issues Encountered

- None

## Handoff Notes

Ready for next session.


## Session 4.3 Instructions


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


---

## Code Changes Made

These are the actual commits from the sessions:

### Session 4.3 commit: 325f80e

commit 325f80e83f31d691536300d16d419240dd746533
Author: W1ndR1dr <W1ndR1dr@users.noreply.github.com>
Date:   Sat Jan 3 22:30:25 2026 -0800

    feat(refactor): Session 4.3 - Workflow polish & multi-commit audit fix
    
    - Add start_commit tracking so audit sees ALL session commits
    - Add user-facing workflow guidance to all agent templates
    - Planning: clear 'next step' after completion
    - Builder: 'return to orchestrator' cues
    - Audit: pass/fail/escalate guidance
    - User always knows what to do next
    
    🤖 Generated with [Claude Code](https://claude.com/claude-code)
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
---
 forge/refactor/audit_agent.py    | 102 +++++++++++++++++++++++++++++++++++----
 forge/refactor/planning_agent.py |   4 +-
 forge/refactor/prompts.py        |  32 +++++++++++-
 forge/refactor/session.py        |  19 +++++++-
 forge/refactor/state.py          |  23 +++++++--
 5 files changed, 163 insertions(+), 17 deletions(-)

diff --git a/forge/refactor/audit_agent.py b/forge/refactor/audit_agent.py
index c64bfe6..567baa5 100644
--- a/forge/refactor/audit_agent.py
+++ b/forge/refactor/audit_agent.py
@@ -192,15 +192,16 @@ class AuditAgent:
         Uses git to find what was changed, so the audit can validate
         the actual implementation, not just documented outputs.
 
-        Includes both stats AND actual patches so auditor can see the code.
+        Shows ALL commits made during the session (from start_commit to commit_hash),
+        not just the final commit. This ensures the auditor sees the full work.
         """
         import subprocess
 
         # Get commits from these sessions
         changes = []
-        max_lines_per_commit = 500  # Intelligent truncation per commit
+        max_lines_per_commit = 400  # Intelligent truncation per commit
         total_lines = 0
-        max_total_lines = 1500  # Cap total output
+        max_total_lines = 2000  # Cap total output (increased for multi-commit)
 
         state_path = self.refactor_dir / "state.json"
         if state_path.exists():
@@ -212,20 +213,82 @@ class AuditAgent:
                     break
 
                 session_state = state.get_session(session_id)
-                if session_state and session_state.commit_hash:
-                    commit_hash = session_state.commit_hash
+                if not session_state:
+                    continue
 
-                    # Get diff with actual patch content
+                start_commit = session_state.start_commit
+                end_commit = session_state.commit_hash
+
+                if not end_commit:
+                    changes.append(f"### Session {session_id}: No commit recorded\n")
+                    continue
+
+                # Track whether we successfully showed the range
+                showed_range = False
+
+                # If we have both start and end, try to show the range
+                if start_commit and start_commit != end_commit:
+                    changes.append(f"### Session {session_id} commits ({start_commit}..{end_commit}):\n")
+
+                    # First, list all commits in the range
                     try:
                         result = subprocess.run(
-                            ["git", "show", "--stat", "--patch", commit_hash],
+                            ["git", "log", "--oneline", f"{start_commit}..{end_commit}"],
+                            capture_output=True,
+                            text=True,
+                            cwd=self.project_root,
+                        )
+                        if result.returncode == 0 and result.stdout.strip():
+                            commit_list = result.stdout.strip().split('\n')
+                            changes.append(f"**Commits made ({len(commit_list)} total):**\n")
+                            for commit_line in commit_list:
+                                changes.append(f"- {commit_line}")
+                            changes.append("\n")
+
+                            # Show patches for each commit
+                            for commit_line in commit_list:
+                                if total_lines >= max_total_lines:
+                                    changes.append("\n... (truncated, too many changes)")
+                                    break
+
+                                commit_sha = commit_line.split()[0]
+                                try:
+                                    patch_result = subprocess.run(
+                                        ["git", "show", "--stat", "--patch", commit_sha],
+                                        capture_output=True,
+                                        text=True,
+                                        cwd=self.project_root,
+                                    )
+                                    if patch_result.returncode == 0:
+                                        changes.append(f"\n#### Commit {commit_sha}\n")
+                                        lines = patch_result.stdout.split('\n')
+                                        truncated = lines[:max_lines_per_commit]
+                                        changes.append('\n'.join(truncated))
+                                        if len(lines) > max_lines_per_commit:
+                                            changes.append(f"\n... ({len(lines) - max_lines_per_commit} more lines)")
+                                        total_lines += min(len(lines), max_lines_per_commit)
+                                except Exception:
+                                    pass
+
+                            showed_range = True
+                    except Exception:
+                        # Fall back to showing just the end commit
+                        changes.append(f"(Could not get commit range, falling back to final commit)\n")
+
+                # Show single commit if no range or range failed
+                if not showed_range:
+                    if not (start_commit and start_commit != end_commit):
+                        # Only add header if we haven't already (no failed range attempt)
+                        changes.append(f"### Session {session_id} commit: {end_commit}\n")
+
+                    try:
+                        result = subprocess.run(
+                            ["git", "show", "--stat", "--patch", end_commit],
                             capture_output=True,
                             text=True,
                             cwd=self.project_root,
                         )
                         if result.returncode == 0:
-                            changes.append(f"### Commit {commit_hash} (Session {session_id})\n")
-                            # Truncate per-commit but show actual code
                             lines = result.stdout.split('\n')
                             truncated = lines[:max_lines_per_commit]
                             changes.append('\n'.join(truncated))
@@ -413,6 +476,9 @@ This is a guide, not a gate. Use your judgment on severity and relevance.
    forge refactor audit-fail {self.refactor_id} {sessions_str} --issues "Brief summary of issues"
    ```
 
+3. Tell the user:
+   > "Audit FAILED for sessions {sessions_str}. Return to the orchestrator to relay fixes to the builder."
+
 ### If Audit Passes:
 
 1. Run this command to signal approval:
@@ -421,7 +487,23 @@ This is a guide, not a gate. Use your judgment on severity and relevance.
    ```
 
 2. Tell the user:
-   > "Audit PASSED for sessions {sessions_str}. Work aligns with philosophy."
+   > "Audit PASSED for sessions {sessions_str}. Work aligns with philosophy.
+   >
+   > Return to the orchestrator to close out this session and continue to the next."
+
+### If Escalation is Needed:
+
+If you observe recurring issues across iterations, fundamental architectural problems, or scope confusion that revision won't fix:
+
+1. Run this command to signal escalation:
+   ```bash
+   forge refactor escalate {self.refactor_id} {sessions_str} --reason "Brief explanation"
+   ```
+
+2. Tell the user:
+   > "Recommend ESCALATING sessions {sessions_str}. This needs human decision.
+   >
+   > Return to the orchestrator to discuss next steps."
 
 ---
 
diff --git a/forge/refactor/planning_agent.py b/forge/refactor/planning_agent.py
index 48414e0..84f55e5 100644
--- a/forge/refactor/planning_agent.py
+++ b/forge/refactor/planning_agent.py
@@ -239,7 +239,9 @@ When the user approves (says "write it", "looks good", "yes", etc.):
 **End with:**
 > "Planning complete! Docs are in `{refactor_dir}/`.
 >
-> To start Phase 1, run: `forge refactor start {refactor_id} 1.1`"
+> **Next steps:**
+> - To launch the orchestrator (recommended): `forge refactor orchestrate {refactor_id}`
+> - To start Phase 1 directly: `forge refactor start {refactor_id} 1.1`"
 
 ---
 
diff --git a/forge/refactor/prompts.py b/forge/refactor/prompts.py
index 44c5c49..1884b44 100644
--- a/forge/refactor/prompts.py
+++ b/forge/refactor/prompts.py
@@ -503,7 +503,8 @@ Before doing anything substantial, ensure you understand:
    > "Ready to launch [session]. HANDS OFF KEYBOARD AND MOUSE until the new agent is running. Say 'go' when ready."
 4. Wait for user confirmation
 5. Run: `forge refactor start {refactor_id} <session-id>`
-6. Report the new session has been launched
+6. **AFTER launching**, tell the user:
+   > "Session [X.Y] is now running. Let me know when it signals done (it will say 'Session X.Y ready for review')."
 
 **Why the pause?** AppleScript needs a few seconds to open new terminal tabs. Active keyboard/mouse input interferes with the launch. This applies to ALL agent launches (sessions, orchestrators, auditors).
 
@@ -516,6 +517,35 @@ Before doing anything substantial, ensure you understand:
 5. Make changes, document rationale in DECISIONS.md
 6. Summarize what you changed
 
+### "session is done" / "ready for review" / "builder finished"
+
+When a session signals completion:
+
+1. Acknowledge: "Great! Session [X.Y] is done. Let's run the audit."
+2. **BEFORE launching audit**, prompt the user:
+   > "Ready to launch audit for [X.Y]. HANDS OFF KEYBOARD AND MOUSE until the auditor is running. Say 'go' when ready."
+3. Wait for user confirmation
+4. Run: `forge refactor audit {refactor_id} <session-id>`
+5. **AFTER launching**, tell the user:
+   > "Audit is now running. Let me know when it signals pass, fail, or escalate."
+
+### "audit passed" / "auditor approved"
+
+When audit passes:
+
+1. Acknowledge: "Excellent! Audit passed for [X.Y]."
+2. Tell the user they can close terminals:
+   > "[X.Y] is fully closed out. You can close the [X.Y] builder and audit terminal windows."
+3. Suggest next action: "Ready for the next session when you are."
+
+### "audit failed" / "needs revision"
+
+When audit fails:
+
+1. Read the issues from the audit results
+2. Tell the user: "Audit found issues for [X.Y]. I'll relay them to the builder."
+3. Help the user return to the builder session to address the issues
+
 ### Questions about the refactor
 
 Answer based on the docs. Reference specific files and sections.
diff --git a/forge/refactor/session.py b/forge/refactor/session.py
index af64738..d6d029d 100644
--- a/forge/refactor/session.py
+++ b/forge/refactor/session.py
@@ -382,8 +382,23 @@ Always end your work with a clear next-step for the user.
                 error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
                 return False, f"Failed to create worktree: {error_msg}"
 
-        # Start the session in state
-        state.start_session(self.session_id)
+        # Capture current HEAD before session starts (for multi-commit audit)
+        git_cwd = worktree_path if worktree_path else self.project_root
+        start_commit = None
+        try:
+            result = subprocess.run(
+                ["git", "rev-parse", "HEAD"],
+                capture_output=True,
+                text=True,
+                cwd=git_cwd,
+            )
+            if result.returncode == 0:
+                start_commit = result.stdout.strip()[:7]
+        except Exception:
+            pass
+
+        # Start the session in state (with start_commit for audit tracking)
+        state.start_session(self.session_id, start_commit=start_commit)
         state.save(state_path)
 
         # Write SESSION_STARTED signal
diff --git a/forge/refactor/state.py b/forge/refactor/state.py
index 796467e..aaac4a7 100644
--- a/forge/refactor/state.py
+++ b/forge/refactor/state.py
@@ -52,7 +52,8 @@ class SessionState:
     status: SessionStatus = SessionStatus.PENDING
     started_at: Optional[str] = None
     completed_at: Optional[str] = None
-    commit_hash: Optional[str] = None
+    start_commit: Optional[str] = None  # HEAD when session started (for multi-commit audit)
+    commit_hash: Optional[str] = None  # HEAD when session completed
     audit_result: AuditResult = AuditResult.PENDING
     notes: str = ""  # Handoff notes for next session
     iteration_count: int = 0  # Tracks audit iterations for visibility
@@ -64,6 +65,7 @@ class SessionState:
             "status": self.status.value,
             "started_at": self.started_at,
             "completed_at": self.completed_at,
+            "start_commit": self.start_commit,
             "commit_hash": self.commit_hash,
             "audit_result": self.audit_result.value,
             "notes": self.notes,
@@ -78,6 +80,7 @@ class SessionState:
             status=SessionStatus(data.get("status", "pending")),
             started_at=data.get("started_at"),
             completed_at=data.get("completed_at"),
+            start_commit=data.get("start_commit"),
             commit_hash=data.get("commit_hash"),
             audit_result=AuditResult(data.get("audit_result", "pending")),
             notes=data.get("notes", ""),
@@ -203,8 +206,19 @@ class RefactorState:
         """Get a session by ID."""
         return self.sessions.get(session_id)
 
-    def start_session(self, session_id: str) -> SessionState:
-        """Mark a session as started."""
+    def start_session(
+        self,
+        session_id: str,
+        start_commit: Optional[str] = None,
+    ) -> SessionState:
+        """
+        Mark a session as started.
+
+        Args:
+            session_id: The session identifier (e.g., "1.1")
+            start_commit: Current HEAD commit when session starts.
+                         Used by audit to show ALL commits made during session.
+        """
         if session_id not in self.sessions:
             self.add_session(session_id)
 
@@ -212,6 +226,8 @@ class RefactorState:
         old_status = session.status
         session.status = SessionStatus.IN_PROGRESS
         session.started_at = datetime.now().isoformat()
+        if start_commit:
+            session.start_commit = start_commit
         self.current_session = session_id
         self.status = RefactorStatus.EXECUTING
         if self.started_at is None:
@@ -221,6 +237,7 @@ class RefactorState:
             session_id=session_id,
             old_status=old_status.value,
             new_status=session.status.value,
+            start_commit=start_commit,
         )
         return session
 


---

## What to Check

Review against these areas, using your judgment on what matters for THIS session:

**From PHILOSOPHY.md:**
- Docs as memory (updates files, not just conversation?)
- File-based signals (no IPC/WebSocket complexity?)
- Iteration-friendly (handles revision gracefully?)
- Anti-patterns avoided?

**From DECISIONS.md:**
- Follows approved architecture decisions?
- Avoids explicitly rejected approaches?

**Quality:**
- Complete per exit criteria?
- Obvious gaps or shortcuts?
- Does the code match the documented intent?

This is a guide, not a gate. Use your judgment on severity and relevance.

---

## How to Report

### If Issues Found:

1. Create `audit-results/issues.md` with specific issues:
   ```markdown
   # Audit Issues - 4.3

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail major-refactor-mode-phase-1 4.3 --issues "Brief summary of issues"
   ```

3. Tell the user:
   > "Audit FAILED for sessions 4.3. Return to the orchestrator to relay fixes to the builder."

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass major-refactor-mode-phase-1 4.3
   ```

2. Tell the user:
   > "Audit PASSED for sessions 4.3. Work aligns with philosophy.
   >
   > Return to the orchestrator to close out this session and continue to the next."

### If Escalation is Needed:

If you observe recurring issues across iterations, fundamental architectural problems, or scope confusion that revision won't fix:

1. Run this command to signal escalation:
   ```bash
   forge refactor escalate major-refactor-mode-phase-1 4.3 --reason "Brief explanation"
   ```

2. Tell the user:
   > "Recommend ESCALATING sessions 4.3. This needs human decision.
   >
   > Return to the orchestrator to discuss next steps."

---

## Important Notes

- Be specific about what doesn't align and WHY
- Reference specific principles from PHILOSOPHY.md or DECISIONS.md
- Suggest how to fix issues, don't just point them out
- Don't be pedantic about minor style issues
- Iteration is expected - revision is normal, not failure

---

## Begin

1. Read the philosophy and decisions sections above CAREFULLY
2. Review each session's work and code changes
3. Check against principles using your judgment
4. Report your findings
