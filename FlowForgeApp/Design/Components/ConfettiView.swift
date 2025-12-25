import SwiftUI

// MARK: - Confetti View
// Physics-based celebration animation
//
// Influenced by: Mike Matas (magical moments, physics)
// "The first ship should be unforgettable"

struct ConfettiView: View {
    @Binding var isActive: Bool
    let particleCount: Int
    let colors: [Color]
    let duration: Double

    @State private var particles: [ConfettiParticle] = []

    init(
        isActive: Binding<Bool>,
        particleCount: Int = 50,
        colors: [Color] = [.red, .blue, .green, .yellow, .orange, .purple, .pink],
        duration: Double = 3.0
    ) {
        self._isActive = isActive
        self.particleCount = particleCount
        self.colors = colors
        self.duration = duration
    }

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                ForEach(particles) { particle in
                    ConfettiPiece(particle: particle)
                }
            }
            .onChange(of: isActive) { _, newValue in
                if newValue {
                    createParticles(in: geometry.size)
                    scheduleCleanup()
                }
            }
        }
        .allowsHitTesting(false)
    }

    private func createParticles(in size: CGSize) {
        particles = (0..<particleCount).map { _ in
            ConfettiParticle(
                id: UUID(),
                color: colors.randomElement() ?? .blue,
                startPosition: CGPoint(x: size.width / 2, y: size.height / 2),
                velocity: CGVector(
                    dx: CGFloat.random(in: -200...200),
                    dy: CGFloat.random(in: (-400)...(-100))
                ),
                rotation: Double.random(in: 0...360),
                rotationSpeed: Double.random(in: -720...720),
                scale: CGFloat.random(in: 0.5...1.5),
                shape: ConfettiShape.allCases.randomElement() ?? .rectangle
            )
        }
    }

    private func scheduleCleanup() {
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            withAnimation(.easeOut(duration: 0.3)) {
                particles = []
                isActive = false
            }
        }
    }
}

// MARK: - Confetti Particle Model

struct ConfettiParticle: Identifiable {
    let id: UUID
    let color: Color
    let startPosition: CGPoint
    let velocity: CGVector
    let rotation: Double
    let rotationSpeed: Double
    let scale: CGFloat
    let shape: ConfettiShape
}

enum ConfettiShape: CaseIterable {
    case rectangle
    case circle
    case triangle
    case star
}

// MARK: - Confetti Piece View

struct ConfettiPiece: View {
    let particle: ConfettiParticle

    @State private var position: CGPoint = .zero
    @State private var rotation: Double = 0
    @State private var opacity: Double = 1
    @State private var hasLaunched = false

    private let gravity: CGFloat = 400

    var body: some View {
        confettiShape
            .fill(particle.color)
            .frame(width: 10 * particle.scale, height: 6 * particle.scale)
            .rotationEffect(.degrees(rotation))
            .rotation3DEffect(
                .degrees(rotation * 0.5),
                axis: (x: 1, y: 0, z: 0)
            )
            .position(position)
            .opacity(opacity)
            .onAppear {
                position = particle.startPosition
                rotation = particle.rotation
                launchParticle()
            }
    }

    private var confettiShape: AnyShape {
        switch particle.shape {
        case .rectangle:
            AnyShape(Rectangle())
        case .circle:
            AnyShape(Circle())
        case .triangle:
            AnyShape(Triangle())
        case .star:
            AnyShape(Star())
        }
    }

    private func launchParticle() {
        guard !hasLaunched else { return }
        hasLaunched = true

        // Animate position with physics
        withAnimation(.timingCurve(0.25, 0.1, 0.25, 1, duration: 2.5)) {
            position = CGPoint(
                x: particle.startPosition.x + particle.velocity.dx * 2,
                y: particle.startPosition.y + particle.velocity.dy * 2 + gravity * 2
            )
        }

        // Animate rotation
        withAnimation(.linear(duration: 2.5)) {
            rotation = particle.rotation + particle.rotationSpeed * 2.5
        }

        // Fade out at the end
        withAnimation(.easeIn(duration: 0.5).delay(2.0)) {
            opacity = 0
        }
    }
}

// MARK: - Custom Shapes

struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: rect.midX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        path.closeSubpath()
        return path
    }
}

struct Star: Shape {
    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let radius = min(rect.width, rect.height) / 2
        let innerRadius = radius * 0.4

        var path = Path()
        let points = 5

        for i in 0..<(points * 2) {
            let angle = (Double(i) * .pi / Double(points)) - .pi / 2
            let r = i.isMultiple(of: 2) ? radius : innerRadius
            let point = CGPoint(
                x: center.x + CGFloat(cos(angle)) * r,
                y: center.y + CGFloat(sin(angle)) * r
            )

            if i == 0 {
                path.move(to: point)
            } else {
                path.addLine(to: point)
            }
        }
        path.closeSubpath()
        return path
    }
}

// MARK: - Ship Celebration View
// Complete celebration overlay for shipping moments

struct ShipCelebrationView: View {
    @Binding var isShowing: Bool
    let featureTitle: String
    let onDismiss: () -> Void

    @State private var showConfetti = false
    @State private var showContent = false

    var body: some View {
        ZStack {
            // Dimmed background
            Color.black.opacity(0.4)
                .ignoresSafeArea()
                .onTapGesture {
                    dismiss()
                }

            // Confetti layer
            ConfettiView(isActive: $showConfetti)
                .ignoresSafeArea()

            // Content card
            VStack(spacing: Spacing.large) {
                // Success icon
                ZStack {
                    Circle()
                        .fill(Accent.success.opacity(0.2))
                        .frame(width: 80, height: 80)

                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 48))
                        .foregroundColor(Accent.success)
                }
                .scaleEffect(showContent ? 1.0 : 0.5)

                // Title
                VStack(spacing: Spacing.small) {
                    Text("Shipped!")
                        .font(Typography.largeTitle)

                    Text(featureTitle)
                        .font(Typography.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                }
                .opacity(showContent ? 1 : 0)
                .offset(y: showContent ? 0 : 20)

                // Dismiss button
                Button("Continue Shipping") {
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
                .tint(Accent.primary)
                .opacity(showContent ? 1 : 0)
            }
            .padding(Spacing.xl)
            .background(Surface.elevated)
            .cornerRadius(CornerRadius.xl)
            .shadow(radius: 20)
            .scaleEffect(showContent ? 1.0 : 0.9)
            .padding(Spacing.xl)
        }
        .opacity(isShowing ? 1 : 0)
        .onAppear {
            if isShowing {
                triggerCelebration()
            }
        }
        .onChange(of: isShowing) { _, newValue in
            if newValue {
                triggerCelebration()
            }
        }
    }

    private func triggerCelebration() {
        // Confetti first
        showConfetti = true

        // Then content with spring
        withAnimation(SpringPreset.celebration.delay(0.1)) {
            showContent = true
        }
    }

    private func dismiss() {
        withAnimation(SpringPreset.smooth) {
            showContent = false
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            isShowing = false
            onDismiss()
        }
    }
}

// MARK: - Preview

#if DEBUG
struct ConfettiPreview: View {
    @State private var showConfetti = false
    @State private var showCelebration = false

    var body: some View {
        ZStack {
            VStack(spacing: Spacing.xl) {
                Text("CELEBRATION SYSTEM")
                    .sectionHeaderStyle()

                Button("Trigger Confetti") {
                    showConfetti = true
                }
                .buttonStyle(.borderedProminent)

                Button("Show Ship Celebration") {
                    showCelebration = true
                }
                .buttonStyle(.bordered)

                Spacer()
            }
            .padding(Spacing.large)

            ConfettiView(isActive: $showConfetti)

            if showCelebration {
                ShipCelebrationView(
                    isShowing: $showCelebration,
                    featureTitle: "Add dark mode toggle",
                    onDismiss: {
                        print("Celebration dismissed")
                    }
                )
            }
        }
        .frame(width: 500, height: 600)
        .background(Surface.window)
    }
}

#Preview {
    ConfettiPreview()
}
#endif
