"""
Refactor execution state management.

Tracks the runtime state of a multi-session refactor execution.
State persists to .forge/refactors/{id}/state.json.
"""

from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import json


class RefactorStatus(str, Enum):
    """Status of an overall refactor."""

    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"


class SessionStatus(str, Enum):
    """Status of a single execution session."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


class AuditResult(str, Enum):
    """Result of an audit review."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class SessionState:
    """
    State for a single execution session.

    Each session (e.g., "1.1", "2.1") has its own state tracking
    progress through the execution lifecycle.
    """

    session_id: str  # e.g., "1.1", "2.1"
    status: SessionStatus = SessionStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    commit_hash: Optional[str] = None
    audit_result: AuditResult = AuditResult.PENDING
    notes: str = ""  # Handoff notes for next session
    iteration_count: int = 0  # Tracks audit iterations for visibility

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "commit_hash": self.commit_hash,
            "audit_result": self.audit_result.value,
            "notes": self.notes,
            "iteration_count": self.iteration_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        """Create SessionState from dictionary."""
        return cls(
            session_id=data["session_id"],
            status=SessionStatus(data.get("status", "pending")),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            commit_hash=data.get("commit_hash"),
            audit_result=AuditResult(data.get("audit_result", "pending")),
            notes=data.get("notes", ""),
            iteration_count=data.get("iteration_count", 0),
        )


@dataclass
class StateChange:
    """A single state change entry for the audit log."""

    timestamp: str
    action: str  # e.g., "session_started", "session_completed", "status_changed"
    details: dict  # Action-specific details

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StateChange":
        return cls(
            timestamp=data["timestamp"],
            action=data["action"],
            details=data.get("details", {}),
        )


@dataclass
class RefactorState:
    """
    Runtime state for a refactor execution.

    This is the central state tracker for a multi-session refactor.
    It knows which sessions exist, which is current, and the overall status.

    Stored at: .forge/refactors/{id}/state.json
    """

    refactor_id: str
    status: RefactorStatus = RefactorStatus.PLANNING
    current_session: Optional[str] = None  # e.g., "1.1"
    sessions: dict[str, SessionState] = field(default_factory=dict)
    started_at: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    history: list[StateChange] = field(default_factory=list)  # Audit log of changes

    def _log_change(self, action: str, **details) -> None:
        """Append a change to the history log."""
        self.history.append(StateChange(
            timestamp=datetime.now().isoformat(),
            action=action,
            details=details,
        ))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "refactor_id": self.refactor_id,
            "status": self.status.value,
            "current_session": self.current_session,
            "sessions": {
                sid: sess.to_dict() for sid, sess in self.sessions.items()
            },
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "history": [h.to_dict() for h in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RefactorState":
        """Create RefactorState from dictionary."""
        sessions = {}
        for sid, sdata in data.get("sessions", {}).items():
            sessions[sid] = SessionState.from_dict(sdata)

        history = []
        for hdata in data.get("history", []):
            history.append(StateChange.from_dict(hdata))

        return cls(
            refactor_id=data["refactor_id"],
            status=RefactorStatus(data.get("status", "planning")),
            current_session=data.get("current_session"),
            sessions=sessions,
            started_at=data.get("started_at"),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
            history=history,
        )

    def save(self, path: Path) -> None:
        """Save state to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now().isoformat()
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "RefactorState":
        """Load state from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    # Session management helpers

    def add_session(self, session_id: str) -> SessionState:
        """Add a new session to track."""
        if session_id in self.sessions:
            raise ValueError(f"Session already exists: {session_id}")
        session = SessionState(session_id=session_id)
        self.sessions[session_id] = session
        self._log_change("session_added", session_id=session_id)
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def start_session(self, session_id: str) -> SessionState:
        """Mark a session as started."""
        if session_id not in self.sessions:
            self.add_session(session_id)

        session = self.sessions[session_id]
        old_status = session.status
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.now().isoformat()
        self.current_session = session_id
        self.status = RefactorStatus.EXECUTING
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()
        self._log_change(
            "session_started",
            session_id=session_id,
            old_status=old_status.value,
            new_status=session.status.value,
        )
        return session

    def complete_session(
        self,
        session_id: str,
        commit_hash: Optional[str] = None,
        notes: str = "",
    ) -> SessionState:
        """Mark a session as completed."""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self.sessions[session_id]
        old_status = session.status
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now().isoformat()
        if commit_hash:
            session.commit_hash = commit_hash
        if notes:
            session.notes = notes
        self._log_change(
            "session_completed",
            session_id=session_id,
            old_status=old_status.value,
            commit_hash=commit_hash,
        )
        return session

    def mark_needs_revision(
        self,
        session_id: str,
        notes: str = "",
    ) -> SessionState:
        """Mark a session as needing revision after failed audit."""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self.sessions[session_id]
        old_status = session.status
        session.status = SessionStatus.NEEDS_REVISION
        session.audit_result = AuditResult.FAILED
        if notes:
            session.notes = notes
        self._log_change(
            "session_needs_revision",
            session_id=session_id,
            old_status=old_status.value,
            notes=notes,
        )
        return session

    def get_pending_sessions(self) -> list[SessionState]:
        """Get all sessions that haven't started."""
        return [
            s for s in self.sessions.values()
            if s.status == SessionStatus.PENDING
        ]

    def get_completed_sessions(self) -> list[SessionState]:
        """Get all completed sessions."""
        return [
            s for s in self.sessions.values()
            if s.status == SessionStatus.COMPLETED
        ]

    def is_complete(self) -> bool:
        """Check if all sessions are completed."""
        if not self.sessions:
            return False
        return all(
            s.status == SessionStatus.COMPLETED
            for s in self.sessions.values()
        )

    def increment_iteration(self, session_id: str) -> int:
        """
        Increment and return iteration count for a session.

        Called when audit fails and session needs revision.
        The auditor uses this count to decide when to escalate.
        """
        session = self.sessions.get(session_id)
        if session:
            session.iteration_count += 1
            self._log_change(
                "iteration_incremented",
                session_id=session_id,
                count=session.iteration_count,
            )
            return session.iteration_count
        return 0
