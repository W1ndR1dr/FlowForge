"""
Forge Refactor Module - Major Refactor Mode for multi-session refactors.

Components:
    - PlanningAgent: Interactive planning conversation that generates refactor docs
    - RefactorState: State management for refactors (coming in Phase 1)
    - Signals: File-based agent communication (coming in Phase 1)

Philosophy: "Docs ARE the memory" - agents read from files, no accumulated context.
See docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md for guiding principles.
"""

from .planning_agent import PlanningAgent

__all__ = ["PlanningAgent"]
