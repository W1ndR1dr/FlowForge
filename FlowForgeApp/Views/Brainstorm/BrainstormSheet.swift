import SwiftUI

/// Sheet for importing brainstorm output from Claude
/// Vibecoder-friendly: Just paste and go!
struct BrainstormSheet: View {
    @Environment(AppState.self) private var appState
    @Environment(\.dismiss) private var dismiss

    @State private var claudeOutput = ""
    @State private var isParsing = false
    @State private var parseError: String?

    var body: some View {
        VStack(spacing: Spacing.large) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: Spacing.micro) {
                    Text("Import Ideas from Claude")
                        .font(Typography.featureTitle)
                    Text("Paste Claude's brainstorm output below")
                        .font(Typography.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button("Cancel") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
            }

            // Instructions
            instructionsView

            // Paste area
            TextEditor(text: $claudeOutput)
                .font(.system(.body, design: .monospaced))
                .frame(minHeight: 200)
                .scrollContentBackground(.hidden)
                .padding(Spacing.small)
                .background(Surface.elevated)
                .cornerRadius(CornerRadius.medium)
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.secondary.opacity(0.2), lineWidth: 1)
                )

            // Error message
            if let error = parseError {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(Accent.warning)
                    Text(error)
                        .font(Typography.caption)
                        .foregroundColor(Accent.warning)
                }
                .padding(Spacing.small)
                .background(Accent.warning.opacity(0.1))
                .cornerRadius(CornerRadius.small)
            }

            // Actions
            HStack {
                Button("Paste from Clipboard") {
                    pasteFromClipboard()
                }
                .buttonStyle(.bordered)

                Spacer()

                Button(action: parseOutput) {
                    if isParsing {
                        ProgressView()
                            .scaleEffect(0.8)
                            .frame(width: 16, height: 16)
                    } else {
                        Text("Parse & Review")
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(claudeOutput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isParsing)
            }
        }
        .padding(Spacing.large)
        .frame(minWidth: 500, minHeight: 400)
    }

    // MARK: - Instructions

    private var instructionsView: some View {
        VStack(alignment: .leading, spacing: Spacing.small) {
            Text("How to brainstorm with Claude:")
                .font(Typography.caption)
                .fontWeight(.semibold)

            VStack(alignment: .leading, spacing: Spacing.micro) {
                instructionRow("1", "Ask Claude to brainstorm features for your project")
                instructionRow("2", "Claude will list ideas with titles and descriptions")
                instructionRow("3", "Copy the entire response and paste it here")
                instructionRow("4", "Review and approve the ones you want to build")
            }
        }
        .padding(Spacing.medium)
        .background(Accent.primary.opacity(0.05))
        .cornerRadius(CornerRadius.medium)
    }

    private func instructionRow(_ number: String, _ text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.small) {
            Text(number)
                .font(Typography.caption)
                .fontWeight(.bold)
                .foregroundColor(Accent.primary)
                .frame(width: 16)

            Text(text)
                .font(Typography.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Actions

    private func pasteFromClipboard() {
        #if os(macOS)
        if let string = NSPasteboard.general.string(forType: .string) {
            claudeOutput = string
        }
        #else
        if let string = UIPasteboard.general.string {
            claudeOutput = string
        }
        #endif
    }

    private func parseOutput() {
        isParsing = true
        parseError = nil

        Task {
            do {
                try await appState.parseBrainstorm(claudeOutput: claudeOutput)

                await MainActor.run {
                    isParsing = false
                    dismiss()
                    // AppState.showingProposalReview will be set to true by parseBrainstorm
                }
            } catch {
                await MainActor.run {
                    isParsing = false
                    parseError = "Couldn't find any feature ideas in that text. Make sure Claude's response includes feature titles."
                }
            }
        }
    }
}

#if DEBUG
#Preview {
    BrainstormSheet()
        .environment(AppState())
        .frame(width: 600, height: 500)
}
#endif
