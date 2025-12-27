import SwiftUI

struct ProjectListView: View {
    @Environment(AppState.self) private var appState
    @State private var hiddenSectionExpanded = false

    var body: some View {
        @Bindable var state = appState

        List(selection: Binding(
            get: { appState.selectedProject },
            set: { newProject in
                if let project = newProject {
                    appState.markProjectAccessed(project)
                    Task {
                        await appState.selectProject(project)
                    }
                }
            }
        )) {
            // Visible projects
            ForEach(appState.visibleSortedProjects) { project in
                ProjectRow(project: project)
                    .tag(project)
                    .contextMenu {
                        Button("Hide Project") {
                            appState.hideProject(project)
                        }
                    }
            }

            // Hidden section (only if there are hidden projects)
            if !appState.hiddenProjects.isEmpty {
                Section {
                    if hiddenSectionExpanded {
                        ForEach(appState.hiddenProjects) { project in
                            ProjectRow(project: project)
                                .tag(project)
                                .opacity(0.6)
                                .contextMenu {
                                    Button("Show Project") {
                                        appState.showProject(project)
                                    }
                                }
                        }
                    }
                } header: {
                    Button {
                        withAnimation(.snappy) {
                            hiddenSectionExpanded.toggle()
                        }
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: hiddenSectionExpanded ? "chevron.down" : "chevron.right")
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                            Text("Hidden (\(appState.hiddenProjects.count))")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                            Spacer()
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .navigationTitle("Projects")
        .toolbar {
            ToolbarItem(placement: .automatic) {
                SortPicker(selection: $state.projectSortOrder)
                    .help("Sort projects")
            }
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task {
                        await appState.loadProjects()
                    }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .help("Refresh projects")
            }
        }
    }
}

struct ProjectRow: View {
    let project: Project

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text(project.name)
                        .font(.headline)

                    if project.needsInitialization {
                        Text("Setup")
                            .font(.caption2.weight(.medium))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(DesignTokens.Colors.warning.opacity(0.15))
                            .foregroundStyle(DesignTokens.Colors.warning)
                            .clipShape(Capsule())
                    }
                }
                Text(project.path)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }

            Spacer()

            if project.needsInitialization {
                Image(systemName: "bolt.badge.clock")
                    .foregroundStyle(.secondary)
                    .font(.caption)
            }
        }
        .padding(.vertical, 4)
        .opacity(project.needsInitialization ? 0.8 : 1.0)
    }
}

#Preview {
    ProjectListView()
        .environment(AppState())
        .frame(width: 250, height: 600)
}
