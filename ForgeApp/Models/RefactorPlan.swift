import Foundation

// MARK: - Refactor Status Enums

/// Status of an overall refactor
enum RefactorStatus: String, Codable, CaseIterable {
    case planning = "planning"
    case executing = "executing"
    case paused = "paused"
    case completed = "completed"

    var displayName: String {
        switch self {
        case .planning: return "Planning"
        case .executing: return "Executing"
        case .paused: return "Paused"
        case .completed: return "Completed"
        }
    }

    var color: String {
        switch self {
        case .planning: return "purple"
        case .executing: return "blue"
        case .paused: return "orange"
        case .completed: return "green"
        }
    }
}

/// Status of a single execution session
enum SessionStatus: String, Codable, CaseIterable {
    case pending = "pending"
    case inProgress = "in_progress"
    case completed = "completed"
    case needsRevision = "needs_revision"

    var displayName: String {
        switch self {
        case .pending: return "Pending"
        case .inProgress: return "In Progress"
        case .completed: return "Completed"
        case .needsRevision: return "Needs Revision"
        }
    }
}

/// Result of an audit review
enum AuditResult: String, Codable {
    case pending = "pending"
    case passed = "passed"
    case failed = "failed"
}

// MARK: - Refactor Session State

/// State for a single execution session in a refactor
struct RefactorSessionState: Identifiable, Codable, Hashable {
    let sessionId: String
    var status: SessionStatus
    var startedAt: String?
    var completedAt: String?
    var startCommit: String?
    var commitHash: String?
    var auditResult: AuditResult
    var notes: String
    var iterationCount: Int

    var id: String { sessionId }

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case status
        case startedAt = "started_at"
        case completedAt = "completed_at"
        case startCommit = "start_commit"
        case commitHash = "commit_hash"
        case auditResult = "audit_result"
        case notes
        case iterationCount = "iteration_count"
    }

    init(
        sessionId: String,
        status: SessionStatus = .pending,
        startedAt: String? = nil,
        completedAt: String? = nil,
        startCommit: String? = nil,
        commitHash: String? = nil,
        auditResult: AuditResult = .pending,
        notes: String = "",
        iterationCount: Int = 0
    ) {
        self.sessionId = sessionId
        self.status = status
        self.startedAt = startedAt
        self.completedAt = completedAt
        self.startCommit = startCommit
        self.commitHash = commitHash
        self.auditResult = auditResult
        self.notes = notes
        self.iterationCount = iterationCount
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        sessionId = try container.decode(String.self, forKey: .sessionId)

        // Handle status string → enum
        let statusString = try container.decodeIfPresent(String.self, forKey: .status) ?? "pending"
        status = SessionStatus(rawValue: statusString) ?? .pending

        startedAt = try container.decodeIfPresent(String.self, forKey: .startedAt)
        completedAt = try container.decodeIfPresent(String.self, forKey: .completedAt)
        startCommit = try container.decodeIfPresent(String.self, forKey: .startCommit)
        commitHash = try container.decodeIfPresent(String.self, forKey: .commitHash)

        let auditString = try container.decodeIfPresent(String.self, forKey: .auditResult) ?? "pending"
        auditResult = AuditResult(rawValue: auditString) ?? .pending

        notes = try container.decodeIfPresent(String.self, forKey: .notes) ?? ""
        iterationCount = try container.decodeIfPresent(Int.self, forKey: .iterationCount) ?? 0
    }
}

// MARK: - State Change (Audit Log)

/// A single state change entry for the audit log
struct StateChange: Codable {
    let timestamp: String
    let action: String
    let details: [String: String]

    init(timestamp: String, action: String, details: [String: String] = [:]) {
        self.timestamp = timestamp
        self.action = action
        self.details = details
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        timestamp = try container.decode(String.self, forKey: .timestamp)
        action = try container.decode(String.self, forKey: .action)

        // Details can be complex, simplify to string dictionary
        if let details = try? container.decode([String: String].self, forKey: .details) {
            self.details = details
        } else {
            self.details = [:]
        }
    }

    enum CodingKeys: String, CodingKey {
        case timestamp
        case action
        case details
    }
}

// MARK: - Refactor State

/// Runtime state for a refactor execution
/// Stored at: .forge/refactors/{id}/state.json
struct RefactorState: Identifiable, Codable {
    let refactorId: String
    var status: RefactorStatus
    var currentSession: String?
    var sessions: [String: RefactorSessionState]
    var startedAt: String?
    var updatedAt: String
    var completedAt: String?
    var history: [StateChange]

    var id: String { refactorId }

    enum CodingKeys: String, CodingKey {
        case refactorId = "refactor_id"
        case status
        case currentSession = "current_session"
        case sessions
        case startedAt = "started_at"
        case updatedAt = "updated_at"
        case completedAt = "completed_at"
        case history
    }

    init(
        refactorId: String,
        status: RefactorStatus = .planning,
        currentSession: String? = nil,
        sessions: [String: RefactorSessionState] = [:],
        startedAt: String? = nil,
        updatedAt: String = ISO8601DateFormatter().string(from: Date()),
        completedAt: String? = nil,
        history: [StateChange] = []
    ) {
        self.refactorId = refactorId
        self.status = status
        self.currentSession = currentSession
        self.sessions = sessions
        self.startedAt = startedAt
        self.updatedAt = updatedAt
        self.completedAt = completedAt
        self.history = history
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        refactorId = try container.decode(String.self, forKey: .refactorId)

        let statusString = try container.decodeIfPresent(String.self, forKey: .status) ?? "planning"
        status = RefactorStatus(rawValue: statusString) ?? .planning

        currentSession = try container.decodeIfPresent(String.self, forKey: .currentSession)

        // Sessions is a dictionary
        sessions = try container.decodeIfPresent([String: RefactorSessionState].self, forKey: .sessions) ?? [:]

        startedAt = try container.decodeIfPresent(String.self, forKey: .startedAt)
        updatedAt = try container.decodeIfPresent(String.self, forKey: .updatedAt)
            ?? ISO8601DateFormatter().string(from: Date())
        completedAt = try container.decodeIfPresent(String.self, forKey: .completedAt)
        history = try container.decodeIfPresent([StateChange].self, forKey: .history) ?? []
    }

    // MARK: - Computed Properties

    /// Sessions sorted by ID (e.g., "1.1", "1.2", "2.1")
    var sortedSessions: [RefactorSessionState] {
        sessions.values.sorted { a, b in
            // Parse "1.1", "2.1" etc. for proper ordering
            let partsA = a.sessionId.split(separator: ".").compactMap { Int($0) }
            let partsB = b.sessionId.split(separator: ".").compactMap { Int($0) }

            // Compare phase first, then session number
            for (pa, pb) in zip(partsA, partsB) {
                if pa != pb { return pa < pb }
            }
            return partsA.count < partsB.count
        }
    }

    /// Completed sessions count
    var completedCount: Int {
        sessions.values.filter { $0.status == .completed }.count
    }

    /// Total sessions count
    var totalCount: Int {
        sessions.count
    }

    /// Progress as fraction (0.0 to 1.0)
    var progress: Double {
        guard totalCount > 0 else { return 0 }
        return Double(completedCount) / Double(totalCount)
    }

    /// Whether all sessions are completed
    var isComplete: Bool {
        guard !sessions.isEmpty else { return false }
        return sessions.values.allSatisfy { $0.status == .completed }
    }

    /// Pending sessions
    var pendingSessions: [RefactorSessionState] {
        sortedSessions.filter { $0.status == .pending }
    }

    /// Current session state (if any)
    var currentSessionState: RefactorSessionState? {
        guard let id = currentSession else { return nil }
        return sessions[id]
    }
}

// MARK: - Refactor Plan (UI-Friendly Wrapper)

/// High-level refactor plan with metadata from docs
/// Combines state.json with metadata from CLAUDE.md/README.md
struct RefactorPlan: Identifiable {
    let id: String
    let title: String
    let description: String?
    let state: RefactorState
    let path: URL

    /// Display title (human-readable)
    var displayTitle: String {
        title.replacingOccurrences(of: "-", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")
    }

    /// Status badge color
    var statusColor: String {
        state.status.color
    }

    /// Progress percentage (0-100)
    var progressPercent: Int {
        Int(state.progress * 100)
    }
}
