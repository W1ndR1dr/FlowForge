import Foundation
import Combine

/// WebSocket client for real-time brainstorming with Claude.
///
/// Connects to /ws/{project}/brainstorm and enables streaming chat.
/// This is the bridge between the app and the Claude CLI running on the Pi.
@MainActor
final class BrainstormClient: ObservableObject {
    // MARK: - Published State

    @Published private(set) var isConnected = false
    @Published private(set) var isTyping = false
    @Published private(set) var messages: [BrainstormMessage] = []
    @Published private(set) var currentSpec: RefinedSpec?
    @Published private(set) var lastError: Error?
    @Published private(set) var streamingText: String = ""  // Current streaming response (animated)
    @Published private(set) var displayedText: String = ""  // Text shown in UI (word-by-word animated)

    // MARK: - Types

    struct BrainstormMessage: Identifiable, Equatable {
        let id = UUID()
        let role: MessageRole
        var content: String
        let timestamp: Date

        enum MessageRole: String {
            case user
            case assistant
        }
    }

    struct RefinedSpec: Codable {
        let title: String
        let whatItDoes: String
        let howItWorks: [String]
        let complexity: String  // Trivial / Small / Medium / Large
        let rawSpec: String

        enum CodingKeys: String, CodingKey {
            case title
            case whatItDoes = "what_it_does"
            case howItWorks = "how_it_works"
            case complexity
            case rawSpec = "raw_spec"
        }
    }

    // MARK: - Private Properties

    private var webSocketTask: URLSessionWebSocketTask?
    private var pingTimer: Timer?
    private var responseTimeoutTask: Task<Void, Never>?  // Timeout for hung responses
    private var currentProject: String?
    private var currentFeatureId: String?
    private var currentFeatureTitle: String?
    private let session: URLSession
    private var currentAssistantMessage: BrainstormMessage?
    private var streamingBuffer: String = ""  // Accumulates chunks before publishing
    private var lastStreamUpdate: Date = .distantPast

    // Timeout duration for responses (2 minutes - Claude can take a while with web search)
    private let responseTimeout: TimeInterval = 120
    private var animationTask: Task<Void, Never>?
    private var wordsToAnimate: [String] = []
    private var animatedWordIndex: Int = 0

    // MARK: - Callbacks

    var onSpecReady: ((RefinedSpec) -> Void)?

    // MARK: - Lifecycle

    init() {
        let config = URLSessionConfiguration.default
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)
    }

    // MARK: - Connection

    /// Connect to brainstorm WebSocket for a project
    /// - Parameters:
    ///   - project: Project name
    ///   - featureId: Optional feature ID for refining mode
    ///   - featureTitle: Optional feature title for refining mode
    func connect(project: String, featureId: String? = nil, featureTitle: String? = nil) {
        if currentProject != nil {
            disconnect()
        }

        currentProject = project
        currentFeatureId = featureId
        currentFeatureTitle = featureTitle
        establishConnection()
    }

    /// Disconnect from WebSocket
    func disconnect() {
        pingTimer?.invalidate()
        pingTimer = nil
        responseTimeoutTask?.cancel()
        responseTimeoutTask = nil
        animationTask?.cancel()
        animationTask = nil

        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        currentProject = nil
        isConnected = false
        isTyping = false
    }

    /// Reset the brainstorm session (start fresh)
    func reset() {
        messages = []
        currentSpec = nil
        currentAssistantMessage = nil

        let message = #"{"type": "reset"}"#
        webSocketTask?.send(.string(message)) { _ in }
    }

    // MARK: - Messaging

    /// Send a message to Claude
    func sendMessage(_ content: String) {
        guard !content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }

        // Reset streaming state
        streamingBuffer = ""
        streamingText = ""
        displayedText = ""
        lastStreamUpdate = .distantPast
        currentAssistantMessage = nil
        animationTask?.cancel()
        animationTask = nil
        responseTimeoutTask?.cancel()
        responseTimeoutTask = nil

        // Add user message
        let userMessage = BrainstormMessage(
            role: .user,
            content: content,
            timestamp: Date()
        )
        messages.append(userMessage)

        // Don't add assistant placeholder yet - ThinkingIndicator shows during thinking
        // Assistant message will be created when first chunk arrives

        isTyping = true

        // Start response timeout
        startResponseTimeout()

        // Send to server
        let payload: [String: Any] = [
            "type": "message",
            "content": content
        ]

        if let data = try? JSONSerialization.data(withJSONObject: payload),
           let jsonString = String(data: data, encoding: .utf8) {
            webSocketTask?.send(.string(jsonString)) { [weak self] error in
                if let error = error {
                    Task { @MainActor in
                        self?.handleSendError(error)
                    }
                }
            }
        }
    }

    /// Start timeout timer for response
    private func startResponseTimeout() {
        responseTimeoutTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64((self?.responseTimeout ?? 120) * 1_000_000_000))
            guard !Task.isCancelled else { return }
            await MainActor.run {
                self?.handleResponseTimeout()
            }
        }
    }

    /// Handle response timeout - reset state and show error
    private func handleResponseTimeout() {
        guard isTyping else { return }  // Already got a response

        print("[BrainstormClient] Response timeout after \(responseTimeout)s")

        // Clean up state
        isTyping = false
        streamingBuffer = ""
        streamingText = ""
        displayedText = ""

        // If we had started an assistant message, finalize it with error
        if currentAssistantMessage != nil {
            finalizeStreamingMessage(streamingBuffer.isEmpty ? "Response timed out. Please try again." : streamingBuffer)
        } else {
            // Add error message
            let errorMessage = BrainstormMessage(
                role: .assistant,
                content: "⚠️ Response timed out. The server may be busy. Please try again.",
                timestamp: Date()
            )
            messages.append(errorMessage)
        }

        currentAssistantMessage = nil
        lastError = NSError(
            domain: "BrainstormClient",
            code: -2,
            userInfo: [NSLocalizedDescriptionKey: "Response timed out"]
        )
    }

    /// Handle send error
    private func handleSendError(_ error: Error) {
        lastError = error
        isTyping = false
        responseTimeoutTask?.cancel()
    }

    // MARK: - Private Methods

    private func establishConnection() {
        guard let project = currentProject else { return }

        let baseURL = PlatformConfig.defaultServerURL
        let wsURL = baseURL
            .replacingOccurrences(of: "http://", with: "ws://")
            .replacingOccurrences(of: "https://", with: "wss://")

        guard let url = URL(string: "\(wsURL)/ws/\(project)/brainstorm") else {
            lastError = URLError(.badURL)
            return
        }

        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()

        receiveMessage()
        startPingTimer()

        isConnected = true
        lastError = nil

        print("Brainstorm WebSocket connecting to: \(url)")

        // Send init message with feature context for refining mode
        sendInitMessage()
    }

    /// Send init message with feature context (for refining mode)
    private func sendInitMessage() {
        var payload: [String: Any] = ["type": "init"]

        if let featureId = currentFeatureId {
            payload["feature_id"] = featureId
        }
        if let featureTitle = currentFeatureTitle {
            payload["feature_title"] = featureTitle
        }

        if let data = try? JSONSerialization.data(withJSONObject: payload),
           let jsonString = String(data: data, encoding: .utf8) {
            webSocketTask?.send(.string(jsonString)) { _ in }
        }
    }

    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            Task { @MainActor in
                switch result {
                case .success(let message):
                    self?.handleMessage(message)
                    self?.receiveMessage()

                case .failure(let error):
                    self?.handleError(error)
                }
            }
        }
    }

    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            parseMessage(text)

        case .data(let data):
            if let text = String(data: data, encoding: .utf8) {
                parseMessage(text)
            }

        @unknown default:
            break
        }
    }

    private func parseMessage(_ text: String) {
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else {
            return
        }

        switch type {
        case "pong":
            break

        case "session_state":
            // Restore session state if reconnecting
            if let state = json["state"] as? [String: Any],
               let messageList = state["messages"] as? [[String: String]] {
                messages = messageList.compactMap { msg in
                    guard let role = msg["role"],
                          let content = msg["content"],
                          let messageRole = BrainstormMessage.MessageRole(rawValue: role) else {
                        return nil
                    }
                    return BrainstormMessage(role: messageRole, content: content, timestamp: Date())
                }
            }

        case "chunk":
            // Streaming chunk - accumulate and animate word-by-word
            if let content = json["content"] as? String {
                // Cancel timeout on first chunk - we're getting data
                responseTimeoutTask?.cancel()
                responseTimeoutTask = nil

                // Create assistant message on first chunk (replaces ThinkingIndicator)
                if currentAssistantMessage == nil {
                    currentAssistantMessage = BrainstormMessage(
                        role: .assistant,
                        content: "",
                        timestamp: Date()
                    )
                    messages.append(currentAssistantMessage!)
                }

                streamingBuffer += content
                streamingText = streamingBuffer

                // Animate the text word-by-word for polished feel
                animateStreamingText(streamingBuffer)
            }

        case "message_complete":
            // Cancel timeout
            responseTimeoutTask?.cancel()
            responseTimeoutTask = nil

            // Full message received - finalize with complete content
            let finalContent = json["content"] as? String ?? streamingBuffer
            if !finalContent.isEmpty {
                finalizeStreamingMessage(finalContent)
            }
            // Stop animation and reset streaming state
            finishAnimation(with: "")
            streamingBuffer = ""
            displayedText = ""
            isTyping = false
            currentAssistantMessage = nil

        case "spec_ready":
            // Spec is ready!
            if let specData = json["spec"] as? [String: Any],
               let jsonData = try? JSONSerialization.data(withJSONObject: specData),
               let spec = try? JSONDecoder().decode(RefinedSpec.self, from: jsonData) {
                currentSpec = spec
                onSpecReady?(spec)
            }

        case "session_reset":
            messages = []
            currentSpec = nil
            currentAssistantMessage = nil

        case "status":
            // Processing status from server - show typing indicator immediately
            if let status = json["status"] as? String, status == "processing" {
                isTyping = true
            }

        case "error":
            if let errorMessage = json["message"] as? String {
                lastError = NSError(domain: "BrainstormClient", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])
            }
            isTyping = false

        default:
            print("Unknown brainstorm message type: \(type)")
        }
    }

    private func finalizeStreamingMessage(_ content: String) {
        guard var message = currentAssistantMessage else { return }
        message.content = content

        // Update the message in the array (single update, not per-chunk)
        if let index = messages.lastIndex(where: { $0.id == message.id }) {
            messages[index] = message
        }
    }

    private func handleError(_ error: Error) {
        isConnected = false
        lastError = error
        isTyping = false
        responseTimeoutTask?.cancel()
        responseTimeoutTask = nil
        animationTask?.cancel()
        animationTask = nil

        print("Brainstorm WebSocket error: \(error.localizedDescription)")

        // Try to reconnect after a delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
            guard self?.currentProject != nil else { return }
            self?.establishConnection()
        }
    }

    private func startPingTimer() {
        pingTimer?.invalidate()
        pingTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.sendPing()
            }
        }
    }

    private func sendPing() {
        let pingMessage = #"{"type": "ping"}"#
        webSocketTask?.send(.string(pingMessage)) { _ in }
    }

    // MARK: - Text Animation

    // Thresholds for animation behavior
    private let maxWordsForAnimation = 300  // Skip word animation for long messages
    private let animationWordDelay: UInt64 = 50_000_000  // 50ms between words

    /// Animate text appearing word-by-word for a polished streaming feel.
    /// For long messages, falls back to immediate display to avoid performance issues.
    private func animateStreamingText(_ newText: String) {
        // Cancel any existing animation
        animationTask?.cancel()

        let currentLength = displayedText.count
        let newLength = newText.count

        // If we're already showing this text or more, just update
        guard newLength > currentLength else {
            displayedText = newText
            return
        }

        // For very long messages, skip word animation entirely
        // (counting words is expensive, use character heuristic: ~5 chars/word)
        if newLength > maxWordsForAnimation * 5 {
            displayedText = newText
            return
        }

        // Find word boundary to animate to
        let newContent = String(newText.dropFirst(currentLength))
        let newWords = newContent.split(separator: " ", omittingEmptySubsequences: false)

        // If only 1-2 new words, animate them
        guard newWords.count > 0 else {
            displayedText = newText
            return
        }

        animationTask = Task { @MainActor in
            var currentText = displayedText

            for word in newWords {
                guard !Task.isCancelled else { return }

                // Append word with space
                if !currentText.isEmpty && !currentText.hasSuffix(" ") {
                    currentText += " "
                }
                currentText += word

                displayedText = currentText

                // Brief delay for streaming feel
                try? await Task.sleep(nanoseconds: animationWordDelay)
            }

            // Ensure we show the complete text
            if !Task.isCancelled {
                displayedText = newText
            }
        }
    }

    /// Stop animation and show all text immediately
    private func finishAnimation(with finalText: String) {
        animationTask?.cancel()
        animationTask = nil
        displayedText = finalText
        streamingText = finalText
    }
}
