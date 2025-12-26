import SwiftUI

// MARK: - Settings View
// macOS standard preferences window
// Vibecoder-friendly: Simple, clear options

struct SettingsView: View {
    var body: some View {
        TabView {
            GeneralSettingsTab()
                .tabItem {
                    Label("General", systemImage: "gear")
                }

            ConnectionSettingsTab()
                .tabItem {
                    Label("Connection", systemImage: "network")
                }
        }
        .frame(width: 500, height: 300)
    }
}

// MARK: - General Settings Tab

struct GeneralSettingsTab: View {
    @AppStorage("showParallelBadges") private var showParallelBadges = true
    @AppStorage("playSounds") private var playSounds = false

    var body: some View {
        Form {
            Section {
                Toggle("Show \"parallel ok\" badges", isOn: $showParallelBadges)
                    .help("Show badges on features that are safe to work on in parallel")

                Toggle("Play sounds on ship", isOn: $playSounds)
                    .help("Play a celebration sound when you ship a feature")
            } header: {
                Text("Display")
            }

            Section {
                Text("FlowForge helps you ship features faster by managing the complexity of parallel development. Just focus on what you want to build!")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } header: {
                Text("About")
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

// MARK: - Connection Settings Tab

struct ConnectionSettingsTab: View {
    @Environment(AppState.self) private var appState
    @State private var serverURL: String = PlatformConfig.defaultServerURL
    @State private var isTestingConnection = false
    @State private var connectionResult: ConnectionTestResult?

    /// Normalized URL preview (what will actually be used)
    private var normalizedURL: String {
        PlatformConfig.normalizeServerURL(serverURL)
    }

    /// Show preview if input differs from normalized
    private var showNormalizedPreview: Bool {
        !serverURL.isEmpty && serverURL != normalizedURL
    }

    var body: some View {
        Form {
            Section {
                HStack {
                    TextField("hostname or IP", text: $serverURL)
                        .textFieldStyle(.roundedBorder)

                    Button("Test") {
                        testConnection()
                    }
                    .disabled(isTestingConnection)
                }

                // Show normalized URL preview if different from input
                if showNormalizedPreview {
                    HStack(spacing: Spacing.small) {
                        Image(systemName: "arrow.right.circle")
                            .foregroundColor(.secondary)
                        Text(normalizedURL)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                // Connection status
                HStack(spacing: Spacing.small) {
                    Circle()
                        .fill(statusColor)
                        .frame(width: 8, height: 8)

                    Text(statusMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Spacer()
                }

                // Test result
                if let result = connectionResult {
                    HStack(spacing: Spacing.small) {
                        Image(systemName: result.success ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .foregroundColor(result.success ? Accent.success : Accent.danger)

                        Text(result.message)
                            .font(.caption)
                            .foregroundColor(result.success ? Accent.success : Accent.danger)
                    }
                    .padding(.vertical, Spacing.small)
                }
            } header: {
                Text("FlowForge Server")
            } footer: {
                Text("Just enter hostname (e.g., \"raspberrypi\") — http:// and port added automatically")
                    .font(.caption2)
            }

            Section {
                Button("Apply Changes") {
                    applyChanges()
                }
                .buttonStyle(.borderedProminent)
                .disabled(normalizedURL == PlatformConfig.currentServerURL)
            }

            Section {
                VStack(alignment: .leading, spacing: Spacing.small) {
                    Text("The FlowForge server handles:")
                        .font(.caption)
                        .fontWeight(.medium)

                    VStack(alignment: .leading, spacing: 2) {
                        bulletPoint("Git worktree management")
                        bulletPoint("Feature analysis & intelligence")
                        bulletPoint("Merge operations")
                        bulletPoint("Real-time sync via WebSocket")
                    }
                }
                .foregroundColor(.secondary)
            } header: {
                Text("Info")
            }
        }
        .formStyle(.grouped)
        .padding()
        .onAppear {
            serverURL = PlatformConfig.currentServerURL
        }
    }

    private var statusColor: Color {
        if isTestingConnection {
            return .orange
        }
        return appState.isConnectedToServer ? Accent.success : Accent.danger
    }

    private var statusMessage: String {
        if isTestingConnection {
            return "Testing connection..."
        }
        return appState.isConnectedToServer ? "Connected" : "Not connected"
    }

    private func bulletPoint(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 4) {
            Text("•")
            Text(text)
        }
        .font(.caption)
    }

    private func testConnection() {
        isTestingConnection = true
        connectionResult = nil

        Task {
            // Test using the normalized URL
            let result = await appState.testConnection(url: normalizedURL)
            await MainActor.run {
                connectionResult = ConnectionTestResult(
                    success: result.success,
                    message: result.message
                )
                isTestingConnection = false
            }
        }
    }

    private func applyChanges() {
        // Apply the normalized URL
        let normalized = normalizedURL
        appState.updateServerURL(normalized)
        PlatformConfig.setServerURL(normalized)
        // Update display to show normalized
        serverURL = normalized
    }
}

struct ConnectionTestResult {
    let success: Bool
    let message: String
}


// MARK: - Preview

#if DEBUG
#Preview {
    SettingsView()
        .environment(AppState())
}
#endif
