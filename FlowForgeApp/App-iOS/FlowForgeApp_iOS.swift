import SwiftUI

@main
struct FlowForgeApp_iOS: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            iOSContentView()
                .environment(appState)
        }
    }
}

/// iOS-specific root view with tab navigation
struct iOSContentView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        TabView {
            // Roadmap Tab
            NavigationStack {
                iOSRoadmapView()
                    .navigationTitle(appState.selectedProject?.name ?? "FlowForge")
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            ConnectionStatusBadge()
                        }
                    }
            }
            .tabItem {
                Label("Roadmap", systemImage: "list.bullet.rectangle")
            }

            // Brainstorm Tab
            NavigationStack {
                BrainstormInputView()
                    .navigationTitle("Brainstorm")
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            ConnectionStatusBadge()
                        }
                    }
            }
            .tabItem {
                Label("Brainstorm", systemImage: "lightbulb")
            }

            // Settings Tab
            NavigationStack {
                iOSSettingsView()
                    .navigationTitle("Settings")
            }
            .tabItem {
                Label("Settings", systemImage: "gear")
            }
        }
    }
}

/// Connection status indicator for toolbar
struct ConnectionStatusBadge: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(appState.isConnectedToServer ? Color.green : Color.red)
                .frame(width: 8, height: 8)
            Text(appState.isConnectedToServer ? "Connected" : "Offline")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

/// iOS Roadmap view - list-based instead of Kanban
struct iOSRoadmapView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        List {
            ForEach(FeatureStatus.allCases, id: \.self) { status in
                Section(status.displayName) {
                    let features = appState.features(for: status)
                    if features.isEmpty {
                        Text("No features")
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(features) { feature in
                            iOSFeatureRow(feature: feature)
                        }
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .refreshable {
            await appState.loadFeatures()
        }
        .overlay {
            if appState.isLoading {
                ProgressView()
            }
        }
    }
}

/// iOS Feature row for list view
struct iOSFeatureRow: View {
    @Environment(AppState.self) private var appState
    let feature: Feature

    @State private var showingDetail = false
    @State private var isCopying = false
    @State private var showCopiedAlert = false

    var body: some View {
        Button {
            showingDetail = true
        } label: {
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(feature.title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Spacer()

                    if let complexity = feature.complexity {
                        Text(complexity.displayName)
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(complexityColor(complexity).opacity(0.2))
                            .foregroundColor(complexityColor(complexity))
                            .clipShape(Capsule())
                    }
                }

                if let description = feature.description, !description.isEmpty {
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }

                if !feature.tags.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 4) {
                            ForEach(feature.tags, id: \.self) { tag in
                                Text(tag)
                                    .font(.caption2)
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.accentColor.opacity(0.2))
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(.plain)
        .swipeActions(edge: .trailing) {
            Button {
                copyPrompt()
            } label: {
                Label("Copy Prompt", systemImage: "doc.on.clipboard")
            }
            .tint(.blue)
        }
        .sheet(isPresented: $showingDetail) {
            iOSFeatureDetailView(feature: feature)
        }
        .alert("Copied!", isPresented: $showCopiedAlert) {
            Button("OK") {}
        } message: {
            Text("Implementation prompt copied to clipboard")
        }
    }

    private func complexityColor(_ complexity: Complexity) -> Color {
        switch complexity {
        case .small: return .green
        case .medium: return .orange
        case .large: return .red
        case .epic: return .purple
        }
    }

    private func copyPrompt() {
        guard let projectName = appState.selectedProject?.name else { return }
        isCopying = true

        Task {
            do {
                let apiClient = APIClient()
                let prompt = try await apiClient.getPrompt(
                    project: projectName,
                    featureId: feature.id
                )

                await MainActor.run {
                    PlatformPasteboard.copy(prompt)
                    isCopying = false
                    showCopiedAlert = true
                }
            } catch {
                await MainActor.run {
                    isCopying = false
                    print("Failed to copy prompt: \(error)")
                }
            }
        }
    }
}

/// iOS Feature detail view
struct iOSFeatureDetailView: View {
    @Environment(AppState.self) private var appState
    @Environment(\.dismiss) private var dismiss
    let feature: Feature

    @State private var showCopiedAlert = false

    var body: some View {
        NavigationStack {
            List {
                Section("Details") {
                    LabeledContent("ID", value: feature.id)
                    LabeledContent("Status", value: feature.status.displayName)
                    if let complexity = feature.complexity {
                        LabeledContent("Complexity", value: complexity.displayName)
                    }
                    if let branch = feature.branch {
                        LabeledContent("Branch", value: branch)
                    }
                }

                if let description = feature.description, !description.isEmpty {
                    Section("Description") {
                        Text(description)
                    }
                }

                if !feature.tags.isEmpty {
                    Section("Tags") {
                        FlowLayout(spacing: 8) {
                            ForEach(feature.tags, id: \.self) { tag in
                                Text(tag)
                                    .font(.caption)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 6)
                                    .background(Color.accentColor.opacity(0.2))
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }

                Section("Actions") {
                    Button {
                        copyPrompt()
                    } label: {
                        Label("Copy Implementation Prompt", systemImage: "doc.on.clipboard")
                    }

                    Button {
                        Task {
                            await appState.updateFeatureStatus(feature, to: .inProgress)
                            dismiss()
                        }
                    } label: {
                        Label("Start Feature", systemImage: "play.fill")
                    }
                    .disabled(feature.status == .inProgress)
                }
            }
            .navigationTitle(feature.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
        .alert("Copied!", isPresented: $showCopiedAlert) {
            Button("OK") {}
        } message: {
            Text("Implementation prompt copied to clipboard")
        }
    }

    private func copyPrompt() {
        guard let projectName = appState.selectedProject?.name else { return }

        Task {
            do {
                let apiClient = APIClient()
                let prompt = try await apiClient.getPrompt(
                    project: projectName,
                    featureId: feature.id
                )

                await MainActor.run {
                    PlatformPasteboard.copy(prompt)
                    showCopiedAlert = true
                }
            } catch {
                print("Failed to copy prompt: \(error)")
            }
        }
    }
}

/// Brainstorm input view for pasting Claude output
struct BrainstormInputView: View {
    @Environment(AppState.self) private var appState
    @State private var claudeOutput = ""
    @State private var isParsing = false
    @State private var parseError: String?
    @State private var showingReview = false

    var body: some View {
        VStack(spacing: 0) {
            if appState.selectedProject == nil {
                ContentUnavailableView(
                    "No Project Selected",
                    systemImage: "folder.badge.questionmark",
                    description: Text("Select a project in Settings first.")
                )
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        // Instructions
                        GroupBox {
                            VStack(alignment: .leading, spacing: 12) {
                                Label("How it works", systemImage: "info.circle")
                                    .font(.headline)

                                Text("1. Brainstorm with Claude (CLI or web)")
                                Text("2. Ask Claude to output READY_FOR_APPROVAL")
                                Text("3. Copy Claude's response and paste below")
                                Text("4. Review and approve proposals")
                            }
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        }

                        // Input area
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Claude's Output")
                                .font(.headline)

                            TextEditor(text: $claudeOutput)
                                .frame(minHeight: 200)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.secondary.opacity(0.3), lineWidth: 1)
                                )
                                .overlay(alignment: .topLeading) {
                                    if claudeOutput.isEmpty {
                                        Text("Paste READY_FOR_APPROVAL output here...")
                                            .foregroundColor(.secondary)
                                            .padding(8)
                                            .allowsHitTesting(false)
                                    }
                                }
                        }

                        // Error display
                        if let error = parseError {
                            Text(error)
                                .font(.caption)
                                .foregroundColor(.red)
                                .padding(.horizontal)
                        }

                        // Parse button
                        Button {
                            parseProposals()
                        } label: {
                            HStack {
                                if isParsing {
                                    ProgressView()
                                        .scaleEffect(0.8)
                                } else {
                                    Image(systemName: "wand.and.stars")
                                }
                                Text("Parse Proposals")
                            }
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(claudeOutput.isEmpty || isParsing)
                    }
                    .padding()
                }
            }
        }
        .sheet(isPresented: $showingReview) {
            iOSProposalReviewSheet(
                proposals: Binding(
                    get: { appState.parsedProposals },
                    set: { appState.parsedProposals = $0 }
                ),
                projectName: appState.selectedProject?.name ?? "",
                onComplete: { proposals in
                    Task {
                        try? await appState.approveProposals(proposals)
                        claudeOutput = ""
                    }
                }
            )
        }
    }

    private func parseProposals() {
        isParsing = true
        parseError = nil

        Task {
            do {
                try await appState.parseBrainstorm(claudeOutput: claudeOutput)
                await MainActor.run {
                    isParsing = false
                    showingReview = true
                }
            } catch {
                await MainActor.run {
                    isParsing = false
                    parseError = error.localizedDescription
                }
            }
        }
    }
}

/// iOS-adapted proposal review sheet
struct iOSProposalReviewSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var proposals: [Proposal]
    let projectName: String
    let onComplete: ([Proposal]) -> Void

    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            List {
                Section {
                    ForEach($proposals) { $proposal in
                        iOSProposalRow(proposal: $proposal)
                    }
                } header: {
                    Text("\(proposals.count) proposal(s)")
                } footer: {
                    HStack {
                        Text("\(approvedCount) approved")
                            .foregroundColor(.green)
                        Text("•")
                        Text("\(declinedCount) declined")
                            .foregroundColor(.red)
                        Text("•")
                        Text("\(pendingCount) pending")
                            .foregroundColor(.secondary)
                    }
                    .font(.caption)
                }
            }
            .navigationTitle("Review Proposals")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button {
                        submitApproved()
                    } label: {
                        if isSubmitting {
                            ProgressView()
                        } else {
                            Text("Add \(approvedCount)")
                        }
                    }
                    .disabled(approvedCount == 0 || isSubmitting)
                }
            }
        }
    }

    private var approvedCount: Int {
        proposals.filter { $0.status == .approved }.count
    }

    private var declinedCount: Int {
        proposals.filter { $0.status == .declined }.count
    }

    private var pendingCount: Int {
        proposals.filter { $0.status == .pending }.count
    }

    private func submitApproved() {
        isSubmitting = true
        onComplete(proposals)
        dismiss()
    }
}

/// Single proposal row for iOS
struct iOSProposalRow: View {
    @Binding var proposal: Proposal

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(proposal.title)
                    .font(.headline)
                    .strikethrough(proposal.status == .declined)

                Spacer()

                StatusPill(status: proposal.status)
            }

            Text(proposal.description)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(2)

            HStack(spacing: 8) {
                Text("P\(proposal.priority)")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(priorityColor.opacity(0.2))
                    .foregroundColor(priorityColor)
                    .clipShape(Capsule())

                Text(proposal.complexity.capitalized)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

            // Action buttons
            if proposal.status == .pending {
                HStack(spacing: 12) {
                    Button("Approve") {
                        proposal.status = .approved
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                    .controlSize(.small)

                    Button("Decline") {
                        proposal.status = .declined
                    }
                    .buttonStyle(.bordered)
                    .tint(.red)
                    .controlSize(.small)

                    Button("Defer") {
                        proposal.status = .deferred
                    }
                    .buttonStyle(.bordered)
                    .tint(.orange)
                    .controlSize(.small)
                }
            }
        }
        .padding(.vertical, 4)
    }

    private var priorityColor: Color {
        switch proposal.priority {
        case 1: return .red
        case 2: return .orange
        case 3: return .yellow
        default: return .blue
        }
    }
}

/// Status pill for proposals
struct StatusPill: View {
    let status: ProposalStatus

    var body: some View {
        Text(status.displayName)
            .font(.caption2)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(statusColor.opacity(0.2))
            .foregroundColor(statusColor)
            .clipShape(Capsule())
    }

    private var statusColor: Color {
        switch status {
        case .pending: return .gray
        case .approved: return .green
        case .declined: return .red
        case .deferred: return .orange
        }
    }
}

/// iOS Settings view
struct iOSSettingsView: View {
    @Environment(AppState.self) private var appState
    @AppStorage("serverURL") private var serverURL = "http://localhost:8081"

    @State private var isTesting = false
    @State private var testResult: String?
    @State private var testSuccess: Bool?

    var body: some View {
        Form {
            Section {
                TextField("Server URL", text: $serverURL)
                    .textContentType(.URL)
                    .autocapitalization(.none)
                    .keyboardType(.URL)
                    .onChange(of: serverURL) { _, newValue in
                        appState.updateServerURL(newValue)
                    }

                Button {
                    testConnection()
                } label: {
                    HStack {
                        if isTesting {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "network")
                        }
                        Text("Test Connection")
                    }
                }
                .disabled(isTesting)

                if let result = testResult {
                    HStack {
                        Image(systemName: testSuccess == true ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .foregroundColor(testSuccess == true ? .green : .red)
                        Text(result)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            } header: {
                Text("Server")
            } footer: {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Enter your FlowForge server URL.")
                    Text("For Tailscale: http://hostname.tailnet-name.ts.net:8081")
                        .font(.caption2)
                }
            }

            Section("Connection Status") {
                HStack {
                    Circle()
                        .fill(appState.isConnectedToServer ? Color.green : Color.red)
                        .frame(width: 12, height: 12)
                    Text(appState.isConnectedToServer ? "Connected to server" : "Not connected")
                    Spacer()
                    if appState.isLoading {
                        ProgressView()
                            .scaleEffect(0.8)
                    }
                }

                if let error = appState.connectionError {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }

            Section("Projects") {
                if appState.projects.isEmpty {
                    Text("No projects found")
                        .foregroundColor(.secondary)
                } else {
                    ForEach(appState.projects) { project in
                        Button {
                            Task {
                                await appState.selectProject(project)
                            }
                        } label: {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(project.name)
                                        .foregroundColor(.primary)
                                    Text(project.path)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                Spacer()
                                if appState.selectedProject?.id == project.id {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.accentColor)
                                }
                            }
                        }
                    }
                }
            }

            Section("About") {
                LabeledContent("Version", value: "1.0.0")
                LabeledContent("Build", value: "1")
            }
        }
    }

    private func testConnection() {
        isTesting = true
        testResult = nil

        Task {
            let result = await appState.testConnection()
            await MainActor.run {
                isTesting = false
                testSuccess = result.success
                testResult = result.message
            }
        }
    }
}

#Preview {
    iOSContentView()
        .environment(AppState())
}
