import SwiftUI

/// View shown when an uninitialized project is selected
struct UninitializedProjectView: View {
    @Environment(AppState.self) private var appState
    let project: Project

    var body: some View {
        VStack(spacing: DesignTokens.Spacing.xl) {
            Spacer()

            // Icon
            Image(systemName: "bolt.badge.clock")
                .font(.system(size: 64))
                .foregroundStyle(DesignTokens.Colors.primary.opacity(0.6))
                .symbolRenderingMode(.hierarchical)

            // Title and description
            VStack(spacing: DesignTokens.Spacing.sm) {
                Text("Set Up FlowForge")
                    .font(.title2.weight(.semibold))

                Text("**\(project.name)** is a Git repository but hasn't been set up with FlowForge yet.")
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 400)
            }

            // Features list
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
                featureRow(icon: "list.bullet.clipboard", text: "Track features in a visual kanban board")
                featureRow(icon: "arrow.triangle.branch", text: "Work on multiple features in parallel")
                featureRow(icon: "doc.text.magnifyingglass", text: "Generate AI prompts with full context")
                featureRow(icon: "arrow.triangle.merge", text: "Merge with confidence")
            }
            .padding(DesignTokens.Spacing.lg)
            .background(DesignTokens.Colors.surface)
            .clipShape(RoundedRectangle(cornerRadius: DesignTokens.Radius.lg))

            // Initialize button
            Button {
                appState.projectToInitialize = project
                appState.showingProjectSetup = true
            } label: {
                HStack(spacing: DesignTokens.Spacing.sm) {
                    Image(systemName: "bolt.fill")
                    Text("Initialize FlowForge")
                }
                .padding(.horizontal, DesignTokens.Spacing.lg)
                .padding(.vertical, DesignTokens.Spacing.md)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Spacer()
        }
        .padding(DesignTokens.Spacing.xl)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(DesignTokens.Colors.background)
    }

    private func featureRow(icon: String, text: String) -> some View {
        HStack(spacing: DesignTokens.Spacing.md) {
            Image(systemName: icon)
                .foregroundStyle(DesignTokens.Colors.primary)
                .frame(width: 24)
            Text(text)
                .font(.subheadline)
        }
    }
}
