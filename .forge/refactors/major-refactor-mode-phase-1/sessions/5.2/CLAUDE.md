# Execution Session: Phase Cards & Notifications

> **Refactor**: major-refactor-mode-phase-1
> **Session**: 5.2
> **Generated**: 2026-01-04 01:22

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

## Thinking Depth (Suggest to User)

If after reading the docs you believe this session would benefit from deeper reasoning, tell the user BEFORE starting work:

- **ultrathink**: Suggest for architectural decisions, security-sensitive code, or complex multi-file changes
- **plan mode**: Suggest if scope is unclear and you need to explore before committing to an approach

Example: "This session involves architectural decisions. I'd recommend launching me with ultrathink. Want to restart with that enabled?"

If already appropriate for the task, just proceed.

---

## Your Mission

FIRST: Read these design research docs:
- docs/design/UI_PATTERNS_RESEARCH.md - UX patterns from Linear, Asana, Basecamp
- docs/design/LINEAR_SWIFTUI_GUIDE.md - SwiftUI implementation patterns

User preferences:
- Rebuild > Remodel: Start fresh if it produces better result than adapting existing code
- No sentimentality about existing UI
- Pre-MVP mindset, zero technical debt

Key patterns from research:
- Calm notifications (badge-only by default, not naggy)
- Progressive disclosure for phase details
- 150-200ms animation timing
- Decision prompts: context + specific ask + escape hatch

Look at ForgeApp/Design/DesignTokens.swift for styling.
Look at ForgeApp/Design/Components/WorkspaceCard.swift for card pattern.

Enhance Major Refactor Mode UI:

1. Create ForgeApp/Views/Refactor/PhaseCardView.swift:
   - Extend WorkspaceCard pattern
   - Show: phase name, status, active worktrees count
   - Click to expand details
   - "Open Terminal" button to launch worktree

2. Add notifications system:
   - In-app toasts: ForgeApp/Views/Components/ToastView.swift
   - macOS system notifications using UNUserNotificationCenter
   - Notification triggers:
     - Phase started
     - Phase complete
     - Audit passed/failed
     - Needs attention

3. Add mode switch to BrainstormChatView:
   - Detect MAJOR_REFACTOR_RECOMMENDED in Claude's response
   - Show: "Claude recommends Major Refactor Mode" banner
   - Button: "Switch to Major Refactor Mode"
   - On click: navigate to refactor creation flow

4. Run xcodegen generate before building

Test: Trigger a notification, see it appear. Start brainstorm with
large idea, see mode switch button.

---

## Scope

**IN scope**: Phase cards, notifications, mode switch in brainstorm

**OUT of scope**: Pause/resume (Phase 6)

---

## When to Ask the User

- Phase card design looks right
- Notification wording is good
- Mode switch placement in brainstorm is correct

---

## Exit Criteria

Before marking this session complete, verify ALL of these:

- [ ] PhaseCardView shows rich phase information
- [ ] In-app toast notifications work
- [ ] macOS system notifications work
- [ ] BrainstormChatView detects MAJOR_REFACTOR_RECOMMENDED
- [ ] Mode switch button appears and navigates correctly

---

## Git Instructions

When all exit criteria are met:

```bash
cd ForgeApp && xcodegen generate
git add ForgeApp/
git commit -m "feat(refactor): Session 5.2 - Phase cards and notifications

- Add PhaseCardView with rich phase info
- Add notification system (in-app + macOS)
- Add mode switch trigger in BrainstormChatView
- Detect MAJOR_REFACTOR_RECOMMENDED marker"
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
   forge refactor done 5.2
   ```

2. Tell the user:
   > "Session 5.2 ready for review. All exit criteria verified and committed."

**Note:** This signals "work complete, ready for audit" - NOT final approval. The orchestrator or audit agent will review. If issues are found, you may be asked to revise.

---

## Communicating Back to User

You are one agent in a multi-agent workflow. The user coordinates between you and the orchestrator.

**After completing work (or a revision cycle):**
> "Session 5.2 complete.
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

Note for Phase 6:
- How notifications are triggered
- How mode switch works
- What's left for full integration
