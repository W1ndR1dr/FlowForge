import Foundation

/// Client for reading refactor state from local filesystem
/// Reads directly from .forge/refactors/ directories (no API needed for macOS)
@MainActor
final class RefactorClient {

    // MARK: - Errors

    enum RefactorError: LocalizedError {
        case refactorNotFound(String)
        case invalidRefactorId(String)
        case parseError(String)

        var errorDescription: String? {
            switch self {
            case .refactorNotFound(let id):
                return "Refactor not found: \(id)"
            case .invalidRefactorId(let id):
                return "Invalid refactor ID: \(id)"
            case .parseError(let detail):
                return "Failed to parse refactor state: \(detail)"
            }
        }
    }

    // MARK: - Public API

    /// Fetch all refactors for a project
    /// - Parameter projectPath: Absolute path to project root
    /// - Returns: List of RefactorPlan objects
    func fetchRefactors(projectPath: String) async throws -> [RefactorPlan] {
        let projectURL = URL(fileURLWithPath: projectPath)
        let refactorsDir = projectURL.appendingPathComponent(".forge/refactors")

        // Check if refactors directory exists
        var isDirectory: ObjCBool = false
        guard FileManager.default.fileExists(atPath: refactorsDir.path, isDirectory: &isDirectory),
              isDirectory.boolValue else {
            // No refactors yet - return empty list (not an error)
            return []
        }

        // Scan for refactor subdirectories
        let contents = try FileManager.default.contentsOfDirectory(
            at: refactorsDir,
            includingPropertiesForKeys: [.isDirectoryKey],
            options: [.skipsHiddenFiles]
        )

        var refactors: [RefactorPlan] = []

        for url in contents {
            // Skip non-directories
            guard (try? url.resourceValues(forKeys: [.isDirectoryKey]).isDirectory) == true else {
                continue
            }

            // Try to load refactor from this directory
            if let plan = try? await loadRefactor(from: url) {
                refactors.append(plan)
            }
        }

        // Sort by updated_at (most recent first)
        return refactors.sorted { a, b in
            a.state.updatedAt > b.state.updatedAt
        }
    }

    /// Fetch a specific refactor by ID
    /// - Parameters:
    ///   - projectPath: Absolute path to project root
    ///   - refactorId: Refactor identifier
    /// - Returns: RefactorPlan if found
    func fetchRefactor(projectPath: String, refactorId: String) async throws -> RefactorPlan {
        // Sanitize refactorId to prevent path traversal
        guard !refactorId.contains("..") && !refactorId.contains("/") else {
            throw RefactorError.invalidRefactorId(refactorId)
        }

        let projectURL = URL(fileURLWithPath: projectPath)
        let refactorDir = projectURL.appendingPathComponent(".forge/refactors/\(refactorId)")

        guard FileManager.default.fileExists(atPath: refactorDir.path) else {
            throw RefactorError.refactorNotFound(refactorId)
        }

        return try await loadRefactor(from: refactorDir)
    }

    // MARK: - Private Helpers

    /// Load a refactor from its directory
    private func loadRefactor(from directory: URL) async throws -> RefactorPlan {
        let refactorId = directory.lastPathComponent
        let stateFile = directory.appendingPathComponent("state.json")

        // Load state.json
        let state: RefactorState
        if FileManager.default.fileExists(atPath: stateFile.path) {
            let data = try Data(contentsOf: stateFile)
            // Handle empty or malformed JSON gracefully
            if data.isEmpty {
                state = RefactorState(refactorId: refactorId)
            } else {
                do {
                    state = try JSONDecoder().decode(RefactorState.self, from: data)
                } catch {
                    throw RefactorError.parseError("state.json: \(error.localizedDescription)")
                }
            }
        } else {
            // No state.json yet - create empty state (planning phase)
            state = RefactorState(refactorId: refactorId)
        }

        // Try to extract title/description from CLAUDE.md or README.md
        let (title, description) = extractMetadata(from: directory, refactorId: refactorId)

        return RefactorPlan(
            id: refactorId,
            title: title,
            description: description,
            state: state,
            path: directory
        )
    }

    /// Extract title and description from metadata files
    private func extractMetadata(from directory: URL, refactorId: String) -> (title: String, description: String?) {
        // Try CLAUDE.md first (has session-level context)
        let claudeFile = directory.appendingPathComponent("CLAUDE.md")
        if let content = try? String(contentsOf: claudeFile, encoding: .utf8) {
            // Extract title from "# Execution Session: ..." or "# Planning Session: ..."
            if let titleMatch = content.range(of: "# (?:Execution|Planning) Session: (.+)", options: .regularExpression) {
                let titleLine = String(content[titleMatch])
                let title = titleLine
                    .replacingOccurrences(of: "# Execution Session: ", with: "")
                    .replacingOccurrences(of: "# Planning Session: ", with: "")
                    .trimmingCharacters(in: .whitespacesAndNewlines)

                // Extract description from "> **Goal**:" line
                var description: String?
                if let goalMatch = content.range(of: "> \\*\\*Goal\\*\\*: (.+)", options: .regularExpression) {
                    let goalLine = String(content[goalMatch])
                    description = goalLine
                        .replacingOccurrences(of: "> **Goal**: ", with: "")
                        .trimmingCharacters(in: .whitespacesAndNewlines)
                }

                return (title, description)
            }
        }

        // Fallback: convert refactorId to title
        let title = refactorId
            .replacingOccurrences(of: "-", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")

        return (title, nil)
    }
}

// MARK: - Project Extension

extension Project {
    /// Path to .forge/refactors directory
    var refactorsPath: String {
        path + "/.forge/refactors"
    }
}
