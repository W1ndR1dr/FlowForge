import SwiftUI

/// Platform-specific configuration
///
/// Architecture: Both iOS and macOS connect to Pi for brainstorming and sync.
/// Mac additionally has native execution capabilities (Claude Code, Xcode builds).
enum PlatformConfig {
    #if os(macOS)
    static let isMac = true
    static let isIOS = false
    /// Mac can run Claude Code locally for implementation
    static let canExecuteNatively = true
    #else
    static let isMac = false
    static let isIOS = true
    /// iOS can only brainstorm and track - execution happens on Mac
    static let canExecuteNatively = false
    #endif

    /// Tailscale hostname for the server (Raspberry Pi - single source of truth)
    static let tailscaleHostname = "raspberrypi"
    static let serverPort = 8081

    /// Default server URL - BOTH platforms connect to Pi for unified sync
    /// The Pi is the single source of truth for brainstorming and feature state.
    /// Mac's native execution capability is separate from the sync layer.
    static var defaultServerURL: String {
        // Both platforms connect to Pi via Tailscale
        return "http://\(tailscaleHostname):\(serverPort)"
    }

    /// Current server URL (may be overridden by user)
    static var currentServerURL: String {
        UserDefaults.standard.string(forKey: "serverURL") ?? defaultServerURL
    }

    /// Server URL (configurable)
    static var serverURL: URL {
        return URL(string: currentServerURL)!
    }

    /// Save custom server URL
    static func setServerURL(_ urlString: String) {
        UserDefaults.standard.set(urlString, forKey: "serverURL")
    }
}

/// Platform-specific color for text background
extension Color {
    static var textBackground: Color {
        #if os(macOS)
        return Color(NSColor.textBackgroundColor)
        #else
        return Color(UIColor.secondarySystemBackground)
        #endif
    }

    static var controlBackground: Color {
        #if os(macOS)
        return Color(NSColor.controlBackgroundColor)
        #else
        return Color(UIColor.systemBackground)
        #endif
    }

    static var windowBackground: Color {
        #if os(macOS)
        return Color(NSColor.windowBackgroundColor)
        #else
        return Color(UIColor.systemBackground)
        #endif
    }
}
