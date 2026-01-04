import Foundation
import UserNotifications

// MARK: - Notification Manager
/// Handles macOS system notifications for refactor events.
/// Calm by design - informational, not alarming.

@MainActor
final class NotificationManager: ObservableObject {
    static let shared = NotificationManager()

    @Published private(set) var isAuthorized = false

    private init() {
        Task {
            await checkAuthorizationStatus()
        }
    }

    // MARK: - Authorization

    /// Check current authorization status
    func checkAuthorizationStatus() async {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        isAuthorized = settings.authorizationStatus == .authorized
    }

    /// Request notification permission
    /// Returns true if authorized
    @discardableResult
    func requestPermission() async -> Bool {
        do {
            let granted = try await UNUserNotificationCenter.current().requestAuthorization(
                options: [.alert, .sound, .badge]
            )
            isAuthorized = granted
            return granted
        } catch {
            print("[NotificationManager] Permission request failed: \(error)")
            return false
        }
    }

    // MARK: - Notification Categories

    enum Category: String {
        case phaseStarted = "PHASE_STARTED"
        case phaseComplete = "PHASE_COMPLETE"
        case auditPassed = "AUDIT_PASSED"
        case auditFailed = "AUDIT_FAILED"
        case needsAttention = "NEEDS_ATTENTION"

        var soundEnabled: Bool {
            switch self {
            case .phaseStarted, .phaseComplete:
                return false  // Silent for routine events
            case .auditPassed, .auditFailed, .needsAttention:
                return true   // Sound for events needing attention
            }
        }
    }

    // MARK: - Send Notifications

    /// Send a system notification
    /// - Parameters:
    ///   - title: Notification title (keep short)
    ///   - body: Notification body (informational, not alarming)
    ///   - category: Notification category for grouping
    func notify(
        title: String,
        body: String,
        category: Category
    ) {
        guard isAuthorized else {
            print("[NotificationManager] Not authorized, skipping notification")
            return
        }

        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.categoryIdentifier = category.rawValue

        if category.soundEnabled {
            content.sound = .default
        }

        // Unique identifier based on timestamp
        let identifier = "\(category.rawValue)_\(Date().timeIntervalSince1970)"

        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: nil  // Deliver immediately
        )

        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("[NotificationManager] Failed to send notification: \(error)")
            }
        }
    }

    // MARK: - Convenience Methods

    /// Notify that a session has started
    func notifySessionStarted(sessionId: String, refactorName: String) {
        notify(
            title: "Session \(sessionId) starting",
            body: refactorName,
            category: .phaseStarted
        )
    }

    /// Notify that a session is ready for review
    func notifySessionComplete(sessionId: String, refactorName: String) {
        notify(
            title: "Session \(sessionId) ready for review",
            body: refactorName,
            category: .phaseComplete
        )
    }

    /// Notify that audit passed
    func notifyAuditPassed(sessionId: String, refactorName: String) {
        notify(
            title: "Session \(sessionId) passed audit",
            body: refactorName,
            category: .auditPassed
        )
    }

    /// Notify that audit failed and needs revision
    func notifyAuditFailed(sessionId: String, refactorName: String) {
        notify(
            title: "Session \(sessionId) needs revision",
            body: "Review audit feedback in \(refactorName)",
            category: .auditFailed
        )
    }

    /// Notify that the refactor needs attention (paused, decision needed)
    func notifyNeedsAttention(refactorName: String, reason: String) {
        notify(
            title: "Refactor paused",
            body: reason,
            category: .needsAttention
        )
    }
}
