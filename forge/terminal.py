"""
Terminal integration for Forge.

Supports opening new terminal tabs/windows in worktree directories
with Claude Code ready to go. Zero git knowledge required.

Supported terminals:
- Warp (recommended for vibecoders)
- iTerm2
- Terminal.app (macOS default)
"""

import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum


# Terminal launching only works on macOS (uses osascript)
IS_MACOS = platform.system() == "Darwin"


def check_accessibility_permissions() -> Tuple[bool, str]:
    """
    Check if we have macOS Accessibility permissions for sending keystrokes.

    Returns (has_permission, message).
    """
    if not IS_MACOS:
        return True, "Not macOS - no permissions needed"

    # Try a harmless keystroke test
    test_script = '''
    tell application "System Events"
        -- Just check if we can access System Events, don't actually send keys
        return name of first process
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', test_script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, (
            "System Events access denied.\n"
            "Fix: System Preferences → Privacy & Security → Accessibility\n"
            "     Add your terminal app (Warp, Terminal, etc.)"
        )

    # Now test actual keystroke permission with a no-op
    keystroke_test = '''
    tell application "System Events"
        -- This will fail if keystrokes aren't allowed
        key code 0 using {}
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', keystroke_test],
        capture_output=True,
        text=True
    )

    if "not allowed to send keystrokes" in result.stderr:
        return False, (
            "Keystroke permissions denied.\n"
            "Fix: System Preferences → Privacy & Security → Accessibility\n"
            "     Add your terminal app (Warp, Terminal, etc.)\n\n"
            "To open settings: open \"x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility\""
        )

    return True, "Accessibility permissions OK"


def ensure_accessibility_permissions() -> bool:
    """
    Check permissions and print helpful message if missing.
    Returns True if permissions are OK.
    """
    has_perms, message = check_accessibility_permissions()

    if not has_perms:
        print(f"\n⚠️  {message}\n")
        return False

    return True


class Terminal(str, Enum):
    """Supported terminal applications."""
    WARP = "warp"
    ITERM = "iterm"
    TERMINAL = "terminal"
    AUTO = "auto"  # Auto-detect


def detect_terminal() -> Terminal:
    """Auto-detect the best available terminal."""
    # Check for Warp first (preferred for vibecoders)
    if Path("/Applications/Warp.app").exists():
        return Terminal.WARP
    elif Path("/Applications/iTerm.app").exists():
        return Terminal.ITERM
    else:
        return Terminal.TERMINAL


def open_terminal_in_directory(
    directory: Path,
    terminal: Terminal = Terminal.AUTO,
    command: Optional[str] = None,
    title: Optional[str] = None,
    initial_input: Optional[str] = None,
) -> bool:
    """
    Open a new terminal tab/window in the specified directory.

    Args:
        directory: Path to open the terminal in
        terminal: Which terminal to use (auto-detects if AUTO)
        command: Optional command to run after opening
        title: Optional title for the tab/window
        initial_input: Optional input to type after command starts (e.g., "start" for Claude)

    Returns:
        True if successful, False otherwise
    """
    if not IS_MACOS:
        # Terminal launching requires macOS osascript
        return False

    # Check permissions before attempting
    if not ensure_accessibility_permissions():
        return False

    if terminal == Terminal.AUTO:
        terminal = detect_terminal()

    try:
        if terminal == Terminal.WARP:
            return _open_warp(directory, command, title, initial_input)
        elif terminal == Terminal.ITERM:
            return _open_iterm(directory, command, title, initial_input)
        else:
            return _open_terminal_app(directory, command, title, initial_input)
    except Exception as e:
        print(f"Failed to open terminal: {e}")
        return False


def _open_warp(
    directory: Path,
    command: Optional[str] = None,
    title: Optional[str] = None,
    initial_input: Optional[str] = None,
) -> bool:
    """Open Warp in a new tab at the specified directory."""

    # Build the AppleScript for Warp
    # Warp supports opening new tabs via the warp:// URL scheme or AppleScript
    script_parts = [
        'tell application "Warp"',
        '    activate',
    ]

    # Escape the directory path for use inside AppleScript strings
    # AppleScript uses \" to escape quotes inside strings
    # In Python, we need \\\" to get a literal \" in the output
    dir_str = str(directory)

    # Create a new window (Cmd+N) and cd to directory
    if command:
        # Build the shell command with proper quoting for AppleScript
        full_command = 'cd \\"' + dir_str + '\\" && ' + command
        script_parts.append('    tell application "System Events" to keystroke "n" using command down')
        script_parts.append('    delay 0.5')
        script_parts.append('    tell application "System Events" to keystroke "' + full_command + '"')
        script_parts.append('    tell application "System Events" to keystroke return')
    else:
        # Just open in the directory
        cd_command = 'cd \\"' + dir_str + '\\"'
        script_parts.append('    tell application "System Events" to keystroke "n" using command down')
        script_parts.append('    delay 0.5')
        script_parts.append('    tell application "System Events" to keystroke "' + cd_command + '"')
        script_parts.append('    tell application "System Events" to keystroke return')

    # If initial_input is provided, wait for command to start then type it
    if initial_input:
        # Wait for Claude to fully start up
        script_parts.append('    delay 3.0')
        script_parts.append('    tell application "System Events" to keystroke "' + initial_input + '"')
        # Use key code 36 (Return) - more reliable than keystroke return
        script_parts.append('    delay 0.2')
        script_parts.append('    tell application "System Events" to key code 36')

    script_parts.append('end tell')

    script = '\n'.join(script_parts)

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 and result.stderr:
        print(f"AppleScript error: {result.stderr}")

    return result.returncode == 0


def _open_iterm(
    directory: Path,
    command: Optional[str] = None,
    title: Optional[str] = None,
    initial_input: Optional[str] = None,
) -> bool:
    """Open iTerm2 in a new tab at the specified directory."""

    cd_command = f'cd "{directory}"'
    if command:
        cd_command += f' && {command}'

    # Build script with optional initial input
    if initial_input:
        script = f'''
    tell application "iTerm"
        activate
        tell current window
            create tab with default profile
            tell current session
                write text "{cd_command}"
                delay 2.0
                write text "{initial_input}"
            end tell
        end tell
    end tell
    '''
    else:
        script = f'''
    tell application "iTerm"
        activate
        tell current window
            create tab with default profile
            tell current session
                write text "{cd_command}"
            end tell
        end tell
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def _open_terminal_app(
    directory: Path,
    command: Optional[str] = None,
    title: Optional[str] = None,
    initial_input: Optional[str] = None,
) -> bool:
    """Open Terminal.app in a new tab at the specified directory."""

    cd_command = f'cd "{directory}"'
    if command:
        cd_command += f' && {command}'

    # Terminal.app doesn't support easy delayed input, so we append it if provided
    if initial_input:
        # For Terminal.app, we can chain the input after a sleep
        cd_command += f' && sleep 2 && echo "{initial_input}"'

    script = f'''
    tell application "Terminal"
        activate
        do script "{cd_command}"
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def launch_claude_code(
    worktree_path: Path,
    prompt_path: Optional[Path] = None,
    claude_command: str = "claude",
    claude_flags: list[str] = None,
    terminal: Terminal = Terminal.AUTO,
    auto_start: bool = True,
) -> bool:
    """
    Launch Claude Code in a new terminal tab at the worktree directory.

    This is the main function vibecoders should use - it handles everything:
    1. Opens new terminal tab in the worktree
    2. Runs Claude Code with appropriate flags
    3. You just paste the prompt from clipboard

    Args:
        worktree_path: Path to the feature worktree
        prompt_path: Optional path to the saved prompt file
        claude_command: Claude CLI command (default: "claude")
        claude_flags: Extra flags for Claude (default: ["--dangerously-skip-permissions"])
        terminal: Which terminal to use (default: auto-detect)
        auto_start: If True, start Claude Code automatically

    Returns:
        True if successful
    """
    if claude_flags is None:
        claude_flags = ["--dangerously-skip-permissions"]

    if auto_start:
        # Build the full claude command
        flags_str = " ".join(claude_flags)
        command = f"{claude_command} {flags_str}"

        return open_terminal_in_directory(
            worktree_path,
            terminal=terminal,
            command=command,
            title=f"Forge: {worktree_path.name}",
        )
    else:
        # Just open in the directory
        return open_terminal_in_directory(
            worktree_path,
            terminal=terminal,
            title=f"Forge: {worktree_path.name}",
        )


# Convenience function for the CLI
def start_feature_in_terminal(
    worktree_path: Path,
    feature_title: str,
    claude_command: str = "claude",
    claude_flags: list[str] = None,
    terminal: str = "auto",
) -> tuple[bool, str]:
    """
    Start working on a feature in a new terminal tab.

    Returns (success, message) for the CLI to display.
    """
    terminal_enum = Terminal(terminal) if terminal != "auto" else Terminal.AUTO

    success = launch_claude_code(
        worktree_path=worktree_path,
        claude_command=claude_command,
        claude_flags=claude_flags,
        terminal=terminal_enum,
        auto_start=True,
    )

    if success:
        detected = detect_terminal() if terminal_enum == Terminal.AUTO else terminal_enum
        return True, f"Opened {detected.value.title()} with Claude Code in {worktree_path.name}"
    else:
        return False, "Failed to open terminal. You can manually run:\n" \
                     f"  cd {worktree_path}\n" \
                     f"  {claude_command} {' '.join(claude_flags or [])}"
