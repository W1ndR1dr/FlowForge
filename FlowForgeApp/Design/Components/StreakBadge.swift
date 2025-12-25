import SwiftUI

// MARK: - Streak Badge
// The motivational element — shipping streak with celebration
//
// Influenced by: Mike Matas (magical moments), Julie Zhuo (emotional design)
// "Shipping should feel good"

struct StreakBadge: View {
    let currentStreak: Int
    let longestStreak: Int
    let totalShipped: Int
    let showDetails: Bool

    @State private var isAnimating = false
    @State private var showingMilestone = false
    @State private var displayedStreak: Int = 0

    init(
        currentStreak: Int,
        longestStreak: Int = 0,
        totalShipped: Int = 0,
        showDetails: Bool = true
    ) {
        self.currentStreak = currentStreak
        self.longestStreak = longestStreak
        self.totalShipped = totalShipped
        self.showDetails = showDetails
    }

    private var streakEmoji: String {
        switch currentStreak {
        case 0: return ""
        case 1...2: return "🔥"
        case 3...6: return "🔥"
        case 7...13: return "🔥"
        case 14...29: return "🔥"
        case 30...: return "🔥"
        default: return "🔥"
        }
    }

    private var streakIntensity: Double {
        // Intensity increases with streak length
        switch currentStreak {
        case 0: return 0
        case 1...2: return 0.6
        case 3...6: return 0.8
        case 7...13: return 1.0
        case 14...29: return 1.2
        case 30...: return 1.5
        default: return 0.6
        }
    }

    private var isMilestone: Bool {
        [7, 14, 30, 50, 100].contains(currentStreak)
    }

    var body: some View {
        HStack(spacing: Spacing.small) {
            // Fire emoji with pulse
            if currentStreak > 0 {
                Text(streakEmoji)
                    .font(.system(size: 20))
                    .scaleEffect(isAnimating ? 1.1 * streakIntensity : 1.0)
                    .animation(
                        Animation
                            .easeInOut(duration: 0.8)
                            .repeatForever(autoreverses: true),
                        value: isAnimating
                    )
            }

            // Streak number with spring animation
            VStack(alignment: .leading, spacing: 2) {
                HStack(alignment: .firstTextBaseline, spacing: Spacing.micro) {
                    Text("\(displayedStreak)")
                        .font(Typography.streakNumber)
                        .foregroundColor(currentStreak > 0 ? Accent.streak : .secondary)
                        .contentTransition(.numericText(value: Double(displayedStreak)))

                    Text(currentStreak == 1 ? "day" : "days")
                        .font(Typography.caption)
                        .foregroundColor(.secondary)
                }

                if showDetails && totalShipped > 0 {
                    Text("\(totalShipped) shipped")
                        .font(Typography.caption)
                        .foregroundColor(.secondary.opacity(0.8))
                }
            }

            // Best streak indicator
            if showDetails && longestStreak > currentStreak {
                Divider()
                    .frame(height: 24)

                VStack(alignment: .leading, spacing: 2) {
                    Text("Best")
                        .font(.system(size: 10))
                        .foregroundColor(.secondary.opacity(0.6))

                    Text("\(longestStreak)")
                        .font(Typography.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.horizontal, Spacing.standard)
        .padding(.vertical, Spacing.medium)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Accent.streak.opacity(currentStreak > 0 ? 0.1 : 0.05))
        )
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Accent.streak.opacity(currentStreak > 0 ? 0.2 : 0), lineWidth: 1)
        )
        .onAppear {
            isAnimating = currentStreak > 0
            withAnimation(SpringPreset.bouncy) {
                displayedStreak = currentStreak
            }
        }
        .onChange(of: currentStreak) { oldValue, newValue in
            // Animate the number change
            withAnimation(SpringPreset.celebration) {
                displayedStreak = newValue
            }

            // Check for milestone
            if newValue > oldValue && isMilestone {
                triggerMilestoneAnimation()
            }
        }
    }

    private func triggerMilestoneAnimation() {
        // This would trigger confetti or other celebration
        showingMilestone = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            showingMilestone = false
        }
    }
}

// MARK: - Compact Streak Badge
// For tight spaces — just the essential info

struct CompactStreakBadge: View {
    let currentStreak: Int

    var body: some View {
        HStack(spacing: Spacing.micro) {
            if currentStreak > 0 {
                Text("🔥")
                    .font(.system(size: 14))
            }

            Text("\(currentStreak)")
                .font(Typography.badge)
                .fontWeight(.bold)
                .foregroundColor(currentStreak > 0 ? Accent.streak : .secondary)
        }
        .padding(.horizontal, Spacing.small)
        .padding(.vertical, Spacing.micro)
        .background(Accent.streak.opacity(currentStreak > 0 ? 0.15 : 0.05))
        .cornerRadius(CornerRadius.small)
    }
}

// MARK: - Streak Milestone Banner
// Shows when user hits a milestone

struct StreakMilestoneBanner: View {
    let milestone: Int
    let onDismiss: () -> Void

    @State private var isVisible = false

    private var milestoneMessage: String {
        switch milestone {
        case 7: return "One week streak! You're building momentum."
        case 14: return "Two weeks! You're a shipping machine."
        case 30: return "30 days! Legendary shipper status."
        case 50: return "50 days! Unstoppable."
        case 100: return "100 DAYS! You are a force of nature."
        default: return "\(milestone) day streak!"
        }
    }

    private var milestoneEmoji: String {
        switch milestone {
        case 7: return "🌟"
        case 14: return "⭐"
        case 30: return "🏆"
        case 50: return "👑"
        case 100: return "🚀"
        default: return "🔥"
        }
    }

    var body: some View {
        HStack(spacing: Spacing.medium) {
            Text(milestoneEmoji)
                .font(.system(size: 32))
                .scaleEffect(isVisible ? 1.0 : 0.5)

            VStack(alignment: .leading, spacing: Spacing.micro) {
                Text("\(milestone) Day Streak!")
                    .font(Typography.featureTitle)
                    .foregroundColor(.primary)

                Text(milestoneMessage)
                    .font(Typography.body)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill")
                    .foregroundColor(.secondary)
            }
            .buttonStyle(.plain)
        }
        .padding(Spacing.standard)
        .background(
            LinearGradient(
                colors: [Accent.streak.opacity(0.2), Accent.success.opacity(0.1)],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Accent.streak.opacity(0.3), lineWidth: 1)
        )
        .scaleEffect(isVisible ? 1.0 : 0.9)
        .opacity(isVisible ? 1.0 : 0)
        .onAppear {
            withAnimation(SpringPreset.celebration) {
                isVisible = true
            }
        }
    }
}

// MARK: - Preview

#if DEBUG
struct StreakBadgePreview: View {
    @State private var streak = 7

    var body: some View {
        VStack(spacing: Spacing.xl) {
            Text("STREAK BADGES")
                .sectionHeaderStyle()

            // Various streak states
            HStack(spacing: Spacing.large) {
                StreakBadge(currentStreak: 0, totalShipped: 0)
                StreakBadge(currentStreak: 3, longestStreak: 7, totalShipped: 15)
                StreakBadge(currentStreak: 7, longestStreak: 7, totalShipped: 42)
            }

            Divider()

            // Compact badges
            HStack(spacing: Spacing.medium) {
                CompactStreakBadge(currentStreak: 0)
                CompactStreakBadge(currentStreak: 5)
                CompactStreakBadge(currentStreak: 14)
            }

            Divider()

            // Interactive
            VStack {
                StreakBadge(currentStreak: streak, longestStreak: 14, totalShipped: 100)

                HStack {
                    Button("- Day") { streak = max(0, streak - 1) }
                    Button("+ Day") { streak += 1 }
                    Button("Reset") { streak = 0 }
                }
            }

            Divider()

            // Milestone banner
            StreakMilestoneBanner(milestone: 7) {
                print("Dismissed")
            }
        }
        .padding(Spacing.large)
        .frame(width: 600, height: 500)
        .background(Surface.window)
    }
}

#Preview {
    StreakBadgePreview()
}
#endif
