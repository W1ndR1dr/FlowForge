import SwiftUI

/// Mission Control Dashboard - A shipping-focused alternative to Kanban
///
/// Design influenced by:
/// - Ryan Singer (Basecamp): Clear scopes, progress visualization
/// - Julie Zhuo (Meta): Emotional design, obvious next action
/// - Kent Beck (XP): Friction-free deployment, small releases
struct MissionControlView: View {
    @Environment(AppState.self) private var appState

    // Get active feature (in-progress or review)
    private var activeFeature: Feature? {
        appState.features.first { $0.status == .inProgress }
            ?? appState.features.first { $0.status == .review }
    }

    // Get planned features (up next)
    private var upNextFeatures: [Feature] {
        Array(appState.features.filter { $0.status == .planned }.prefix(3))
    }

    // Get recently shipped (completed this week)
    private var shippedThisWeek: [Feature] {
        let weekAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date()) ?? Date()
        return appState.features.filter { feature in
            feature.status == .completed &&
            (feature.completedAt ?? Date.distantPast) > weekAgo
        }
    }

    // Get blocked features
    private var blockedFeatures: [Feature] {
        appState.features.filter { $0.status == .blocked }
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header with streak
                headerView

                // Today's Mission (the ONE thing)
                todaysMissionSection

                // Up Next (max 3)
                upNextSection

                // Blocked (if any)
                if !blockedFeatures.isEmpty {
                    blockedSection
                }

                // Shipped This Week
                shippedSection
            }
            .padding()
        }
        .background(Color.windowBackground)
    }

    // MARK: - Header

    private var headerView: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                if let project = appState.selectedProject {
                    Text(project.name)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                }
                Text("Mission Control")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()

            // Streak Badge
            VStack(alignment: .trailing, spacing: 4) {
                Text(appState.shippingStats.displayText)
                    .font(.title2)
                    .fontWeight(.semibold)
                if appState.shippingStats.totalShipped > 0 {
                    Text("\(appState.shippingStats.totalShipped) total shipped")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.orange.opacity(0.15))
            .cornerRadius(12)
        }
    }

    // MARK: - Today's Mission

    private var todaysMissionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("TODAY'S MISSION")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)

            if let feature = activeFeature {
                ActiveMissionCard(feature: feature)
            } else if let nextFeature = upNextFeatures.first {
                // No active feature - prompt to start
                StartMissionCard(feature: nextFeature)
            } else {
                EmptyMissionCard()
            }
        }
    }

    // MARK: - Up Next

    private var upNextSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("UP NEXT")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondary)

                Spacer()

                Text("\(upNextFeatures.count)/\(AppState.maxPlannedFeatures)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.secondary.opacity(0.1))
                    .cornerRadius(4)
            }

            if upNextFeatures.isEmpty {
                HStack {
                    Image(systemName: "sparkles")
                        .foregroundColor(.green)
                    Text("Backlog clear! Time to brainstorm.")
                        .foregroundColor(.secondary)
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color.green.opacity(0.1))
                .cornerRadius(8)
            } else {
                ForEach(upNextFeatures) { feature in
                    UpNextCard(feature: feature)
                }
            }
        }
    }

    // MARK: - Blocked

    private var blockedSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("BLOCKED")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.red)

                Text("\(blockedFeatures.count)")
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(Color.red)
                    .cornerRadius(4)
            }

            ForEach(blockedFeatures) { feature in
                BlockedCard(feature: feature)
            }
        }
    }

    // MARK: - Shipped This Week

    private var shippedSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("SHIPPED THIS WEEK")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondary)

                if !shippedThisWeek.isEmpty {
                    Text("\(shippedThisWeek.count)")
                        .font(.caption)
                        .foregroundColor(.green)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.green.opacity(0.2))
                        .cornerRadius(4)
                }
            }

            if shippedThisWeek.isEmpty {
                Text("Nothing shipped yet this week. Let's change that!")
                    .foregroundColor(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.secondary.opacity(0.05))
                    .cornerRadius(8)
            } else {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                    ForEach(shippedThisWeek) { feature in
                        ShippedCard(feature: feature)
                    }
                }
            }
        }
    }
}

// MARK: - Card Components

struct ActiveMissionCard: View {
    @Environment(AppState.self) private var appState
    let feature: Feature

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Circle()
                    .fill(feature.status == .review ? Color.orange : Color.blue)
                    .frame(width: 12, height: 12)

                Text(feature.title)
                    .font(.title3)
                    .fontWeight(.semibold)

                Spacer()

                Text(feature.status.displayName)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(feature.status == .review ? Color.orange.opacity(0.2) : Color.blue.opacity(0.2))
                    .cornerRadius(4)
            }

            if let description = feature.description, !description.isEmpty {
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }

            // Big SHIP button (Julie Zhuo - obvious next action)
            if feature.status == .review {
                Button {
                    // Would trigger ship
                } label: {
                    HStack {
                        Image(systemName: "paperplane.fill")
                        Text("SHIP IT")
                            .fontWeight(.bold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
            }
        }
        .padding()
        .background(Color.controlBackground)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.blue.opacity(0.3), lineWidth: 2)
        )
    }
}

struct StartMissionCard: View {
    @Environment(AppState.self) private var appState
    let feature: Feature

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Ready to build?")
                .font(.headline)
                .foregroundColor(.secondary)

            Text(feature.title)
                .font(.title3)
                .fontWeight(.semibold)

            Button {
                Task {
                    await appState.startFeature(feature)
                }
            } label: {
                HStack {
                    Image(systemName: "hammer.fill")
                    Text("START BUILDING")
                        .fontWeight(.bold)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
        }
        .padding()
        .background(Color.controlBackground)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.blue.opacity(0.2), lineWidth: 1)
        )
    }
}

struct EmptyMissionCard: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 48))
                .foregroundColor(.green)

            Text("All clear!")
                .font(.headline)

            Text("No active mission. Add a feature to get started.")
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(32)
        .frame(maxWidth: .infinity)
        .background(Color.green.opacity(0.1))
        .cornerRadius(12)
    }
}

struct UpNextCard: View {
    let feature: Feature

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(feature.title)
                    .font(.subheadline)
                    .fontWeight(.medium)

                if !feature.tags.isEmpty {
                    Text(feature.tags.joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            if let complexity = feature.complexity {
                Text(complexity.displayName)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.controlBackground)
        .cornerRadius(8)
    }
}

struct BlockedCard: View {
    let feature: Feature

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.red)

            Text(feature.title)
                .font(.subheadline)

            Spacer()
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(8)
    }
}

struct ShippedCard: View {
    let feature: Feature

    var body: some View {
        HStack {
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)

            Text(feature.title)
                .font(.caption)
                .lineLimit(1)

            Spacer()
        }
        .padding(8)
        .background(Color.green.opacity(0.1))
        .cornerRadius(6)
    }
}

#Preview {
    MissionControlView()
        .environment(AppState())
        .frame(width: 800, height: 900)
}
