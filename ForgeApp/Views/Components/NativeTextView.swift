import SwiftUI

#if os(macOS)
import AppKit

/// Efficient text view for long content using native NSTextField.
/// Uses NSTextField in label mode which properly reports intrinsic size.
struct NativeTextView: NSViewRepresentable {
    let text: String
    let font: NSFont
    let textColor: NSColor
    let backgroundColor: NSColor
    let isSelectable: Bool

    init(
        text: String,
        font: NSFont = .systemFont(ofSize: 13),
        textColor: NSColor = .labelColor,
        backgroundColor: NSColor = .clear,
        isSelectable: Bool = true
    ) {
        self.text = text
        self.font = font
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.isSelectable = isSelectable
    }

    func makeNSView(context: Context) -> NSTextField {
        let textField = NSTextField(wrappingLabelWithString: "")
        textField.isEditable = false
        textField.isSelectable = isSelectable
        textField.drawsBackground = false
        textField.isBordered = false
        textField.lineBreakMode = .byWordWrapping
        textField.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        return textField
    }

    func updateNSView(_ textField: NSTextField, context: Context) {
        textField.stringValue = text
        textField.font = font
        textField.textColor = textColor
        textField.isSelectable = isSelectable
    }
}

#else
import UIKit

/// Efficient text view for long content using native UITextView.
struct NativeTextView: UIViewRepresentable {
    let text: String
    let font: UIFont
    let textColor: UIColor
    let backgroundColor: UIColor
    let isSelectable: Bool

    init(
        text: String,
        font: UIFont = .systemFont(ofSize: 15),
        textColor: UIColor = .label,
        backgroundColor: UIColor = .clear,
        isSelectable: Bool = true
    ) {
        self.text = text
        self.font = font
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.isSelectable = isSelectable
    }

    func makeUIView(context: Context) -> UITextView {
        let textView = UITextView()
        textView.isEditable = false
        textView.isSelectable = isSelectable
        textView.isScrollEnabled = false  // Let parent scroll
        textView.backgroundColor = backgroundColor
        textView.textContainerInset = .zero
        textView.textContainer.lineFragmentPadding = 0
        return textView
    }

    func updateUIView(_ textView: UITextView, context: Context) {
        if textView.text != text {
            textView.text = text
            textView.font = font
            textView.textColor = textColor
            textView.backgroundColor = backgroundColor
            textView.isSelectable = isSelectable
        }
    }
}
#endif

// MARK: - SwiftUI Convenience

extension NativeTextView {
    /// Create with SwiftUI-style parameters
    static func styled(
        _ text: String,
        size: CGFloat = 13,
        color: Color = .primary,
        background: Color = .clear,
        selectable: Bool = true
    ) -> NativeTextView {
        #if os(macOS)
        return NativeTextView(
            text: text,
            font: .systemFont(ofSize: size),
            textColor: NSColor(color),
            backgroundColor: NSColor(background),
            isSelectable: selectable
        )
        #else
        return NativeTextView(
            text: text,
            font: .systemFont(ofSize: size),
            textColor: UIColor(color),
            backgroundColor: UIColor(background),
            isSelectable: selectable
        )
        #endif
    }
}
