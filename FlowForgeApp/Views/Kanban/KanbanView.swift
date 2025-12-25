import SwiftUI

struct KanbanView: View {
    @Environment(AppState.self) private var appState
    @State private var showingAddFeature = false
    @State private var newFeatureTitle = ""
    @State private var searchText = ""
    @State private var selectedTags: Set<String> = []

    private let displayedStatuses: [FeatureStatus] = [
        .planned,
        .inProgress,
        .review,
        .completed,
        .blocked
    ]

    // Filtered features based on search and tags
    private var filteredFeatures: [Feature] {
        appState.features.filter { feature in
            let matchesSearch = searchText.isEmpty ||
                feature.title.localizedCaseInsensitiveContains(searchText) ||
                (feature.description?.localizedCaseInsensitiveContains(searchText) ?? false)

            let matchesTags = selectedTags.isEmpty ||
                !selectedTags.isDisjoint(with: Set(feature.tags))

            return matchesSearch && matchesTags
        }
    }

    // All unique tags across features
    private var allTags: [String] {
        Array(Set(appState.features.flatMap { $0.tags })).sorted()
    }

    private func features(for status: FeatureStatus) -> [Feature] {
        filteredFeatures.filter { $0.status == status }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                if let project = appState.selectedProject {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(project.name)
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("\(filteredFeatures.count) of \(appState.features.count) features")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                // Shipping Streak Badge (Wave 4.4)
                if appState.shippingStats.currentStreak > 0 || appState.shippingStats.totalShipped > 0 {
                    HStack(spacing: 8) {
                        Text(appState.shippingStats.displayText)
                            .font(.headline)
                        if appState.shippingStats.longestStreak > appState.shippingStats.currentStreak {
                            Text("Best: \(appState.shippingStats.longestStreak)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Text("| \(appState.shippingStats.totalShipped) shipped")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.orange.opacity(0.15))
                    .cornerRadius(8)
                }

                Spacer()

                // Search field
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    TextField("Search features...", text: $searchText)
                        .textFieldStyle(.plain)
                        .frame(width: 200)
                    if !searchText.isEmpty {
                        Button {
                            searchText = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(8)
                .background(Color.controlBackground)
                .cornerRadius(8)

                // Planned slots indicator
                if appState.plannedSlotsRemaining > 0 {
                    Text("\(appState.plannedSlotsRemaining) slot\(appState.plannedSlotsRemaining == 1 ? "" : "s") left")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(4)
                } else {
                    Text("Full!")
                        .font(.caption)
                        .foregroundColor(.orange)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.15))
                        .cornerRadius(4)
                }

                Button {
                    showingAddFeature = true
                } label: {
                    Label("Add Feature", systemImage: "plus")
                }
                .buttonStyle(.borderedProminent)
                .disabled(!appState.canAddPlannedFeature)
            }
            .padding()
            .background(Color.windowBackground)

            // Tag filter chips
            if !allTags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(allTags, id: \.self) { tag in
                            TagFilterChip(
                                tag: tag,
                                isSelected: selectedTags.contains(tag)
                            ) {
                                if selectedTags.contains(tag) {
                                    selectedTags.remove(tag)
                                } else {
                                    selectedTags.insert(tag)
                                }
                            }
                        }

                        if !selectedTags.isEmpty {
                            Button("Clear") {
                                selectedTags.removeAll()
                            }
                            .font(.caption)
                            .foregroundColor(.secondary)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                }
                .background(Color.windowBackground.opacity(0.5))
            }

            Divider()

            // Kanban Board
            ScrollView(.horizontal, showsIndicators: true) {
                HStack(alignment: .top, spacing: 16) {
                    ForEach(displayedStatuses, id: \.self) { status in
                        StatusColumn(
                            status: status,
                            features: features(for: status),
                            projectName: appState.selectedProject?.name ?? ""
                        )
                    }
                }
                .padding()
            }
        }
        .sheet(isPresented: $showingAddFeature) {
            AddFeatureSheet(
                isPresented: $showingAddFeature,
                featureTitle: $newFeatureTitle
            )
        }
    }
}

struct AddFeatureSheet: View {
    @Environment(AppState.self) private var appState
    @Binding var isPresented: Bool
    @Binding var featureTitle: String

    var body: some View {
        VStack(spacing: 20) {
            Text("Add New Feature")
                .font(.title2)
                .fontWeight(.bold)

            TextField("Feature title", text: $featureTitle)
                .textFieldStyle(.roundedBorder)
                .onSubmit {
                    addFeature()
                }

            HStack {
                Button("Cancel") {
                    isPresented = false
                    featureTitle = ""
                }
                .keyboardShortcut(.cancelAction)

                Spacer()

                Button("Add") {
                    addFeature()
                }
                .keyboardShortcut(.defaultAction)
                .disabled(featureTitle.trimmingCharacters(in: .whitespaces).isEmpty)
            }
        }
        .padding()
        .frame(width: 400)
    }

    private func addFeature() {
        guard !featureTitle.trimmingCharacters(in: .whitespaces).isEmpty else { return }

        Task {
            await appState.addFeature(title: featureTitle)
            await MainActor.run {
                isPresented = false
                featureTitle = ""
            }
        }
    }
}

// Tag filter chip for search/filter
struct TagFilterChip: View {
    let tag: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(tag)
                .font(.caption)
                .padding(.horizontal, 10)
                .padding(.vertical, 5)
                .background(isSelected ? Color.accentColor : Color.secondary.opacity(0.2))
                .foregroundColor(isSelected ? .white : .primary)
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    KanbanView()
        .environment(AppState())
        .frame(width: 1200, height: 800)
}
