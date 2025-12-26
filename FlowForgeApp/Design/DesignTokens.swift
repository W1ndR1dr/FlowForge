import SwiftUI

// MARK: - Design Tokens
// Influenced by: Dieter Rams (systematic), Edward Tufte (semantic), Jony Ive (considered)
//
// "Good design is as little design as possible" — Dieter Rams
// Every token serves a purpose. Nothing decorative.

// MARK: - Color System

/// Semantic status colors — the color IS the information (Tufte)
enum StatusColor {
    /// Idea: Quick capture, rough sketch — creative purple
    static let idea = Color("StatusIdea", bundle: nil)
    static let ideaFallback = Color(light: .purple.opacity(0.8), dark: .purple)

    /// Planned: Waiting, not urgent — subdued, patient
    static let planned = Color("StatusPlanned", bundle: nil)
    static let plannedFallback = Color(light: .init(white: 0.45), dark: .init(white: 0.55))

    /// In Progress: Active work, attention here — confident blue
    static let inProgress = Color("StatusInProgress", bundle: nil)
    static let inProgressFallback = Color(light: .blue, dark: .init(red: 0.4, green: 0.6, blue: 1.0))

    /// Review: Almost done, needs final check — warm amber
    static let review = Color("StatusReview", bundle: nil)
    static let reviewFallback = Color(light: .orange, dark: .init(red: 1.0, green: 0.7, blue: 0.3))

    /// Completed: Shipped, celebration — fresh emerald
    static let completed = Color("StatusCompleted", bundle: nil)
    static let completedFallback = Color(light: .init(red: 0.2, green: 0.7, blue: 0.4), dark: .init(red: 0.3, green: 0.8, blue: 0.5))

    /// Blocked: Problem, needs intervention — alert rose
    static let blocked = Color("StatusBlocked", bundle: nil)
    static let blockedFallback = Color(light: .init(red: 0.9, green: 0.3, blue: 0.3), dark: .init(red: 1.0, green: 0.4, blue: 0.4))

    static func color(for status: FeatureStatus) -> Color {
        switch status {
        case .idea: return ideaFallback
        case .planned: return plannedFallback
        case .inProgress: return inProgressFallback
        case .review: return reviewFallback
        case .completed: return completedFallback
        case .blocked: return blockedFallback
        }
    }
}

/// Complexity indicators — size feeling through visual weight (Tufte)
enum ComplexityColor {
    /// Small: Quick win, ship today — light, encouraging
    static let small = Color.green.opacity(0.8)

    /// Medium: Half-day to full day — balanced, neutral
    static let medium = Color.orange.opacity(0.8)

    /// Large: Multi-day, needs planning — heavier, attention
    static let large = Color.red.opacity(0.8)

    /// Epic: Should be broken down — outlined, warning
    static let epic = Color.purple.opacity(0.6)
}

/// Surface hierarchy — Ive's layered depth thinking
enum Surface {
    /// Base window background — respects system appearance
    static var window: Color {
        #if os(macOS)
        Color(nsColor: .windowBackgroundColor)
        #else
        Color(uiColor: .systemBackground)
        #endif
    }

    /// Elevated surface (+1 level) — cards, containers
    static var elevated: Color {
        #if os(macOS)
        Color(nsColor: .controlBackgroundColor)
        #else
        Color(uiColor: .secondarySystemBackground)
        #endif
    }

    /// Highlighted surface (+2 level) — active card, focus
    static var highlighted: Color {
        #if os(macOS)
        Color(nsColor: .selectedContentBackgroundColor).opacity(0.3)
        #else
        Color(uiColor: .tertiarySystemBackground)
        #endif
    }

    /// Overlay with blur — modals, sheets
    static let overlay = Color.black.opacity(0.4)
}

/// Accent colors for actions and emphasis
enum Accent {
    /// Primary action color — the SHIP button
    static let primary = Color.blue

    /// Success/celebration — shipping moments
    static let success = Color.green

    /// Warning — approaching limits, streak at risk
    static let warning = Color.orange

    /// Danger — destructive actions, blockers
    static let danger = Color.red

    /// Streak fire — motivation, gamification
    static let streak = Color.orange
}

// MARK: - Typography Scale
// "Above all else, show the data" — Tufte
// Hierarchy is purposeful, not decorative

enum Typography {
    /// Project name, main headers — Large Title
    static let largeTitle = Font.largeTitle.weight(.bold)

    /// Section headers — Title 2
    static let sectionHeader = Font.title2.weight(.semibold)

    /// Feature titles — Headline
    static let featureTitle = Font.headline.weight(.semibold)

    /// Descriptions, body text — Body
    static let body = Font.body

    /// Metadata, timestamps — Caption
    static let caption = Font.caption.weight(.regular)

    /// Badges, tags — Caption 2
    static let badge = Font.caption2.weight(.medium)

    /// Streak number — custom large
    static let streakNumber = Font.system(size: 28, weight: .bold, design: .rounded)

    /// Vibe input placeholder — inviting
    static let vibeInput = Font.title3.weight(.regular)
}

// MARK: - Spacing Scale
// Systematic spacing — Rams' "less, but better"

enum Spacing {
    /// Micro spacing — 4pt (badge internals, tight elements)
    static let micro: CGFloat = 4

    /// Small spacing — 8pt (tag spacing, icon gaps)
    static let small: CGFloat = 8

    /// Medium spacing — 12pt (card internal spacing)
    static let medium: CGFloat = 12

    /// Standard spacing — 16pt (section gaps, card padding)
    static let standard: CGFloat = 16

    /// Large spacing — 24pt (major section gaps)
    static let large: CGFloat = 24

    /// XL spacing — 32pt (view-level separation)
    static let xl: CGFloat = 32
}

// MARK: - Corner Radius
// Consistent curves — considered, not arbitrary

enum CornerRadius {
    /// Small — 4pt (badges, chips)
    static let small: CGFloat = 4

    /// Medium — 8pt (buttons, small cards)
    static let medium: CGFloat = 8

    /// Large — 12pt (major cards, containers)
    static let large: CGFloat = 12

    /// XL — 16pt (modals, sheets)
    static let xl: CGFloat = 16
}

// MARK: - Shadows
// Subtle depth — Ive's material thinking

enum Shadow {
    /// Subtle shadow — resting state
    static func subtle(_ colorScheme: ColorScheme) -> some View {
        Color.black.opacity(colorScheme == .dark ? 0.3 : 0.08)
    }

    /// Elevated shadow — hover, focus
    static func elevated(_ colorScheme: ColorScheme) -> some View {
        Color.black.opacity(colorScheme == .dark ? 0.4 : 0.12)
    }

    /// Shadow radius for resting state
    static let subtleRadius: CGFloat = 2

    /// Shadow radius for elevated state
    static let elevatedRadius: CGFloat = 8
}

// MARK: - Animation Timing
// Mike Matas: "Every animation should feel physical"
// These are base values — AnimationPrimitives.swift has the full system

enum Timing {
    /// Micro-interactions — button press, hover (100ms)
    static let micro: Double = 0.1

    /// State transitions — color change, card move (300ms)
    static let standard: Double = 0.3

    /// Celebrations — confetti, streak (500-800ms)
    static let celebration: Double = 0.5

    /// Long animations — modal appear, graph zoom (400ms)
    static let long: Double = 0.4
}

// MARK: - Helper Extensions

extension Color {
    /// Create a color that adapts to light/dark mode
    init(light: Color, dark: Color) {
        #if os(macOS)
        self.init(nsColor: NSColor(name: nil) { appearance in
            appearance.bestMatch(from: [.aqua, .darkAqua]) == .darkAqua
                ? NSColor(dark)
                : NSColor(light)
        })
        #else
        self.init(uiColor: UIColor { traitCollection in
            traitCollection.userInterfaceStyle == .dark
                ? UIColor(dark)
                : UIColor(light)
        })
        #endif
    }
}

// MARK: - Design Token View Modifiers

extension View {
    /// Apply card styling with proper elevation
    func cardStyle(isActive: Bool = false) -> some View {
        self
            .padding(Spacing.standard)
            .background(isActive ? Surface.highlighted : Surface.elevated)
            .cornerRadius(CornerRadius.large)
    }

    /// Apply badge styling
    func badgeStyle(color: Color) -> some View {
        self
            .font(Typography.badge)
            .padding(.horizontal, Spacing.small)
            .padding(.vertical, Spacing.micro)
            .background(color.opacity(0.2))
            .foregroundColor(color)
            .cornerRadius(CornerRadius.small)
    }

    /// Apply section header styling
    func sectionHeaderStyle() -> some View {
        self
            .font(Typography.caption)
            .fontWeight(.semibold)
            .foregroundColor(.secondary)
            .textCase(.uppercase)
            .tracking(0.5)
    }
}

// MARK: - Unified DesignTokens Namespace
// Provides a consistent interface for accessing design tokens

enum DesignTokens {
    enum Colors {
        static let primary = Accent.primary
        static let success = Accent.success
        static let warning = Accent.warning
        static let danger = Accent.danger
        static let surface = Surface.elevated
        static let background = Surface.window
    }

    enum Spacing {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 12
        static let lg: CGFloat = 16
        static let xl: CGFloat = 24
    }

    enum Radius {
        static let sm: CGFloat = 4
        static let md: CGFloat = 8
        static let lg: CGFloat = 12
    }
}

// MARK: - Preview

#if DEBUG
struct DesignTokensPreview: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.large) {
                // Colors
                Text("STATUS COLORS")
                    .sectionHeaderStyle()

                HStack(spacing: Spacing.medium) {
                    ForEach(FeatureStatus.allCases, id: \.self) { status in
                        VStack {
                            Circle()
                                .fill(StatusColor.color(for: status))
                                .frame(width: 40, height: 40)
                            Text(status.rawValue)
                                .font(Typography.caption)
                        }
                    }
                }

                // Typography
                Text("TYPOGRAPHY")
                    .sectionHeaderStyle()

                VStack(alignment: .leading, spacing: Spacing.small) {
                    Text("Large Title").font(Typography.largeTitle)
                    Text("Section Header").font(Typography.sectionHeader)
                    Text("Feature Title").font(Typography.featureTitle)
                    Text("Body Text").font(Typography.body)
                    Text("Caption").font(Typography.caption)
                    Text("BADGE").font(Typography.badge)
                }

                // Spacing
                Text("SPACING")
                    .sectionHeaderStyle()

                HStack(spacing: Spacing.small) {
                    spacingBlock(Spacing.micro, "4")
                    spacingBlock(Spacing.small, "8")
                    spacingBlock(Spacing.medium, "12")
                    spacingBlock(Spacing.standard, "16")
                    spacingBlock(Spacing.large, "24")
                }
            }
            .padding(Spacing.large)
        }
        .frame(width: 500, height: 600)
    }

    func spacingBlock(_ size: CGFloat, _ label: String) -> some View {
        VStack {
            Rectangle()
                .fill(Color.blue.opacity(0.3))
                .frame(width: size, height: size)
            Text(label)
                .font(Typography.caption)
        }
    }
}

#Preview {
    DesignTokensPreview()
}
#endif
