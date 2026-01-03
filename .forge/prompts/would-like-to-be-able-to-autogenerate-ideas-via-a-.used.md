# Implement: AI Idea Generator Button

## Workflow Context

You're in a Forge-managed worktree for this feature.
- **Feature ID:** `would-like-to-be-able-to-autogenerate-ideas-via-a-`
- **Worktree:** `/Users/Brian/Projects/Active/Forge/.forge-worktrees/would-like-to-be-able-to-autogenerate-ideas-via-a-`
- **Branch:** Isolated from main (changes won't affect main until shipped)
- **To ship:** When human says "ship it", run `forge merge would-like-to-be-able-to-autogenerate-ideas-via-a-`
- **Your focus:** Implement the feature. Human decides when to ship.

## Feature
A button in the UI that uses AI to generate relevant feature ideas for the current project. When clicked, it analyzes the project's existing features and context to suggest complementary new features that would make sense to build next.

How it works:
- Button appears in the feature list/sidebar area (near "Add Feature" or in the toolbar)
- On click, sends existing feature titles and project context to AI
- AI generates 3-5 contextually relevant feature ideas
- Ideas appear in a popover or modal for the user to review
- User can dismiss ideas, or click one to add it directly to the Idea Inbox for refinement
- If no project context exists, generates reasonable ideas for a dev tool/productivity app

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
- Run `forge merge would-like-to-be-able-to-autogenerate-ideas-via-a-` to merge to main and clean up
- This handles: merge → build validation → worktree cleanup → done

Ask clarifying questions if the specification is unclear.
