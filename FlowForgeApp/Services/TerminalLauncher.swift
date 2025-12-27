import Foundation
#if os(macOS)
import AppKit
#endif

/// Launches Claude Code in Warp terminal at a specific worktree path.
/// This is the bridge between FlowForge orchestration and actual coding.
/// macOS only - iOS doesn't have terminal access.
enum TerminalLauncher {

    /// Result of a terminal launch attempt
    struct LaunchResult {
        let success: Bool
        let message: String
    }

    #if os(macOS)
    /// Launch Claude Code in Warp at the given worktree path
    /// - Parameters:
    ///   - worktreePath: Absolute path to the worktree directory
    ///   - prompt: Optional prompt to copy to clipboard and pipe into Claude
    ///   - launchCommand: Full command from server config (e.g., "claude --dangerously-skip-permissions")
    /// - Returns: LaunchResult indicating success/failure
    @MainActor
    static func launchClaudeCode(
        worktreePath: String,
        prompt: String? = nil,
        launchCommand: String? = nil
    ) async -> LaunchResult {
        // Build the claude command
        let claudeCommand = launchCommand ?? "claude --dangerously-skip-permissions"

        let fullCommand: String
        if let prompt = prompt, !prompt.isEmpty {
            // Copy prompt to clipboard, then pipe it into Claude
            // This automates the "paste prompt" step
            copyToClipboard(prompt)
            fullCommand = "cd '\(worktreePath)' && pbpaste | \(claudeCommand)"
        } else {
            // No prompt - just launch (resume case)
            fullCommand = "cd '\(worktreePath)' && \(claudeCommand)"
        }

        // Try Warp's URL scheme first (no permissions needed)
        if let warpURL = URL(string: "warp://action/new_tab?command=\(fullCommand.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") {
            if NSWorkspace.shared.open(warpURL) {
                let message = prompt != nil
                    ? "Claude Code started in Warp with prompt"
                    : "Claude Code opened in Warp"
                return LaunchResult(success: true, message: message)
            }
        }

        // Fallback: AppleScript (requires Accessibility permissions)
        let script = """
        tell application "Warp"
            activate
            delay 0.3
        end tell

        tell application "System Events"
            tell process "Warp"
                keystroke "t" using command down
                delay 0.5
                keystroke "\(fullCommand.escapedForAppleScript)"
                keystroke return
            end tell
        end tell
        """

        let result = await runAppleScript(script)

        if result.success {
            let message = prompt != nil
                ? "Claude Code started in Warp with prompt"
                : "Claude Code opened in Warp"
            return LaunchResult(success: true, message: message)
        } else {
            // Fallback: Try opening Terminal.app if Warp isn't available
            let fallbackResult = await launchInDefaultTerminal(worktreePath: worktreePath)
            return fallbackResult
        }
    }

    /// Fallback to default Terminal.app
    private static func launchInDefaultTerminal(worktreePath: String) async -> LaunchResult {
        let script = """
        tell application "Terminal"
            activate
            do script "cd '\(worktreePath.escapedForAppleScript)' && claude"
        end tell
        """

        let result = await runAppleScript(script)

        if result.success {
            return LaunchResult(
                success: true,
                message: "Claude Code opened in Terminal. Prompt copied to clipboard."
            )
        } else {
            return LaunchResult(
                success: false,
                message: "Failed to open terminal: \(result.error ?? "Unknown error")"
            )
        }
    }

    /// Copy text to system clipboard
    private static func copyToClipboard(_ text: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
    }

    /// Run AppleScript and return result
    private static func runAppleScript(_ script: String) async -> (success: Bool, error: String?) {
        await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                var error: NSDictionary?
                let appleScript = NSAppleScript(source: script)
                let _ = appleScript?.executeAndReturnError(&error)

                if let error = error {
                    let errorMessage = error[NSAppleScript.errorMessage] as? String ?? "Unknown error"
                    continuation.resume(returning: (false, errorMessage))
                } else {
                    continuation.resume(returning: (true, nil))
                }
            }
        }
    }
    #endif
}

// MARK: - String Extension for AppleScript escaping

private extension String {
    /// Escape string for safe use in AppleScript
    var escapedForAppleScript: String {
        self.replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "'", with: "'\\''")
    }
}
