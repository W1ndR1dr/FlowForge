# Recreating Linear's Design Language in SwiftUI for macOS

Linear's interface represents the apex of developer tool design—dense yet breathable, dark yet warm, minimal yet functional. This guide provides specific values, code patterns, and implementation strategies for recreating Linear's visual language in a dark-mode SwiftUI macOS application targeting macOS 26.

## The Linear design philosophy in brief

Linear achieves its distinctive aesthetic through three core principles: **opacity-based elevation** rather than harsh shadows, **perceptual uniformity** via LCH color space, and **ruthless consistency** where every identical element animates identically. Their internal design system "Orbiter" requires only three variables to generate a complete theme: base color, accent color, and contrast level. This minimalism-through-system-thinking should guide your implementation.

---

## Color palette: the exact values

Linear's dark theme centers on **near-black backgrounds with warm undertones**. Their official theme format uses six comma-separated hex values representing background, text, surface, text-secondary, accent, and accent-text.

### Core dark mode palette (extracted from Linear's Midnight theme)

| Purpose | Hex | SwiftUI Implementation |
|---------|-----|----------------------|
| **Primary background** | `#0F0F10` | `Color(red: 0.059, green: 0.059, blue: 0.063)` |
| **Elevated surface** | `#151516` | `Color(red: 0.082, green: 0.082, blue: 0.086)` |
| **Primary text** | `#EEEFF1` | `Color(red: 0.933, green: 0.937, blue: 0.945)` |
| **Secondary text** | `#95A2B3` | `Color(red: 0.584, green: 0.635, blue: 0.702)` |
| **Accent (default)** | `#5E6AD2` | Linear's signature indigo |
| **Borders/dividers** | `rgba(255,255,255,0.08)` | `Color.white.opacity(0.08)` |
| **Hover background** | `rgba(255,255,255,0.06)` | `Color.white.opacity(0.06)` |

### Semantic colors

Linear uses muted, desaturated versions of standard semantic colors that feel native to their dark palette:

```swift
extension Color {
    // Linear-style semantic colors
    static let linearSuccess = Color(red: 0.302, green: 0.714, blue: 0.506)  // Muted green
    static let linearWarning = Color(red: 0.918, green: 0.678, blue: 0.329)  // Warm amber
    static let linearError = Color(red: 0.824, green: 0.369, blue: 0.396)    // #D25E65 (from themes)
    static let linearInfo = Color(red: 0.369, green: 0.416, blue: 0.824)     // Soft blue
}
```

### Brand colors (official from linear.app/brand)

| Color Name | Hex | Usage |
|-----------|-----|-------|
| Mercury White | `#F4F5F8` | Light mode accent |
| Nordic Gray | `#222326` | Dark mode wordmark |
| Button Indigo | `#4551B5` | Primary actions |

---

## Typography: Inter everywhere

Linear officially uses **Inter** for body/UI text and **Inter Display** for headings, confirmed in their redesign blog. This provides the clean, geometric sans-serif that defines modern developer tools.

### Type scale (reverse-engineered from Linear's web app)

| Style | Size | Weight | Letter-spacing | Line-height | Color |
|-------|------|--------|----------------|-------------|-------|
| **Hero heading** | 62px | 800 (Black) | 0 | 72px | `#F7F8F8` |
| **Section heading** | 20px | 600 (Semibold) | 0 | 28px | Primary |
| **Body large** | 15-16px | 400 (Regular) | 0 | 24px | Primary |
| **Body** | 14px | 400 (Regular) | 0 | 20px | Primary |
| **Label/caption** | 12px | 600 (Semibold) | 0.5px | 15px | `#95A2B3` |
| **Muted** | 13px | 400 (Regular) | 0 | 18px | Secondary |

### Implementing Inter in SwiftUI

```swift
// Load Inter as a variable font for full axis control
extension Font {
    static func inter(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .custom("Inter", size: size).weight(weight)
    }
    
    static func interDisplay(_ size: CGFloat, weight: Font.Weight = .semibold) -> Font {
        .custom("InterDisplay", size: size).weight(weight)
    }
}

// Define your type scale
extension Font {
    static let linearTitle = Font.interDisplay(20, weight: .semibold)
    static let linearBody = Font.inter(14, weight: .regular)
    static let linearCaption = Font.inter(12, weight: .semibold)
    static let linearMuted = Font.inter(13, weight: .regular)
}
```

For variable font axis control (optical sizing, precise weights):

```swift
extension Font {
    static func interVariable(_ size: CGFloat, axis: [Int: Double]) -> Font {
        let descriptor = NSFontDescriptor(fontAttributes: [
            .name: "Inter",
            .variation: axis
        ])
        return Font(NSFont(descriptor: descriptor, size: size) ?? .systemFont(ofSize: size))
    }
}

// Usage with weight axis (2003265652 = 'wght')
Text("Hello").font(.interVariable(14, axis: [2003265652: 500]))
```

---

## Density and breathing room: tight but not cramped

Linear achieves high information density through **reduced but consistent spacing** and **visual hierarchy through color rather than white space**. The key insight: they compress vertical spacing while maintaining horizontal padding.

### Spacing scale (inferred from UI analysis)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Between icon and text in same element |
| `sm` | 8px | Row vertical padding, compact gaps |
| `md` | 12px | Standard horizontal padding in rows |
| `lg` | 16px | Section gaps, larger component padding |
| `xl` | 24px | Major section separations |

### Row height philosophy

Linear's list rows are notably compact—approximately **32-36px** for standard items versus macOS's default ~44px. They achieve this through:

```swift
// Linear-style dense list configuration
List {
    ForEach(items) { item in
        LinearRow(item: item)
            .listRowInsets(EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12))
            .listRowBackground(Color.clear)
            .listRowSeparator(.hidden)
    }
}
.listStyle(.plain)
.scrollContentBackground(.hidden)
.environment(\.defaultMinListRowHeight, 32)  // Reduce minimum
.listRowSpacing(2)  // Tight vertical rhythm
```

### Achieving the tight-but-breathable feel

The secret is **generous horizontal padding** combined with **minimal vertical spacing**:

```swift
struct LinearRow: View {
    let item: Item
    @State private var isHovered = false
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: item.icon)
                .font(.system(size: 14))
                .foregroundColor(.secondary)
                .frame(width: 16)
            
            Text(item.title)
                .font(.inter(14))
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(item.shortcut)
                .font(.inter(12))
                .foregroundColor(Color(hex: "#95A2B3"))
        }
        .padding(.vertical, 6)      // Tight vertical
        .padding(.horizontal, 12)   // Generous horizontal
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isHovered ? Color.white.opacity(0.06) : Color.clear)
        )
        .onHover { isHovered = $0 }
    }
}
```

---

## Sidebar that feels unified, not chrome

Linear's sidebar integrates seamlessly with content rather than feeling like bolted-on OS chrome. The approach: **remove visual separation** and **use color continuity**.

### Eliminating NavigationSplitView defaults

```swift
struct LinearSidebar: View {
    @State private var selection: String?
    
    var body: some View {
        NavigationSplitView {
            SidebarContent(selection: $selection)
                .navigationSplitViewColumnWidth(min: 200, ideal: 240, max: 280)
        } detail: {
            DetailContent(selection: selection)
        }
        .navigationSplitViewStyle(.balanced)
        .toolbar(removing: .title)          // Remove title chrome
        .toolbarBackground(.hidden, for: .windowToolbar)  // Hide toolbar bg
        .preferredColorScheme(.dark)        // Force dark mode
    }
}
```

### Custom sidebar implementation

For complete control, bypass system sidebar styling entirely:

```swift
struct LinearSidebarContent: View {
    @Binding var selection: SidebarItem?
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 2) {
                // Section header
                Text("WORKSPACE")
                    .font(.inter(11, weight: .semibold))
                    .foregroundColor(Color(hex: "#95A2B3"))
                    .padding(.horizontal, 12)
                    .padding(.top, 16)
                    .padding(.bottom, 4)
                
                ForEach(items) { item in
                    SidebarRow(item: item, isSelected: selection?.id == item.id)
                        .onTapGesture {
                            withAnimation(.snappy(duration: 0.2)) {
                                selection = item
                            }
                        }
                }
            }
            .padding(.vertical, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(hex: "#0F0F10"))  // Match main background
    }
}

struct SidebarRow: View {
    let item: SidebarItem
    let isSelected: Bool
    @State private var isHovered = false
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: item.icon)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(isSelected ? .white : Color(hex: "#95A2B3"))
                .frame(width: 18)
            
            Text(item.title)
                .font(.inter(14))
                .foregroundColor(isSelected ? .white : .primary)
            
            Spacer()
            
            if item.count > 0 {
                Text("\(item.count)")
                    .font(.inter(12))
                    .foregroundColor(Color(hex: "#95A2B3"))
            }
        }
        .padding(.vertical, 7)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 6, style: .continuous)
                .fill(backgroundColor)
        )
        .padding(.horizontal, 8)
        .onHover { isHovered = $0 }
    }
    
    var backgroundColor: Color {
        if isSelected { return Color.white.opacity(0.1) }
        if isHovered { return Color.white.opacity(0.05) }
        return Color.clear
    }
}
```

### Blur approach: use sparingly

Linear uses minimal blur—primarily for modals and dropdowns rather than sidebars. When needed:

```swift
struct LinearBlurView: NSViewRepresentable {
    var material: NSVisualEffectView.Material = .hudWindow
    
    func makeNSView(context: Context) -> NSVisualEffectView {
        let view = NSVisualEffectView()
        view.material = material
        view.blendingMode = .behindWindow
        view.state = .active
        view.appearance = NSAppearance(named: .darkAqua)
        return view
    }
    
    func updateNSView(_ nsView: NSVisualEffectView, context: Context) {}
}
```

---

## Soft elevation: surfaces that lift gently

Linear creates depth through **opacity and color shifts rather than dramatic shadows**. Surfaces are differentiated by subtle background value changes.

### The elevation system

| Level | Purpose | Color Treatment |
|-------|---------|----------------|
| **Base (0)** | Main background | `#0F0F10` |
| **Elevated (1)** | Cards, panels | `#151516` |
| **Floating (2)** | Dropdowns, popovers | `#1A1A1C` + subtle shadow |
| **Modal (3)** | Dialogs, command palette | `#1E1E20` + medium shadow |

### Shadow philosophy

Linear uses **very soft, large-radius shadows** with low opacity:

```swift
extension View {
    func linearCardShadow() -> some View {
        self.shadow(
            color: Color.black.opacity(0.25),
            radius: 20,
            x: 0,
            y: 8
        )
    }
    
    func linearDropdownShadow() -> some View {
        self.shadow(
            color: Color.black.opacity(0.4),
            radius: 32,
            x: 0,
            y: 16
        )
    }
    
    func linearSubtleShadow() -> some View {
        self.shadow(
            color: Color.black.opacity(0.15),
            radius: 8,
            x: 0,
            y: 2
        )
    }
}
```

### Card implementation

```swift
struct LinearCard<Content: View>: View {
    @ViewBuilder let content: Content
    
    var body: some View {
        content
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(Color(hex: "#151516"))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .strokeBorder(Color.white.opacity(0.06), lineWidth: 1)
                    )
            )
            .linearSubtleShadow()
    }
}
```

### Popover/dropdown styling

```swift
struct LinearPopover<Content: View>: View {
    @ViewBuilder let content: Content
    
    var body: some View {
        content
            .padding(8)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(Color(hex: "#1A1A1C"))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .strokeBorder(Color.white.opacity(0.08), lineWidth: 1)
                    )
            )
            .linearDropdownShadow()
    }
}
```

---

## Dark-native input fields

System TextField controls look foreign in Linear's aesthetic. Custom styling is essential.

### Fully styled text field

```swift
struct LinearTextField: View {
    let placeholder: String
    @Binding var text: String
    @FocusState private var isFocused: Bool
    @State private var isHovered = false
    
    var body: some View {
        TextField(placeholder, text: $text)
            .textFieldStyle(.plain)
            .font(.inter(14))
            .foregroundColor(.primary)
            .padding(.vertical, 10)
            .padding(.horizontal, 12)
            .background(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(Color(hex: "#151516"))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .strokeBorder(borderColor, lineWidth: 1)
            )
            .focused($isFocused)
            .onHover { isHovered = $0 }
    }
    
    var borderColor: Color {
        if isFocused { return Color(hex: "#5E6AD2").opacity(0.6) }
        if isHovered { return Color.white.opacity(0.12) }
        return Color.white.opacity(0.08)
    }
}
```

### Search input with icon

```swift
struct LinearSearchField: View {
    @Binding var text: String
    @FocusState private var isFocused: Bool
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(Color(hex: "#95A2B3"))
            
            TextField("Search...", text: $text)
                .textFieldStyle(.plain)
                .font(.inter(14))
                .focused($isFocused)
            
            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(Color(hex: "#95A2B3"))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .fill(Color(hex: "#151516"))
                .overlay(
                    RoundedRectangle(cornerRadius: 8, style: .continuous)
                        .strokeBorder(
                            isFocused ? Color(hex: "#5E6AD2").opacity(0.5) : Color.white.opacity(0.08),
                            lineWidth: 1
                        )
                )
        )
    }
}
```

### NSTextField for full control (cursor color, selection)

When you need to customize cursor or selection colors:

```swift
struct LinearNSTextField: NSViewRepresentable {
    @Binding var text: String
    var placeholder: String = ""
    
    func makeNSView(context: Context) -> NSTextField {
        let field = NSTextField()
        field.delegate = context.coordinator
        field.stringValue = text
        field.placeholderString = placeholder
        field.font = NSFont(name: "Inter", size: 14)
        field.textColor = NSColor(Color.primary)
        field.backgroundColor = NSColor(Color(hex: "#151516"))
        field.isBordered = false
        field.focusRingType = .none
        field.drawsBackground = true
        field.cell?.wraps = false
        field.cell?.isScrollable = true
        return field
    }
    
    func updateNSView(_ nsView: NSTextField, context: Context) {
        nsView.stringValue = text
    }
    
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    
    class Coordinator: NSObject, NSTextFieldDelegate {
        var parent: LinearNSTextField
        init(_ parent: LinearNSTextField) { self.parent = parent }
        
        func controlTextDidChange(_ notification: Notification) {
            guard let field = notification.object as? NSTextField else { return }
            parent.text = field.stringValue
        }
    }
}
```

---

## Micro-interactions and animation timing

Linear's CTO revealed that **hover transitions use exactly 150ms**—and any deviation from this consistency is treated as a quality defect.

### The golden timing values

| Interaction | Duration | Curve/Spring |
|------------|----------|--------------|
| **Hover in/out** | 150ms | `.easeInOut(duration: 0.15)` |
| **Button press** | 120ms | `.snappy(duration: 0.12)` |
| **Selection change** | 200ms | `.snappy(duration: 0.2)` |
| **View transitions** | 300-400ms | `.spring(response: 0.35, dampingFraction: 0.85)` |
| **Modal presentation** | 350ms | `.spring(response: 0.35, dampingFraction: 0.9)` |

### Hover modifier (reusable)

```swift
struct LinearHoverModifier: ViewModifier {
    @State private var isHovered = false
    var hoverBackground: Color = Color.white.opacity(0.06)
    var cornerRadius: CGFloat = 6
    
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .fill(isHovered ? hoverBackground : Color.clear)
            )
            .onHover { hovering in
                withAnimation(.easeInOut(duration: 0.15)) {
                    isHovered = hovering
                }
            }
    }
}

extension View {
    func linearHover(background: Color = Color.white.opacity(0.06), radius: CGFloat = 6) -> some View {
        modifier(LinearHoverModifier(hoverBackground: background, cornerRadius: radius))
    }
}
```

### Button with press scale

```swift
struct LinearButtonStyle: ButtonStyle {
    @State private var isHovered = false
    var variant: Variant = .secondary
    
    enum Variant {
        case primary, secondary, ghost
    }
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.inter(14, weight: .medium))
            .padding(.vertical, 8)
            .padding(.horizontal, 14)
            .foregroundColor(foregroundColor)
            .background(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(backgroundColor(isPressed: configuration.isPressed))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .strokeBorder(borderColor, lineWidth: variant == .ghost ? 0 : 1)
            )
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.snappy(duration: 0.12), value: configuration.isPressed)
            .onHover { isHovered = $0 }
    }
    
    var foregroundColor: Color {
        switch variant {
        case .primary: return .white
        case .secondary, .ghost: return .primary
        }
    }
    
    func backgroundColor(isPressed: Bool) -> Color {
        switch variant {
        case .primary:
            return isPressed ? Color(hex: "#4551B5") : Color(hex: "#5E6AD2")
        case .secondary:
            return isPressed ? Color.white.opacity(0.08) : (isHovered ? Color.white.opacity(0.06) : Color.clear)
        case .ghost:
            return isHovered ? Color.white.opacity(0.06) : Color.clear
        }
    }
    
    var borderColor: Color {
        switch variant {
        case .primary: return Color.clear
        case .secondary: return Color.white.opacity(0.1)
        case .ghost: return Color.clear
        }
    }
}
```

### Selection with matched geometry

```swift
struct LinearTabBar: View {
    @Binding var selection: Int
    let tabs: [String]
    @Namespace private var namespace
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(Array(tabs.enumerated()), id: \.offset) { index, title in
                Button {
                    withAnimation(.snappy(duration: 0.25)) {
                        selection = index
                    }
                } label: {
                    Text(title)
                        .font(.inter(13, weight: selection == index ? .semibold : .regular))
                        .foregroundColor(selection == index ? .primary : .secondary)
                        .padding(.vertical, 6)
                        .padding(.horizontal, 12)
                        .background {
                            if selection == index {
                                RoundedRectangle(cornerRadius: 6, style: .continuous)
                                    .fill(Color.white.opacity(0.1))
                                    .matchedGeometryEffect(id: "tab", in: namespace)
                            }
                        }
                }
                .buttonStyle(.plain)
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .fill(Color(hex: "#151516"))
        )
    }
}
```

---

## macOS 26 considerations

macOS 26 Tahoe introduces **Liquid Glass**, Apple's new adaptive material system. For a Linear-style app, you'll want to **opt out of some automatic Liquid Glass behaviors** to maintain your custom dark aesthetic.

### Preserving your design in Tahoe

```swift
@main
struct LinearStyleApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
                // Tahoe: Control glass effect adoption
        }
        .windowStyle(.hiddenTitleBar)
        .windowToolbarStyle(.unifiedCompact)
    }
}
```

### Useful new Tahoe APIs

While maintaining Linear's aesthetic, leverage these new capabilities:

- **`ToolbarSpacer(.fixed)`** for precise toolbar grouping
- **`scrollEdgeEffectStyle(.soft)`** for dense list scroll indicators
- **`containerBackground(.hidden, for: .window)`** to remove system backgrounds

### Dense list optimizations (all macOS versions)

```swift
extension View {
    func linearListStyling() -> some View {
        self
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
            .environment(\.defaultMinListRowHeight, 32)
            .listRowSpacing(2)
    }
}
```

---

## Complete color extension

```swift
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 6: (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default: (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(.sRGB, red: Double(r) / 255, green: Double(g) / 255, blue: Double(b) / 255, opacity: Double(a) / 255)
    }
}

// Linear palette namespace
enum LinearColors {
    // Backgrounds
    static let background = Color(hex: "#0F0F10")
    static let surface = Color(hex: "#151516")
    static let surfaceElevated = Color(hex: "#1A1A1C")
    static let surfaceModal = Color(hex: "#1E1E20")
    
    // Text
    static let textPrimary = Color(hex: "#EEEFF1")
    static let textSecondary = Color(hex: "#95A2B3")
    static let textTertiary = Color(hex: "#6B7280")
    static let textMuted = Color(hex: "#4B5563")
    
    // Interactive
    static let accent = Color(hex: "#5E6AD2")
    static let accentHover = Color(hex: "#6872D9")
    static let accentPressed = Color(hex: "#4551B5")
    
    // Borders
    static let border = Color.white.opacity(0.08)
    static let borderFocus = Color(hex: "#5E6AD2").opacity(0.5)
    static let borderHover = Color.white.opacity(0.12)
    
    // Semantic
    static let success = Color(hex: "#4DA673")
    static let warning = Color(hex: "#EAA94B")
    static let error = Color(hex: "#D25E65")
    static let info = Color(hex: "#5E6AD2")
    
    // Interaction states
    static let hoverBackground = Color.white.opacity(0.06)
    static let selectedBackground = Color.white.opacity(0.1)
    static let pressedBackground = Color.white.opacity(0.08)
}
```

---

## Key implementation principles

Linear's design excellence stems from **obsessive consistency**: every similar element animates identically (that 150ms timing), every surface follows the elevation hierarchy, and every interaction provides immediate feedback. Their "Quality Wednesdays" practice—where each engineer fixes one small polish issue weekly—has accumulated over 1,000 micro-improvements.

For your SwiftUI implementation, prioritize these patterns: use `.plain` list styles and manually control everything; define your colors once in an enum and reference consistently; create reusable hover and button modifiers; and test every interaction for that 150ms timing consistency. The goal isn't pixel-perfect replication but capturing the *feeling* of Linear—dense information, gentle elevation, and interface elements that respond instantly to every input.

The complete system emerges from these primitives: Inter typography at a tight scale, near-black backgrounds differentiated by subtle value shifts, opacity-based hover and selection states, soft shadows with large radii, and spring animations that feel snappy without bouncing. When these elements align consistently, you achieve that distinctive Linear quality—an interface that feels as refined as native macOS while remaining unmistakably custom.