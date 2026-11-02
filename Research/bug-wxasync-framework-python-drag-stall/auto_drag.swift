import Cocoa
import ApplicationServices

// Post a synthetic circular left-button drag: auto_drag <x> <y> <radius> <seconds>
// Always releases the button, including on early exit. Needs Accessibility permission.
func f(_ s: String) -> Double { Double(s) ?? 0 }
let a = CommandLine.arguments
guard a.count >= 5 else {
    print("usage: auto_drag x y radius seconds")
    exit(2)
}
let src = CGEventSource(stateID: .hidSystemState)

func post(_ type: CGEventType, _ p: CGPoint) {
    CGEvent(mouseEventSource: src, mouseType: type, mouseCursorPosition: p, mouseButton: .left)?
        .post(tap: .cghidEventTap)
}

func release() {
    let p = CGEvent(source: nil)?.location ?? .zero
    for t in [CGEventType.leftMouseUp, .rightMouseUp, .otherMouseUp] {
        CGEvent(mouseEventSource: src, mouseType: t, mouseCursorPosition: p, mouseButton: .left)?
            .post(tap: .cghidEventTap)
        usleep(20_000)
    }
}

let cx = f(a[1]), cy = f(a[2])
let radius = max(5, f(a[3]))
let seconds = min(30, max(1, f(a[4])))
let start = CGPoint(x: cx + radius, y: cy)

atexit { release() }            // belt and braces

post(.mouseMoved, start)
usleep(150_000)
post(.leftMouseDown, start)
let t0 = Date()
var n = 0
while Date().timeIntervalSince(t0) < seconds {
    let ang = Date().timeIntervalSince(t0) * 4.0
    post(.leftMouseDragged, CGPoint(x: cx + radius * CGFloat(cos(ang)),
                                    y: cy + radius * CGFloat(sin(ang))))
    usleep(8_000)
    n += 1
}
release()
print("posted \(n) drag events over \(seconds)s")
