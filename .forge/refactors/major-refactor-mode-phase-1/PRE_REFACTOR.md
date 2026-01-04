# Pre-Refactor Codebase Analysis

> **Goal**: 
> **Generated**: 2026-01-03
>
> ## ⚠️ FOR CLAUDE CODE AGENTS
>
> This is a **SNAPSHOT document**.
> - Line numbers may shift after code changes
> - Use for **architectural understanding**, not exact references
> - For execution workflow: See EXECUTION.md

---

## Executive Summary

The Forge refactor module implements a Major Refactor Mode designed for multi-session, AI-assisted code refactoring. It follows a 'docs ARE the memory' philosophy where each Claude session starts fresh by reading documentation files rather than relying on accumulated conversation context. The system is structured around four key components: PlanningAgent (creates refactor structure and launches collaborative planning sessions), RefactorState (tracks execution progress across sessions via state.json), Signals (file-based agent communication via JSON files in a signals/ directory), and ExecutionSession (manages individual session lifecycles).

The architecture is designed for 'vibecoders' - developers who work extensively with AI but may not be Git experts. Each refactor creates a self-contained directory under .forge/refactors/{id}/ containing planning docs (PHILOSOPHY.md, VISION.md, DECISIONS.md, PRE_REFACTOR.md, EXECUTION_PLAN.md), execution state (state.json, metadata.json), and signal files for inter-agent communication. Sessions are identified hierarchically (e.g., '1.1' for Phase 1, Session 1) and each gets its own subdirectory with a tailored CLAUDE.md.

The most important aspects to understand before making changes: (1) State persistence is via JSON files that must remain backward-compatible, (2) Signals use atomic file writes with timestamp-based ordering, (3) Terminal launching uses macOS-specific AppleScript via osascript, (4) The CLAUDE.md generation is critical as it's the 'memory' that guides Claude in each fresh session, and (5) Session specs are parsed from markdown using regex which is fragile if the format changes.

---

## Current Architecture

**Core Components:**
- **PlanningAgent** (planning_agent.py): Creates refactor directories, generates planning CLAUDE.md, launches terminal with Claude
- **RefactorState** (state.py): Persists overall refactor status and all session states to state.json
- **SessionState** (state.py): Tracks individual session lifecycle (PENDING→IN_PROGRESS→COMPLETED/NEEDS_REVISION)
- **Signal System** (signals.py): File-based async communication via timestamped JSON files
- **ExecutionSession** (session.py): Manages session spec loading, CLAUDE.md generation, terminal launching
- **CodebaseAnalyzer** (analyzer.py): Generates goal-focused PRE_REFACTOR.md via Claude CLI calls
- **Terminal Module** (terminal.py): macOS-specific terminal automation (Warp/iTerm/Terminal.app)

**Data Flow:**
1. CLI command → PlanningAgent.launch() → Creates refactor directory + docs + launches terminal
2. Claude creates planning docs (PHILOSOPHY, VISION, DECISIONS, EXECUTION_PLAN)
3. forge refactor start → ExecutionSession.launch() → Updates state → Writes signal → Launches session terminal
4. Claude executes session → Commits → complete_session() → Updates state + signal
5. Orchestrator (future) reads signals + state to determine next session

**State Hierarchy:**
- RefactorStatus: PLANNING → EXECUTING ↔ PAUSED → COMPLETED
- SessionStatus: PENDING → IN_PROGRESS → COMPLETED/NEEDS_REVISION
- AuditResult: PENDING → PASSED/FAILED

---

## Key Files

| File | Purpose | Key Lines |
|------|---------|-----------|
| `forge/refactor/state.py` | State management with RefactorState and SessionState dataclasses for JSON persistence | RefactorState class (lines 45-130), save/load methods, start_session/complete_session logic |
| `forge/refactor/signals.py` | File-based signal system for agent communication via timestamped JSON files | write_signal() with atomic temp+rename, SignalType enum, convenience signal_* functions |
| `forge/refactor/session.py` | ExecutionSession orchestration and SessionSpec markdown parsing | SessionSpec.from_markdown() regex parsing, ExecutionSession.launch() lifecycle, generate_execution_claude_md() |
| `forge/refactor/planning_agent.py` | Creates refactor directories and launches planning Claude sessions | create_refactor() directory setup, generate_planning_claude_md(), launch() main entry point |
| `forge/refactor/analyzer.py` | Generates PRE_REFACTOR.md by analyzing codebase via Claude CLI | CodebaseAnalyzer._call_claude() for AI analysis, AnalysisResult.to_markdown() output formatting |
| `forge/refactor/prompts.py` | PLANNING_PROMPT template that guides Claude through planning process | Full PLANNING_PROMPT with instructions for exploring, questioning, debating, documenting |
| `forge/cli.py` | Typer CLI with refactor subcommands (plan, list, status, resume, start) | refactor_plan, refactor_start, refactor_list commands (search for '@refactor_app.command') |
| `forge/terminal.py` | macOS terminal automation for Warp/iTerm/Terminal.app via AppleScript | open_terminal_in_directory(), detect_terminal(), _open_warp/_open_iterm/_open_terminal_app functions |
| `.forge/refactors/major-refactor-mode-phase-1/state.json` | Active refactor state showing current session 2.2 in progress | Shows sessions 2.1 and 2.2 both in_progress, refactor in executing state |

---

## Patterns in Use

- Dataclass-based models with to_dict/from_dict for JSON serialization
- File-based state persistence (state.json, metadata.json) - no database
- File-based signal system for async agent communication (atomic writes via temp+rename)
- Typer CLI with subcommand groups (main app + refactor_app)
- Rich console for formatted output (tables, panels, markdown)
- macOS AppleScript automation via osascript for terminal control
- Regex-based markdown parsing for session specs (fragile pattern)
- CLAUDE.md convention - Claude reads this file automatically per directory
- Hierarchical session IDs (phase.session format like '1.1', '2.2')
- Enum-based status tracking (RefactorStatus, SessionStatus, AuditResult)
- Timestamp-ordered signal files ({YYYYMMDD_HHMMSS_microseconds}_{type}.json)

---

## Known Gaps / Issues

- No automated orchestrator - sessions must be manually started with 'forge refactor start'
- No audit agent implementation - AuditResult exists but no code uses it
- Regex parsing of EXECUTION_PLAN.md is fragile - format changes break parsing
- State.json can have multiple sessions 'in_progress' (inconsistent with stated 'one at a time' design)
- No cleanup/archive mechanism for completed refactors
- Terminal automation only works on macOS - no Linux/Windows support
- No signal polling/watching mechanism - manual checks required
- CLAUDE.md generation embeds static prompts - no dynamic context injection
- analyzer.py calls Claude CLI but has no fallback if Claude unavailable
- Session completion requires manual call to complete_session() - no auto-detection

---

## Summary

This analysis provides context for the refactor goal. Execution sessions should:
1. Read this document to understand the current state
2. Reference PHILOSOPHY.md for guiding principles
3. Check DECISIONS.md for approved architecture
