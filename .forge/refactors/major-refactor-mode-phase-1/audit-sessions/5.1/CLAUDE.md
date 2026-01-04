# Audit Session

> **Refactor**: major-refactor-mode-phase-1
> **Sessions Under Review**: 5.1
> **Generated**: 2026-01-04 00:56

---

## Your Role: Guardian of Idea Fidelity

You are the **Audit Agent** - your job is to prevent drift and ensure the implementation
aligns with the original vision and principles.

**Key insight**: You're catching structural issues. The user will also do a "vibes check"
to catch feel/intent issues. Together, you form a two-layer validation system.

---

## Thinking Depth (Suggest to User)

If after reading the scope you believe this audit would benefit from deeper reasoning, tell the user BEFORE starting:

- **ultrathink**: Suggest for reviewing architectural changes, security-sensitive code, or complex multi-file changes

Example: "This audit covers significant architectural changes. I'd recommend launching me with ultrathink. Want to restart with that enabled?"

If already appropriate for the task, just proceed.

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
| 2026-01-03 | Three-layer audit | Builder self-check → Formal auditor → User vibes |
| 2026-01-03 | No hardcoded iteration limits | Model judges escalation, not MAX_ITERATIONS constant |
| 2026-01-03 | PRE_REFACTOR.md as planning byproduct | Planning Agent generates it, not separate analyze step |
| 2026-01-03 | Testing = signals, not source of truth | Three-layer audit + spec-first tests; user vibes ungameable |

---

## Resolved Questions

Questions that were open, now decided:

### Decision: PRE_REFACTOR.md Generation

**Rejected**: Separate `forge refactor analyze` step before planning

**Why rejected**: Clutters workflow, duplicates exploration, may miss nuance

**Approved**: Planning Agent generates PRE_REFACTOR.md as byproduct at end of planning

**Rationale**:
- Captures what Planning Agent actually understood (not a generic scan)
- No separate workflow step
- Becomes immutable "before" snapshot for audit comparison
- `forge refactor analyze` becomes optional fallback if Planning Agent didn't generate one

**Decided**: 2026-01-03 (via Prometheus consultation)

---

### Decision: Testing Strategy

**Rejected**: Automated tests as primary quality signal

**Why rejected**: Reward hacking - LLMs can optimize for metrics (green checkmarks) rather than actual correctness

**Approved**: Three-layer audit + spec-first tests for regression

**Rationale**:
- User vibes is the ungameable oracle (human intuition, not formal spec)
- Tests are one signal among many, not source of truth
- Spec-first tests (written BEFORE implementation) define target, can't be gamed
- Regression tests catch breaks over time (safety net)
- See PHILOSOPHY.md "Testing in AI-Assisted Development" for full framing

**Decided**: 2026-01-03 (via Prometheus consultation)


---

## What You're Validating

Review the following session work:

## Session 5.1

## Output from Session 5.1


# Session 5.1 Output

> **Completed**: 2026-01-04 00:54

## Summary

Session 5.1 completed

## Accomplishments

- See commit for details

## Issues Encountered

- None

## Handoff Notes

Ready for next session.


## Session 5.1 Instructions


# Execution Session: Models & Basic View

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 5.1
> **Generated**: 2026-01-04 00:31

---

## FIRST: Read These Docs (REQUIRED)

Before doing ANYTHING, read these files to understand the context:

**Philosophy & Decisions:**
1. `docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md` - Guiding principles
2. `docs/MAJOR_REFACTOR_MODE/DECISIONS.md` - Architecture decisions (don't re-litigate)

**Phase-Level Context:**
**CRITICAL FOR ALL PHASE 5 SESSIONS:**

**Required Reading:**
- `docs/design/UI_PATTERNS_RESEARCH.md` - UX patterns from Linear, Asana, Basecamp
- `docs/design/LINEAR_SWIFTUI_GUIDE.md` - SwiftUI implementation patterns (use as inspiration, not prescription)

**User Preferences:**
- No sentimentality about existing UI - full redesign is fine
- Pre-MVP mindset - zero technical debt
- **Rebuild > Remodel**: If starting fresh produces a better result than adapting existing code, start fresh. Don't salvage code just because it exists.
- Refactor belongs in project view (project-specific)
- Data source: Read local `.forge/refactors/` files directly (no API for Mac app)
- Deep research threads available: Ask user to spawn if needed for design questions

---

## Your Mission

FIRST: Read the design research docs (see Phase 5 header above).

Design vision from research:
- Stepped progress indicator: [✓ Planning] ──→ [● Foundation] - - → [○ Polish]
- Linear-inspired dark mode (use as inspiration, not prescription)
- Dense rows (32-36px), 150ms hover transitions
- Progressive disclosure (collapsed by default, count badges)

Look at existing patterns in ForgeApp/Models/Feature.swift and
ForgeApp/Design/Components/WorkspaceCard.swift - but feel free to deviate
if the research suggests better patterns.

Add Major Refactor Mode to Forge macOS app:

1. Create ForgeApp/Models/RefactorPlan.swift:
   - RefactorPlan struct (mirrors Python RefactorState)
   - RefactorPhase struct
   - PhaseStatus enum
   - Codable for JSON parsing

2. Create ForgeApp/Views/Refactor/RefactorDashboardView.swift:
   - List of phases with status indicators
   - Current phase highlighted
   - Simple list view (railroad track is stretch goal for later)
   - Use existing DesignTokens for styling

3. Create ForgeApp/Services/RefactorClient.swift:
   - fetchRefactors() -> [RefactorPlan]
   - fetchRefactor(id) -> RefactorPlan
   - Use existing APIClient patterns

4. Add navigation to refactor dashboard from main app
   - Maybe a "Refactors" section in sidebar
   - Or accessible from project view

5. Run xcodegen generate before building

Test: Create a test refactor via CLI, see it appear in the app.

---

## Scope

**IN scope**: Swift models, basic dashboard view

**OUT of scope**: Notifications, mode switch (5.2)

---

## When to Ask the User

- The phase list UI looks right (show a screenshot/mockup)
- Navigation placement is correct
- You need to add API endpoints to Python server first

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] RefactorPlan.swift model exists and parses correctly
- [ ] RefactorDashboardView shows list of phases
- [ ] Can navigate to dashboard from main app
- [ ] Styling follows design research (or explains deviation)

---

## Git Instructions

When all exit criteria are met:

```bash
cd ForgeApp && xcodegen generate
git add ForgeApp/
git commit -m "feat(refactor): Session 5.1 - Swift models and basic dashboard

- Add RefactorPlan model
- Add RefactorDashboardView with phase list
- Add RefactorClient for local file reading
- Navigate from main app to refactor view"
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
   forge refactor done 5.1
   ```

2. Tell the user:
   > "Session 5.1 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session 5.1 complete.
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

Note for Session 5.2:
- What models exist
- How navigation works
- What styling was used
- Any design decisions made


---

## Code Changes Made

These are the actual commits from the sessions:

### Session 5.1 commits (7158981..e84c3e9):

**Commits made (1 total):**

- e84c3e9 feat(refactor): Session 5.1 - Swift models and basic dashboard



#### Commit e84c3e9

commit e84c3e9172c99f21e246050af26e450c8f631b25
Author: W1ndR1dr <W1ndR1dr@users.noreply.github.com>
Date:   Sun Jan 4 00:54:14 2026 -0800

    feat(refactor): Session 5.1 - Swift models and basic dashboard
    
    - Add RefactorPlan model mirroring Python RefactorState
    - Add RefactorClient for reading local .forge/refactors/ files
    - Add RefactorDashboardView with stepped progress indicator
    - Integrate dashboard into WorkspaceView (macOS only)
    - Design follows Linear-inspired patterns from UI research
    
    🤖 Generated with [Claude Code](https://claude.com/claude-code)
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
---
 ForgeApp/Models/RefactorPlan.swift                 | 305 +++++++++++++
 ForgeApp/Services/RefactorClient.swift             | 174 +++++++
 .../Views/Refactor/RefactorDashboardView.swift     | 505 +++++++++++++++++++++
 ForgeApp/Views/Workspace/WorkspaceView.swift       |   7 +-
 4 files changed, 990 insertions(+), 1 deletion(-)

diff --git a/ForgeApp/Models/RefactorPlan.swift b/ForgeApp/Models/RefactorPlan.swift
new file mode 100644
index 0000000..1222f08
--- /dev/null
+++ b/ForgeApp/Models/RefactorPlan.swift
@@ -0,0 +1,305 @@
+import Foundation
+
+// MARK: - Refactor Status Enums
+
+/// Status of an overall refactor
+enum RefactorStatus: String, Codable, CaseIterable {
+    case planning = "planning"
+    case executing = "executing"
+    case paused = "paused"
+    case completed = "completed"
+
+    var displayName: String {
+        switch self {
+        case .planning: return "Planning"
+        case .executing: return "Executing"
+        case .paused: return "Paused"
+        case .completed: return "Completed"
+        }
+    }
+
+    var color: String {
+        switch self {
+        case .planning: return "purple"
+        case .executing: return "blue"
+        case .paused: return "orange"
+        case .completed: return "green"
+        }
+    }
+}
+
+/// Status of a single execution session
+enum SessionStatus: String, Codable, CaseIterable {
+    case pending = "pending"
+    case inProgress = "in_progress"
+    case completed = "completed"
+    case needsRevision = "needs_revision"
+
+    var displayName: String {
+        switch self {
+        case .pending: return "Pending"
+        case .inProgress: return "In Progress"
+        case .completed: return "Completed"
+        case .needsRevision: return "Needs Revision"
+        }
+    }
+}
+
+/// Result of an audit review
+enum AuditResult: String, Codable {
+    case pending = "pending"
+    case passed = "passed"
+    case failed = "failed"
+}
+
+// MARK: - Refactor Session State
+
+/// State for a single execution session in a refactor
+struct RefactorSessionState: Identifiable, Codable, Hashable {
+    let sessionId: String
+    var status: SessionStatus
+    var startedAt: String?
+    var completedAt: String?
+    var startCommit: String?
+    var commitHash: String?
+    var auditResult: AuditResult
+    var notes: String
+    var iterationCount: Int
+
+    var id: String { sessionId }
+
+    enum CodingKeys: String, CodingKey {
+        case sessionId = "session_id"
+        case status
+        case startedAt = "started_at"
+        case completedAt = "completed_at"
+        case startCommit = "start_commit"
+        case commitHash = "commit_hash"
+        case auditResult = "audit_result"
+        case notes
+        case iterationCount = "iteration_count"
+    }
+
+    init(
+        sessionId: String,
+        status: SessionStatus = .pending,
+        startedAt: String? = nil,
+        completedAt: String? = nil,
+        startCommit: String? = nil,
+        commitHash: String? = nil,
+        auditResult: AuditResult = .pending,
+        notes: String = "",
+        iterationCount: Int = 0
+    ) {
+        self.sessionId = sessionId
+        self.status = status
+        self.startedAt = startedAt
+        self.completedAt = completedAt
+        self.startCommit = startCommit
+        self.commitHash = commitHash
+        self.auditResult = auditResult
+        self.notes = notes
+        self.iterationCount = iterationCount
+    }
+
+    init(from decoder: Decoder) throws {
+        let container = try decoder.container(keyedBy: CodingKeys.self)
+        sessionId = try container.decode(String.self, forKey: .sessionId)
+
+        // Handle status string → enum
+        let statusString = try container.decodeIfPresent(String.self, forKey: .status) ?? "pending"
+        status = SessionStatus(rawValue: statusString) ?? .pending
+
+        startedAt = try container.decodeIfPresent(String.self, forKey: .startedAt)
+        completedAt = try container.decodeIfPresent(String.self, forKey: .completedAt)
+        startCommit = try container.decodeIfPresent(String.self, forKey: .startCommit)
+        commitHash = try container.decodeIfPresent(String.self, forKey: .commitHash)
+
+        let auditString = try container.decodeIfPresent(String.self, forKey: .auditResult) ?? "pending"
+        auditResult = AuditResult(rawValue: auditString) ?? .pending
+
+        notes = try container.decodeIfPresent(String.self, forKey: .notes) ?? ""
+        iterationCount = try container.decodeIfPresent(Int.self, forKey: .iterationCount) ?? 0
+    }
+}
+
+// MARK: - State Change (Audit Log)
+
+/// A single state change entry for the audit log
+struct StateChange: Codable {
+    let timestamp: String
+    let action: String
+    let details: [String: String]
+
+    init(timestamp: String, action: String, details: [String: String] = [:]) {
+        self.timestamp = timestamp
+        self.action = action
+        self.details = details
+    }
+
+    init(from decoder: Decoder) throws {
+        let container = try decoder.container(keyedBy: CodingKeys.self)
+        timestamp = try container.decode(String.self, forKey: .timestamp)
+        action = try container.decode(String.self, forKey: .action)
+
+        // Details can be complex, simplify to string dictionary
+        if let details = try? container.decode([String: String].self, forKey: .details) {
+            self.details = details
+        } else {
+            self.details = [:]
+        }
+    }
+
+    enum CodingKeys: String, CodingKey {
+        case timestamp
+        case action
+        case details
+    }
+}
+
+// MARK: - Refactor State
+
+/// Runtime state for a refactor execution
+/// Stored at: .forge/refactors/{id}/state.json
+struct RefactorState: Identifiable, Codable {
+    let refactorId: String
+    var status: RefactorStatus
+    var currentSession: String?
+    var sessions: [String: RefactorSessionState]
+    var startedAt: String?
+    var updatedAt: String
+    var completedAt: String?
+    var history: [StateChange]
+
+    var id: String { refactorId }
+
+    enum CodingKeys: String, CodingKey {
+        case refactorId = "refactor_id"
+        case status
+        case currentSession = "current_session"
+        case sessions
+        case startedAt = "started_at"
+        case updatedAt = "updated_at"
+        case completedAt = "completed_at"
+        case history
+    }
+
+    init(
+        refactorId: String,
+        status: RefactorStatus = .planning,
+        currentSession: String? = nil,
+        sessions: [String: RefactorSessionState] = [:],
+        startedAt: String? = nil,
+        updatedAt: String = ISO8601DateFormatter().string(from: Date()),
+        completedAt: String? = nil,
+        history: [StateChange] = []
+    ) {
+        self.refactorId = refactorId
+        self.status = status
+        self.currentSession = currentSession
+        self.sessions = sessions
+        self.startedAt = startedAt
+        self.updatedAt = updatedAt
+        self.completedAt = completedAt
+        self.history = history
+    }
+
+    init(from decoder: Decoder) throws {
+        let container = try decoder.container(keyedBy: CodingKeys.self)
+        refactorId = try container.decode(String.self, forKey: .refactorId)
+
+        let statusString = try container.decodeIfPresent(String.self, forKey: .status) ?? "planning"
+        status = RefactorStatus(rawValue: statusString) ?? .planning
+
+        currentSession = try container.decodeIfPresent(String.self, forKey: .currentSession)
+
+        // Sessions is a dictionary
+        sessions = try container.decodeIfPresent([String: RefactorSessionState].self, forKey: .sessions) ?? [:]
+
+        startedAt = try container.decodeIfPresent(String.self, forKey: .startedAt)
+        updatedAt = try container.decodeIfPresent(String.self, forKey: .updatedAt)
+            ?? ISO8601DateFormatter().string(from: Date())
+        completedAt = try container.decodeIfPresent(String.self, forKey: .completedAt)
+        history = try container.decodeIfPresent([StateChange].self, forKey: .history) ?? []
+    }
+
+    // MARK: - Computed Properties
+
+    /// Sessions sorted by ID (e.g., "1.1", "1.2", "2.1")
+    var sortedSessions: [RefactorSessionState] {
+        sessions.values.sorted { a, b in
+            // Parse "1.1", "2.1" etc. for proper ordering
+            let partsA = a.sessionId.split(separator: ".").compactMap { Int($0) }
+            let partsB = b.sessionId.split(separator: ".").compactMap { Int($0) }
+
+            // Compare phase first, then session number
+            for (pa, pb) in zip(partsA, partsB) {
+                if pa != pb { return pa < pb }
+            }
+            return partsA.count < partsB.count
+        }
+    }
+
+    /// Completed sessions count
+    var completedCount: Int {
+        sessions.values.filter { $0.status == .completed }.count
+    }
+
+    /// Total sessions count
+    var totalCount: Int {
+        sessions.count
+    }
+
+    /// Progress as fraction (0.0 to 1.0)
+    var progress: Double {
+        guard totalCount > 0 else { return 0 }
+        return Double(completedCount) / Double(totalCount)
+    }
+
+    /// Whether all sessions are completed
+    var isComplete: Bool {
+        guard !sessions.isEmpty else { return false }
+        return sessions.values.allSatisfy { $0.status == .completed }
+    }
+
+    /// Pending sessions
+    var pendingSessions: [RefactorSessionState] {
+        sortedSessions.filter { $0.status == .pending }
+    }
+
+    /// Current session state (if any)
+    var currentSessionState: RefactorSessionState? {
+        guard let id = currentSession else { return nil }
+        return sessions[id]
+    }
+}
+
+// MARK: - Refactor Plan (UI-Friendly Wrapper)
+
+/// High-level refactor plan with metadata from docs
+/// Combines state.json with metadata from CLAUDE.md/README.md
+struct RefactorPlan: Identifiable {
+    let id: String
+    let title: String
+    let description: String?
+    let state: RefactorState
+    let path: URL
+
+    /// Display title (human-readable)
+    var displayTitle: String {
+        title.replacingOccurrences(of: "-", with: " ")
+            .split(separator: " ")
+            .map { $0.capitalized }
+            .joined(separator: " ")
+    }
+
+    /// Status badge color
+    var statusColor: String {
+        state.status.color
+    }
+
+    /// Progress percentage (0-100)
+    var progressPercent: Int {
+        Int(state.progress * 100)
+    }
+}
diff --git a/ForgeApp/Services/RefactorClient.swift b/ForgeApp/Services/RefactorClient.swift
new file mode 100644
index 0000000..f06b568
--- /dev/null
+++ b/ForgeApp/Services/RefactorClient.swift
@@ -0,0 +1,174 @@
+import Foundation
+
+/// Client for reading refactor state from local filesystem
+/// Reads directly from .forge/refactors/ directories (no API needed for macOS)
+@MainActor
+final class RefactorClient {
+
+    // MARK: - Errors
+
+    enum RefactorError: LocalizedError {
+        case refactorNotFound(String)
+        case invalidRefactorId(String)
+        case parseError(String)
+
+        var errorDescription: String? {
+            switch self {
+            case .refactorNotFound(let id):
+                return "Refactor not found: \(id)"
+            case .invalidRefactorId(let id):
+                return "Invalid refactor ID: \(id)"
+            case .parseError(let detail):
+                return "Failed to parse refactor state: \(detail)"
+            }
+        }
+    }
+
+    // MARK: - Public API
+
+    /// Fetch all refactors for a project
+    /// - Parameter projectPath: Absolute path to project root
+    /// - Returns: List of RefactorPlan objects
+    func fetchRefactors(projectPath: String) async throws -> [RefactorPlan] {
+        let projectURL = URL(fileURLWithPath: projectPath)
+        let refactorsDir = projectURL.appendingPathComponent(".forge/refactors")
+
+        // Check if refactors directory exists
+        var isDirectory: ObjCBool = false
+        guard FileManager.default.fileExists(atPath: refactorsDir.path, isDirectory: &isDirectory),
+              isDirectory.boolValue else {
+            // No refactors yet - return empty list (not an error)
+            return []
+        }
+
+        // Scan for refactor subdirectories
+        let contents = try FileManager.default.contentsOfDirectory(
+            at: refactorsDir,
+            includingPropertiesForKeys: [.isDirectoryKey],
+            options: [.skipsHiddenFiles]
+        )
+
+        var refactors: [RefactorPlan] = []
+
+        for url in contents {
+            // Skip non-directories
+            guard (try? url.resourceValues(forKeys: [.isDirectoryKey]).isDirectory) == true else {
+                continue
+            }
+
+            // Try to load refactor from this directory
+            if let plan = try? await loadRefactor(from: url) {
+                refactors.append(plan)

... (643 more lines)

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
   # Audit Issues - 5.1

   ## Critical Issues
   - [Session X.Y] Principle violated: "..." - [description]

   ## Warnings
   - [Session X.Y] Potential drift: [description]

   ## Suggestions
   - [How to fix each issue]
   ```

2. Run this command to signal revision needed:
   ```bash
   forge refactor audit-fail major-refactor-mode-phase-1 5.1 --issues "Brief summary of issues"
   ```

3. Tell the user:
   > "Audit FAILED for session 5.1.
   >
   > **Go back to your orchestrator terminal** and paste this output. The orchestrator will guide you through getting fixes from the builder."

### If Audit Passes:

1. Run this command to signal approval:
   ```bash
   forge refactor audit-pass major-refactor-mode-phase-1 5.1
   ```

2. Tell the user:
   > "Audit PASSED for session 5.1. Work aligns with philosophy.
   >
   > **Go back to your orchestrator terminal** and tell them the audit passed. They'll guide you to the next step."

### If Escalation is Needed:

If you observe recurring issues across iterations, fundamental architectural problems, or scope confusion that revision won't fix:

1. Run this command to signal escalation:
   ```bash
   forge refactor escalate major-refactor-mode-phase-1 5.1 --reason "Brief explanation"
   ```

2. Tell the user:
   > "Recommend ESCALATING session 5.1. This needs a human decision - the issue is too fundamental for automated revision.
   >
   > **Go back to your orchestrator terminal** and paste this output. We'll figure out the right path forward together."

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
