import SwiftUI

// MARK: - Connection Status Bar
// Shows server connection state clearly at the top of the app.
// Visible when disconnected/connecting, fades when connected.

struct ConnectionStatusBar: View {
    enum ConnectionState {
        case disconnected
        case connecting
        case connected

        var color: Color {
            switch self {
            case .disconnected: return Accent.danger
            case .connecting: return Accent.warning
            case .connected: return Accent.success
            }
        }

        var backgroundColor: Color {
            switch self {
            case .disconnected: return Accent.danger.opacity(0.15)
            case .connecting: return Accent.warning.opacity(0.15)
            case .connected: return Accent.success.opacity(0.15)
            }
        }

        var message: String {
            switch self {
            case .disconnected: return "Server disconnected"
            case .connecting: return "Connecting..."
            case .connected: return "Connected"
            }
        }

        var icon: String {
            switch self {
            case .disconnected: return "wifi.slash"
            case .connecting: return "wifi"
            case .connected: return "checkmark.circle.fill"
            }
        }
    }

    let state: ConnectionState
    var serverURL: String = ""

    @State private var isVisible = true
    @State private var didAppear = false

    var body: some View {
        if shouldShow {
            HStack(spacing: Spacing.small) {
                // Status icon
                if state == .connecting {
                    ProgressView()
                        .scaleEffect(0.6)
                        .frame(width: 14, height: 14)
                } else {
                    Image(systemName: state.icon)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(state.color)
                }

                // Message
                Text(state.message)
                    .font(Typography.caption)
                    .foregroundColor(state.color)

                // Server URL (if disconnected)
                if state == .disconnected && !serverURL.isEmpty {
                    Text("·")
                        .foregroundColor(.secondary)
                    Text(serverURL)
                        .font(Typography.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, Spacing.medium)
            .padding(.vertical, Spacing.small)
            .background(state.backgroundColor)
            .cornerRadius(CornerRadius.medium)
            .transition(.move(edge: .top).combined(with: .opacity))
            .onAppear {
                didAppear = true
                scheduleHideIfConnected()
            }
            .onChange(of: state) { _, newState in
                withAnimation(SpringPreset.snappy) {
                    isVisible = true
                }
                scheduleHideIfConnected()
            }
        }
    }

    private var shouldShow: Bool {
        switch state {
        case .disconnected, .connecting:
            return true
        case .connected:
            return isVisible && didAppear
        }
    }

    private func scheduleHideIfConnected() {
        guard state == .connected else { return }

        // Fade out after 2 seconds when connected
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            withAnimation(SpringPreset.smooth) {
                isVisible = false
            }
        }
    }
}

// MARK: - Preview

#if DEBUG
struct ConnectionStatusBarPreview: View {
    @State private var state: ConnectionStatusBar.ConnectionState = .disconnected

    var body: some View {
        VStack(spacing: Spacing.xl) {
            Text("CONNECTION STATUS BAR")
                .sectionHeaderStyle()

            // States
            VStack(spacing: Spacing.medium) {
                ConnectionStatusBar(state: .disconnected, serverURL: "raspberrypi:8081")
                ConnectionStatusBar(state: .connecting)
                ConnectionStatusBar(state: .connected)
            }

            Divider()

            // Interactive
            VStack(spacing: Spacing.medium) {
                ConnectionStatusBar(state: state, serverURL: "raspberrypi:8081")

                HStack {
                    Button("Disconnected") { state = .disconnected }
                    Button("Connecting") { state = .connecting }
                    Button("Connected") { state = .connected }
                }
            }
        }
        .padding(Spacing.large)
        .frame(width: 500, height: 400)
        .background(Surface.window)
    }
}

#Preview {
    ConnectionStatusBarPreview()
}
#endif
