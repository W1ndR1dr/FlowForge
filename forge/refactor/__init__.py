"""
Forge Refactor Module - Major Refactor Mode for multi-session refactors.

Components:
    - PlanningAgent: Interactive planning conversation that generates refactor docs
    - RefactorState: State management for refactors
    - SessionState: State for individual execution sessions
    - Signals: File-based agent communication

Philosophy: "Docs ARE the memory" - agents read from files, no accumulated context.
See docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md for guiding principles.
"""

from .planning_agent import PlanningAgent
from .state import (
    RefactorState,
    RefactorStatus,
    SessionState,
    SessionStatus,
    AuditResult,
    StateChange,
)
from .signals import (
    Signal,
    SignalType,
    write_signal,
    read_signals,
    read_latest_signal,
    clear_signals,
    get_signals_dir,
    signal_session_started,
    signal_session_done,
    signal_audit_passed,
    signal_revision_needed,
    signal_question,
)
from .session import (
    ExecutionSession,
    SessionSpec,
    complete_session,
)
from .analyzer import (
    CodebaseAnalyzer,
    AnalysisResult,
    analyze_codebase,
)
from .orchestrator import (
    OrchestratorSession,
    SignalSummary,
    SignalEvent,
)

__all__ = [
    # Planning
    "PlanningAgent",
    # State
    "RefactorState",
    "RefactorStatus",
    "SessionState",
    "SessionStatus",
    "AuditResult",
    "StateChange",
    # Signals
    "Signal",
    "SignalType",
    "write_signal",
    "read_signals",
    "read_latest_signal",
    "clear_signals",
    "get_signals_dir",
    "signal_session_started",
    "signal_session_done",
    "signal_audit_passed",
    "signal_revision_needed",
    "signal_question",
    # Execution Sessions
    "ExecutionSession",
    "SessionSpec",
    "complete_session",
    # Analyzer
    "CodebaseAnalyzer",
    "AnalysisResult",
    "analyze_codebase",
    # Orchestrator
    "OrchestratorSession",
    "SignalSummary",
    "SignalEvent",
]
