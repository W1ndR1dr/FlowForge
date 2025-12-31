# Implement: Linear-Style Unified Toolbar (Remove Redundant Title)

## Workflow Context

You're in a Forge-managed worktree for this feature.
- **Feature ID:** `the-title-at-the-top-is-redundant-i-see-two-tites-`
- **Branch:** Isolated from main (changes won't affect main until shipped)
- **To ship:** When human says "ship it", run `forge merge the-title-at-the-top-is-redundant-i-see-two-tites-`
- **Your focus:** Implement the feature. Human decides when to ship.

## Feature
Replaces the current double-title setup (window title bar + in-content title) with a single unified toolbar at the top of the Kanban board, matching Linear's clean, immersive aesthetic. The window becomes borderless with content extending to the edges.

How it works:
- Remove the standard macOS window title bar (use `.windowStyle(.hiddenTitleBar)` or similar)
- Create a custom toolbar row at the top of ContentView/KanbanView
- Left side: Project name/switcher
- Right side: Shipping streak badge, quick add button, search (⌘K trigger)
- Toolbar should be slim (~44pt height) with subtle bottom border or shadow
- Window remains draggable from the toolbar area
- Traffic lights (close/minimize/zoom) integrated into the toolbar, not floating

Complexity: Medium

## Research

If this feature involves novel patterns, complex architecture, or unfamiliar APIs:
- **Ask the human** to run deep research threads if you need authoritative context
- For clinical/medical evidence, specifically ask them to check OpenEvidence
- Cite official documentation where applicable

## Instructions

You're helping a vibecoder who isn't a Git expert.
Handle all Git operations safely without requiring them to understand Git.

**Engage plan mode and ultrathink before implementing.**
Present your plan for approval before writing code.

When implementing:
- Commit changes with conventional commit format
- Follow existing patterns in the codebase
- Test on target device/environment

When human says "ship it":
- Run `forge merge the-title-at-the-top-is-redundant-i-see-two-tites-` to merge to main and clean up
- This handles: merge → build validation → worktree cleanup → done

Ask clarifying questions if the specification is unclear.
