import SwiftUI

// MARK: - Refactor Dashboard View
/// Shows list of refactors for the current project with phase progress
/// Design: Linear-inspired, stepped progress indicators, dense rows

struct RefactorDashboardView: View {
    @Environment(AppState.self) private var appState
    @State private var refactors: [RefactorPlan] = []
    @State private var isLoading = true
    @State private var error: String?
    @State private var selectedRefactor: RefactorPlan?

    private let client = RefactorClient()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.medium) {
            // Header
            HStack {
                HStack(spacing: Spacing.small) {
                    Image(systemName: "arrow.triangle.branch")
                        .foregroundColor(Linear.accent)
                    Text("REFACTORS")
                        .sectionHeaderStyle()
                }

                if !refactors.isEmpty {
                    Text("\(refactors.count)")
                        .badgeStyle(color: Linear.accent)
                }

                Spacer()
            }

            // Content
            if isLoading {
                RefactorLoadingView()
            } else if let error = error {
                RefactorErrorView(message: error, onRetry: loadRefactors)
            } else if refactors.isEmpty {
                RefactorEmptyView()
            } else {
                ScrollView {
                    VStack(spacing: Spacing.small) {
                        ForEach(refactors) { plan in
                            RefactorCard(
                                plan: plan,
                                isSelected: selectedRefactor?.id == plan.id,
                                onSelect: { selectedRefactor = plan }
                            )
                        }
                    }
                }
                .frame(maxHeight: 300)
            }

            // Selected refactor detail (expanded view)
            if let plan = selectedRefactor {
                Divider()
                    .background(Linear.border)

                RefactorDetailView(plan: plan)
            }
        }
        .linearSection()
        .onAppear {
            loadRefactors()
        }
    }

    private func loadRefactors() {
        guard let project = appState.selectedProject else {
            error = "No project selected"
            isLoading = false
            return
        }

        isLoading = true
        error = nil

        Task {
            do {
                refactors = try await client.fetchRefactors(projectPath: project.path)
                // Auto-select first if none selected
                if selectedRefactor == nil {
                    selectedRefactor = refactors.first
                }
            } catch {
                self.error = error.localizedDescription
            }
            isLoading = false
        }
    }
}

// MARK: - Refactor Card

struct RefactorCard: View {
    let plan: RefactorPlan
    let isSelected: Bool
    let onSelect: () -> Void

    @State private var isHovered = false

    /// Status indicator color
    private var statusColor: Color {
        switch plan.state.status {
        case .planning: return Accent.brainstorm
        case .executing: return StatusColor.inProgressFallback
        case .paused: return Accent.warning
        case .completed: return Accent.success
        }
    }

    var body: some View {
        Button(action: onSelect) {
            HStack(spacing: Spacing.medium) {
                // Status indicator
                Circle()
                    .fill(statusColor)
                    .frame(width: 8, height: 8)
                    .pulse(isActive: plan.state.status == .executing)

                // Title and description
                VStack(alignment: .leading, spacing: 2) {
                    Text(plan.displayTitle)
                        .font(Typography.body)
                        .fontWeight(.medium)
                        .foregroundColor(Linear.textPrimary)
                        .lineLimit(1)

                    if let description = plan.description {
                        Text(description)
                            .font(Typography.caption)
                            .foregroundColor(Linear.textSecondary)
                            .lineLimit(1)
                    }
                }

                Spacer()

                // Progress badge
                HStack(spacing: Spacing.micro) {
                    Text("\(plan.state.completedCount)/\(plan.state.totalCount)")
                        .font(Typography.caption)
                        .foregroundColor(Linear.textTertiary)

                    // Mini progress bar
                    ProgressView(value: plan.state.progress)
                        .progressViewStyle(.linear)
                        .frame(width: 40)
                        .tint(statusColor)
                }

                // Status badge
                Text(plan.state.status.displayName)
                    .font(Typography.badge)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(statusColor.opacity(0.15))
                    .foregroundColor(statusColor)
                    .cornerRadius(CornerRadius.small)
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium, style: .continuous)
                    .fill(backgroundColor)
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium, style: .continuous)
                    .strokeBorder(
                        isSelected ? Linear.accent.opacity(0.5) : Color.clear,
                        lineWidth: 1
                    )
            )
        }
        .buttonStyle(.plain)
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.15)) {
                isHovered = hovering
            }
        }
    }

    private var backgroundColor: Color {
        if isSelected { return Linear.selectedBackground }
        if isHovered { return Linear.hoverBackground }
        return Color.clear
    }
}

// MARK: - Refactor Detail View

struct RefactorDetailView: View {
    let plan: RefactorPlan

    @State private var isExpanded = true

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.medium) {
            // Header with expand/collapse
            Button {
                withAnimation(.snappy(duration: 0.2)) {
                    isExpanded.toggle()
                }
            } label: {
                HStack {
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(Linear.textSecondary)
                        .frame(width: 12)

                    Text("Sessions")
                        .font(Typography.label)
                        .foregroundColor(Linear.textSecondary)

                    Text("(\(plan.state.completedCount)/\(plan.state.totalCount))")
                        .font(Typography.caption)
                        .foregroundColor(Linear.textTertiary)

                    Spacer()

                    if let current = plan.state.currentSession {
                        Text("Current: \(current)")
                            .font(Typography.caption)
                            .foregroundColor(Linear.accent)
                    }
                }
            }
            .buttonStyle(.plain)

            if isExpanded {
                // Stepped progress indicator
                SteppedProgressView(sessions: plan.state.sortedSessions, currentId: plan.state.currentSession)

                // Session list
                VStack(spacing: Spacing.micro) {
                    ForEach(plan.state.sortedSessions) { session in
                        SessionRow(
                            session: session,
                            isCurrent: session.sessionId == plan.state.currentSession
                        )
                    }
                }
            }
        }
    }
}

// MARK: - Stepped Progress View
/// Visual: [✓ 1.1] ──→ [● 1.2] - - → [○ 2.1]

struct SteppedProgressView: View {
    let sessions: [RefactorSessionState]
    let currentId: String?

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(Array(sessions.enumerated()), id: \.element.id) { index, session in
                    // Session node
                    SessionNode(
                        session: session,
                        isCurrent: session.sessionId == currentId
                    )

                    // Connector (except after last)
                    if index < sessions.count - 1 {
                        SessionConnector(
                            isCompleted: session.status == .completed
                        )
                    }
                }
            }
            .padding(.vertical, Spacing.small)
        }
    }
}

struct SessionNode: View {
    let session: RefactorSessionState
    let isCurrent: Bool

    private var nodeColor: Color {
        switch session.status {
        case .completed: return Accent.success
        case .inProgress: return StatusColor.inProgressFallback
        case .needsRevision: return Accent.warning
        case .pending: return Linear.textMuted
        }
    }

    private var nodeIcon: String {
        switch session.status {
        case .completed: return "checkmark"
        case .inProgress: return ""
        case .needsRevision: return "exclamationmark"
        case .pending: return ""
        }
    }

    var body: some View {
        VStack(spacing: Spacing.micro) {
            ZStack {
                Circle()
                    .fill(session.status == .pending ? Color.clear : nodeColor)
                    .stroke(nodeColor, lineWidth: 2)
                    .frame(width: isCurrent ? 24 : 20, height: isCurrent ? 24 : 20)

                if !nodeIcon.isEmpty {
                    Image(systemName: nodeIcon)
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(.white)
                }

                if session.status == .inProgress {
                    Circle()
                        .fill(nodeColor)
                        .frame(width: 10, height: 10)
                }
            }
            .pulse(isActive: isCurrent && session.status == .inProgress)

            Text(session.sessionId)
                .font(.system(size: 10, weight: isCurrent ? .semibold : .regular))
                .foregroundColor(isCurrent ? Linear.textPrimary : Linear.textTertiary)
        }
    }
}

struct SessionConnector: View {
    let isCompleted: Bool

    var body: some View {
        Rectangle()
            .fill(isCompleted ? Accent.success : Linear.textMuted.opacity(0.5))
            .frame(width: 24, height: 2)
            .padding(.bottom, 16) // Align with node center
    }
}

// MARK: - Session Row

struct SessionRow: View {
    let session: RefactorSessionState
    let isCurrent: Bool

    @State private var isHovered = false

    private var statusColor: Color {
        switch session.status {
        case .completed: return Accent.success
        case .inProgress: return StatusColor.inProgressFallback
        case .needsRevision: return Accent.warning
        case .pending: return Linear.textMuted
        }
    }

    private var statusIcon: String {
        switch session.status {
        case .completed: return "checkmark.circle.fill"
        case .inProgress: return "circle.fill"
        case .needsRevision: return "exclamationmark.circle.fill"
        case .pending: return "circle"
        }
    }

    var body: some View {
        HStack(spacing: Spacing.small) {
            // Status icon
            Image(systemName: statusIcon)
                .font(.system(size: 12))
                .foregroundColor(statusColor)
                .frame(width: 16)

            // Session ID
            Text(session.sessionId)
                .font(Typography.body)
                .fontWeight(isCurrent ? .medium : .regular)
                .foregroundColor(isCurrent ? Linear.textPrimary : Linear.textSecondary)

            Spacer()

            // Iteration count (if > 0)
            if session.iterationCount > 0 {
                Text("\(session.iterationCount) revision\(session.iterationCount > 1 ? "s" : "")")
                    .font(Typography.caption)
                    .foregroundColor(Linear.textTertiary)
            }

            // Audit badge
            if session.auditResult != .pending {
                Text(session.auditResult == .passed ? "Passed" : "Failed")
                    .font(Typography.badge)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(
                        (session.auditResult == .passed ? Accent.success : Accent.danger).opacity(0.15)
                    )
                    .foregroundColor(session.auditResult == .passed ? Accent.success : Accent.danger)
                    .cornerRadius(CornerRadius.small)
            }

            // Status badge
            Text(session.status.displayName)
                .font(Typography.badge)
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(statusColor.opacity(0.15))
                .foregroundColor(statusColor)
                .cornerRadius(CornerRadius.small)
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 8)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small, style: .continuous)
                .fill(backgroundColor)
        )
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.15)) {
                isHovered = hovering
            }
        }
    }

    private var backgroundColor: Color {
        if isCurrent { return Linear.accent.opacity(0.1) }
        if isHovered { return Linear.hoverBackground }
        return Color.clear
    }
}

// MARK: - Empty, Loading, Error States

struct RefactorEmptyView: View {
    var body: some View {
        VStack(spacing: Spacing.medium) {
            Image(systemName: "arrow.triangle.branch")
                .font(.system(size: 32))
                .foregroundColor(Linear.textMuted)

            Text("No refactors yet")
                .font(Typography.body)
                .foregroundColor(Linear.textSecondary)

            Text("Major refactors will appear here when started")
                .font(Typography.caption)
                .foregroundColor(Linear.textTertiary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xl)
    }
}

struct RefactorLoadingView: View {
    var body: some View {
        HStack(spacing: Spacing.medium) {
            ProgressView()
                .scaleEffect(0.8)
            Text("Loading refactors...")
                .font(Typography.body)
                .foregroundColor(Linear.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.large)
    }
}

struct RefactorErrorView: View {
    let message: String
    let onRetry: () -> Void

    var body: some View {
        VStack(spacing: Spacing.medium) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 24))
                .foregroundColor(Accent.warning)

            Text(message)
                .font(Typography.body)
                .foregroundColor(Linear.textSecondary)
                .multilineTextAlignment(.center)

            Button("Retry") {
                onRetry()
            }
            .buttonStyle(.linearSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.large)
    }
}

// MARK: - Preview

#if DEBUG
#Preview {
    RefactorDashboardView()
        .environment(AppState())
        .frame(width: 500, height: 600)
        .background(Linear.background)
}
#endif
