"""
File-based signal system for agent communication.

Agents communicate via JSON signal files in .forge/refactors/{id}/signals/.
This is simpler and more robust than IPC - signals survive crashes and are
human-inspectable.

Signal file format:
{
    "type": "SESSION_DONE",
    "session_id": "1.1",
    "timestamp": "2026-01-03T14:30:00",
    "payload": {...}
}
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import json
import os
import tempfile
import shutil


class SignalType(str, Enum):
    """Types of signals agents can send."""

    # Session lifecycle
    SESSION_STARTED = "session_started"  # Agent began work on a session
    SESSION_DONE = "session_done"  # Agent finished work (includes commit_hash, summary)

    # Audit results
    AUDIT_PASSED = "audit_passed"  # Audit agent approved the session
    REVISION_NEEDED = "revision_needed"  # Audit found issues (includes issues list)

    # User interaction
    QUESTION = "question"  # Agent needs user input (includes question, options)

    # Control
    PAUSED = "paused"  # User paused the refactor
    RESUMED = "resumed"  # User resumed the refactor


@dataclass
class Signal:
    """A signal message between agents."""

    type: SignalType
    session_id: str
    timestamp: str
    payload: dict

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Signal":
        """Create Signal from dictionary."""
        return cls(
            type=SignalType(data["type"]),
            session_id=data["session_id"],
            timestamp=data["timestamp"],
            payload=data.get("payload", {}),
        )


def write_signal(
    signals_dir: Path,
    signal_type: SignalType,
    session_id: str,
    payload: Optional[dict] = None,
) -> Path:
    """
    Write a signal file atomically.

    Uses write-to-temp-then-rename pattern for atomic writes.
    Filename format: {timestamp}_{signal_type}.json

    Args:
        signals_dir: Directory to write signal to
        signal_type: Type of signal
        session_id: Session this signal relates to
        payload: Additional data for the signal

    Returns:
        Path to the written signal file
    """
    signals_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()
    timestamp_str = timestamp.isoformat()

    # Create filename with microsecond precision for ordering
    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}_{signal_type.value}.json"

    signal = Signal(
        type=signal_type,
        session_id=session_id,
        timestamp=timestamp_str,
        payload=payload or {},
    )

    signal_path = signals_dir / filename

    # Atomic write: write to temp file, then rename
    fd, temp_path = tempfile.mkstemp(
        suffix=".json",
        prefix="signal_",
        dir=signals_dir,
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(signal.to_dict(), f, indent=2)
        os.rename(temp_path, signal_path)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    return signal_path


def read_signals(signals_dir: Path) -> list[Signal]:
    """
    Read all signals from a directory, sorted by timestamp.

    Args:
        signals_dir: Directory containing signal files

    Returns:
        List of Signal objects, oldest first
    """
    if not signals_dir.exists():
        return []

    signals = []
    for path in signals_dir.glob("*.json"):
        # Skip archive directory
        if path.is_dir():
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            signals.append(Signal.from_dict(data))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Skip malformed signals
            continue

    # Sort by timestamp (filename prefix makes this chronological)
    return sorted(signals, key=lambda s: s.timestamp)


def read_latest_signal(signals_dir: Path, signal_type: Optional[SignalType] = None) -> Optional[Signal]:
    """
    Read the most recent signal, optionally filtered by type.

    Args:
        signals_dir: Directory containing signal files
        signal_type: Optional filter for signal type

    Returns:
        Most recent Signal, or None if no signals found
    """
    signals = read_signals(signals_dir)
    if signal_type:
        signals = [s for s in signals if s.type == signal_type]
    return signals[-1] if signals else None


def clear_signals(signals_dir: Path) -> None:
    """
    Archive old signals to signals/archive/.

    Moves all current signals to an archive subdirectory with timestamp.
    This preserves history while clearing the active signals directory.

    Args:
        signals_dir: Directory containing signal files
    """
    if not signals_dir.exists():
        return

    archive_dir = signals_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Create archive folder with timestamp
    archive_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_folder = archive_dir / archive_name
    archive_folder.mkdir(exist_ok=True)

    # Move all signal files to archive
    for path in signals_dir.glob("*.json"):
        if path.is_file():
            shutil.move(str(path), archive_folder / path.name)


def get_signals_dir(refactor_dir: Path) -> Path:
    """Get the signals directory for a refactor."""
    return refactor_dir / "signals"


# Convenience functions for common signals

def signal_session_started(
    signals_dir: Path,
    session_id: str,
    worktree_path: Optional[str] = None,
) -> Path:
    """Write a SESSION_STARTED signal."""
    return write_signal(
        signals_dir,
        SignalType.SESSION_STARTED,
        session_id,
        {"worktree_path": worktree_path} if worktree_path else {},
    )


def signal_session_done(
    signals_dir: Path,
    session_id: str,
    commit_hash: Optional[str] = None,
    summary: str = "",
) -> Path:
    """Write a SESSION_DONE signal."""
    return write_signal(
        signals_dir,
        SignalType.SESSION_DONE,
        session_id,
        {
            "commit_hash": commit_hash,
            "summary": summary,
        },
    )


def signal_audit_passed(
    signals_dir: Path,
    session_id: str,
    notes: str = "",
) -> Path:
    """Write an AUDIT_PASSED signal."""
    return write_signal(
        signals_dir,
        SignalType.AUDIT_PASSED,
        session_id,
        {"notes": notes},
    )


def signal_revision_needed(
    signals_dir: Path,
    session_id: str,
    issues: list[str],
    suggestions: list[str] = None,
) -> Path:
    """Write a REVISION_NEEDED signal."""
    return write_signal(
        signals_dir,
        SignalType.REVISION_NEEDED,
        session_id,
        {
            "issues": issues,
            "suggestions": suggestions or [],
        },
    )


def signal_question(
    signals_dir: Path,
    session_id: str,
    question: str,
    options: list[str] = None,
) -> Path:
    """Write a QUESTION signal (agent needs user input)."""
    return write_signal(
        signals_dir,
        SignalType.QUESTION,
        session_id,
        {
            "question": question,
            "options": options or [],
        },
    )
