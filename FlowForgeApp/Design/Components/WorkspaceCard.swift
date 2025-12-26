import SwiftUI
#if os(macOS)
import AppKit
#endif

// MARK: - Workspace Card
// Shows an active workspace (feature being worked on)
// For vibecoders: "Each workspace is isolated — changes can't interfere!"

struct WorkspaceCard: View {
    let feature: Feature
    let onResume: () -> Void
    let onStop: () -> Void

    @State private var isHovered = false
    @State private var isLaunching = false

    /// Status indicator color
    private var statusColor: Color {
        switch feature.status {
        case .inProgress:
            return StatusColor.inProgressFallback
        case .review:
            return StatusColor.reviewFallback
        default:
            return .secondary
        }
    }

    /// Friendly status message
    private var statusMessage: String {
        switch feature.status {
        case .inProgress:
            if let path = feature.worktreePath {
                let folder = URL(fileURLWithPath: path).lastPathComponent
                return "Worktree: \(folder)"
            }
            return "In worktree"
        case .review:
            return "Ready for review"
        default:
            return feature.status.displayName
        }
    }

    /// Time since started
    private var timeWorking: String {
        guard let started = feature.startedAt else { return "" }
        let elapsed = Date().timeIntervalSince(started)

        if elapsed < 60 {
            return "Just started"
        } else if elapsed < 3600 {
            let minutes = Int(elapsed / 60)
            return "\(minutes)m"
        } else {
            let hours = Int(elapsed / 3600)
            return "\(hours)h"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.small) {
            // Header with status
            HStack {
                // Pulsing status indicator
                Circle()
                    .fill(statusColor)
                    .frame(width: 8, height: 8)
                    .pulse(isActive: feature.status == .inProgress)

                Text(feature.title)
                    .font(Typography.body)
                    .fontWeight(.medium)
                    .lineLimit(1)

                Spacer()

                if !timeWorking.isEmpty {
                    Text(timeWorking)
                        .font(Typography.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Status message and worktree path
            VStack(alignment: .leading, spacing: Spacing.micro) {
                Text(statusMessage)
                    .font(Typography.caption)
                    .foregroundColor(.secondary)

                // Clickable worktree path
                #if os(macOS)
                if let path = feature.worktreePath {
                    Button(action: { openInFinder(path) }) {
                        HStack(spacing: 4) {
                            Image(systemName: "folder")
                                .font(.system(size: 10))
                            Text(path)
                                .font(.system(size: 10, design: .monospaced))
                                .lineLimit(1)
                                .truncationMode(.middle)
                        }
                        .foregroundColor(.secondary.opacity(0.7))
                    }
                    .buttonStyle(.plain)
                    .help("Open in Finder")
                }
                #endif
            }

            // Actions
            HStack(spacing: Spacing.small) {
                #if os(macOS)
                Button(action: { Task { await openInTerminal() } }) {
                    Label(isLaunching ? "Opening..." : "Open in Terminal", systemImage: "terminal")
                        .font(Typography.caption)
                }
                .buttonStyle(.bordered)
                .controlSize(.small)
                .disabled(isLaunching || feature.worktreePath == nil)
                #endif

                if feature.status == .inProgress {
                    Button(action: onStop) {
                        Label("Mark Done", systemImage: "checkmark.circle")
                            .font(Typography.caption)
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                    .tint(Accent.success)
                }
            }
        }
        .padding(Spacing.medium)
        .background(Surface.elevated)
        .cornerRadius(CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(statusColor.opacity(isHovered ? 0.5 : 0.2), lineWidth: 1)
        )
        .hoverable(isHovered: isHovered)
        .onHover { isHovered = $0 }
    }

    // MARK: - Actions

    #if os(macOS)
    /// Open Claude Code in the worktree directory
    @MainActor
    private func openInTerminal() async {
        guard let worktreePath = feature.worktreePath else { return }

        isLaunching = true
        defer { isLaunching = false }

        // Launch Claude Code in terminal without prompt (resume mode)
        let _ = await TerminalLauncher.launchClaudeCode(
            worktreePath: worktreePath,
            prompt: nil,  // No auto-paste on resume
            launchCommand: "claude --dangerously-skip-permissions"
        )
    }

    /// Open the worktree folder in Finder
    private func openInFinder(_ path: String) {
        NSWorkspace.shared.selectFile(nil, inFileViewerRootedAtPath: path)
    }
    #endif
}

// MARK: - Active Workspaces Section
// Shows all features currently being worked on

struct ActiveWorkspacesSection: View {
    @Environment(AppState.self) private var appState

    /// Features that are currently being worked on (in-progress or review)
    private var activeFeatures: [Feature] {
        appState.features.filter { $0.status == .inProgress || $0.status == .review }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.medium) {
            // Header
            HStack {
                HStack(spacing: Spacing.small) {
                    Image(systemName: "hammer.fill")
                        .foregroundColor(Accent.primary)
                    Text("ACTIVE WORKSPACES")
                        .sectionHeaderStyle()
                }

                if !activeFeatures.isEmpty {
                    Text("\(activeFeatures.count)")
                        .badgeStyle(color: Accent.primary)
                }

                Spacer()

                // Helpful tip
                if !activeFeatures.isEmpty {
                    Text("Each isolated — no conflicts!")
                        .font(Typography.caption)
                        .foregroundColor(.secondary)
                }
            }

            if activeFeatures.isEmpty {
                // Empty state
                VStack(spacing: Spacing.small) {
                    Image(systemName: "laptopcomputer")
                        .font(.system(size: 24))
                        .foregroundColor(.secondary.opacity(0.5))
                    Text("No active workspaces")
                        .font(Typography.body)
                        .foregroundColor(.secondary)
                    Text("Start a feature to create a workspace")
                        .font(Typography.caption)
                        .foregroundColor(.secondary.opacity(0.7))
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.large)
                .background(Surface.elevated)
                .cornerRadius(CornerRadius.medium)
            } else {
                // Workspace cards grid
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: Spacing.small) {
                    ForEach(activeFeatures) { feature in
                        WorkspaceCard(
                            feature: feature,
                            onResume: {
                                Task {
                                    await resumeWorkspace(feature)
                                }
                            },
                            onStop: {
                                Task {
                                    await appState.stopFeature(feature)
                                }
                            }
                        )
                    }
                }
            }
        }
    }

    @MainActor
    private func resumeWorkspace(_ feature: Feature) async {
        #if os(macOS)
        guard let worktreePath = feature.worktreePath else { return }

        // Launch Claude Code in terminal (resume mode - no prompt auto-paste)
        let _ = await TerminalLauncher.launchClaudeCode(
            worktreePath: worktreePath,
            prompt: nil,
            launchCommand: "claude --dangerously-skip-permissions"
        )
        #endif
    }
}

// MARK: - Preview

#if DEBUG
#Preview {
    VStack(spacing: Spacing.large) {
        // Single workspace card
        WorkspaceCard(
            feature: Feature(
                id: "dark-mode",
                title: "Add dark mode toggle",
                status: .inProgress,
                startedAt: Date().addingTimeInterval(-3600)
            ),
            onResume: {},
            onStop: {}
        )
        .frame(width: 250)

        // Section with multiple workspaces
        ActiveWorkspacesSection()
            .environment(AppState())
    }
    .padding()
    .frame(width: 600)
    .background(Surface.window)
}
#endif
