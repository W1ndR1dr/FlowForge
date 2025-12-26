import SwiftUI

/// Sheet for initializing a new project with FlowForge
struct ProjectSetupSheet: View {
    @Environment(AppState.self) private var appState
    @Environment(\.dismiss) private var dismiss

    let project: Project

    @State private var isInitializing = false
    @State private var useQuickMode = true
    @State private var projectDescription = ""
    @State private var projectVision = ""

    var body: some View {
        VStack(spacing: 0) {
            // Header
            header

            Divider()

            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.lg) {
                    projectInfo
                    modeSelector
                    if !useQuickMode {
                        guidedFields
                    }
                    whatGetsCreated
                }
                .padding(DesignTokens.Spacing.lg)
            }

            Divider()

            // Footer with actions
            footer
        }
        .frame(width: 480, height: useQuickMode ? 420 : 560)
    }

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Initialize FlowForge")
                    .font(.headline)
                Text(project.name)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Button {
                dismiss()
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .foregroundStyle(.secondary)
                    .font(.title2)
            }
            .buttonStyle(.plain)
        }
        .padding(DesignTokens.Spacing.md)
    }

    private var projectInfo: some View {
        HStack(spacing: DesignTokens.Spacing.md) {
            Image(systemName: "folder.badge.gearshape")
                .font(.largeTitle)
                .foregroundStyle(DesignTokens.Colors.primary)

            VStack(alignment: .leading, spacing: 4) {
                Text(project.name)
                    .font(.headline)
                Text(project.path)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }

            Spacer()
        }
        .padding(DesignTokens.Spacing.md)
        .background(DesignTokens.Colors.surface)
        .clipShape(RoundedRectangle(cornerRadius: DesignTokens.Radius.md))
    }

    private var modeSelector: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
            Text("Setup Mode")
                .font(.subheadline.weight(.medium))

            HStack(spacing: DesignTokens.Spacing.sm) {
                modeButton(
                    title: "Quick",
                    subtitle: "Just the essentials",
                    icon: "bolt.fill",
                    isSelected: useQuickMode
                ) {
                    withAnimation(.spring(response: 0.3)) {
                        useQuickMode = true
                    }
                }

                modeButton(
                    title: "Guided",
                    subtitle: "Add project context",
                    icon: "slider.horizontal.3",
                    isSelected: !useQuickMode
                ) {
                    withAnimation(.spring(response: 0.3)) {
                        useQuickMode = false
                    }
                }
            }
        }
    }

    private func modeButton(
        title: String,
        subtitle: String,
        icon: String,
        isSelected: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            VStack(spacing: DesignTokens.Spacing.xs) {
                Image(systemName: icon)
                    .font(.title2)
                Text(title)
                    .font(.subheadline.weight(.medium))
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity)
            .padding(DesignTokens.Spacing.md)
            .background(isSelected ? DesignTokens.Colors.primary.opacity(0.1) : DesignTokens.Colors.surface)
            .overlay(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                    .stroke(isSelected ? DesignTokens.Colors.primary : Color.clear, lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: DesignTokens.Radius.md))
        }
        .buttonStyle(.plain)
    }

    private var guidedFields: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.md) {
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                Text("Project Description")
                    .font(.subheadline.weight(.medium))
                TextField("What does this project do?", text: $projectDescription, axis: .vertical)
                    .textFieldStyle(.roundedBorder)
                    .lineLimit(2...4)
            }

            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                Text("Vision")
                    .font(.subheadline.weight(.medium))
                TextField("Where is this project headed?", text: $projectVision, axis: .vertical)
                    .textFieldStyle(.roundedBorder)
                    .lineLimit(2...4)
            }
        }
    }

    private var whatGetsCreated: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
            Text("What gets created")
                .font(.subheadline.weight(.medium))

            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                fileItem(".flowforge/", "FlowForge configuration directory")
                fileItem("config.json", "Project settings")
                fileItem("registry.json", "Feature database")
                fileItem("project-context.md", "AI context for prompts")
            }
            .padding(DesignTokens.Spacing.sm)
            .background(DesignTokens.Colors.surface)
            .clipShape(RoundedRectangle(cornerRadius: DesignTokens.Radius.sm))
        }
    }

    private func fileItem(_ name: String, _ description: String) -> some View {
        HStack(spacing: DesignTokens.Spacing.sm) {
            Image(systemName: name.hasSuffix("/") ? "folder.fill" : "doc.fill")
                .foregroundStyle(.secondary)
                .frame(width: 16)
            Text(name)
                .font(.caption.monospaced())
            Text("-")
                .foregroundStyle(.tertiary)
            Text(description)
                .font(.caption)
                .foregroundStyle(.secondary)
            Spacer()
        }
    }

    private var footer: some View {
        HStack {
            Button("Cancel") {
                dismiss()
            }
            .keyboardShortcut(.escape)

            Spacer()

            Button {
                Task {
                    await initializeProject()
                }
            } label: {
                HStack(spacing: DesignTokens.Spacing.xs) {
                    if isInitializing {
                        ProgressView()
                            .controlSize(.small)
                    }
                    Text(isInitializing ? "Initializing..." : "Initialize")
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(isInitializing)
            .keyboardShortcut(.return)
        }
        .padding(DesignTokens.Spacing.md)
    }

    private func initializeProject() async {
        isInitializing = true

        do {
            try await appState.initializeProject(project, quick: useQuickMode)
            dismiss()
        } catch {
            appState.errorMessage = error.localizedDescription
        }

        isInitializing = false
    }
}
