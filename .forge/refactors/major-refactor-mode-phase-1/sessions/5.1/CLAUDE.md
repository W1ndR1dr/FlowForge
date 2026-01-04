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
