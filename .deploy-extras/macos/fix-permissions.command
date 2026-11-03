#!/bin/bash
# Pynsource - remove the "downloaded from the internet" flag from Pynsource.app so macOS
# stops refusing to launch it. Does nothing else: no download, no install, no network.
#
# NOTE: this script is unsigned too, so macOS may refuse to run THIS as well. If so:
#   * System Settings > Privacy & Security > Security > "Open Anyway", then run it again, or
#   * simply skip it - open Terminal and paste:
#         xattr -dr com.apple.quarantine "/path/to/Pynsource.app"
#         (drag the app from Finder into Terminal to fill in the path)
#   * or skip both: double-click Pynsource.app, let macOS block it, then
#     System Settings > Privacy & Security > "Open Anyway".
#
# Why any of this is needed: the app is ad-hoc signed only (no Apple Developer ID, which
# costs USD $99/year), so macOS cannot verify who built it.

set -u
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
APP_NAME="Pynsource.app"
APP="$SCRIPTPATH/$APP_NAME"

say() {
    echo "$1"
    osascript -e "display dialog \"$1\" buttons {\"OK\"} with icon ${2:-note}" >/dev/null 2>&1
}

if [ ! -d "$APP" ]; then
    say "Pynsource.app was not found next to this script. Put this script in the same folder as Pynsource.app and run it again." caution
    exit 1
fi

if ! command -v xattr >/dev/null 2>&1; then
    say "This script needs the built-in 'xattr' tool, which is missing. Use System Settings > Privacy & Security > Open Anyway on Pynsource.app instead." caution
    exit 1
fi

xattr -dr com.apple.quarantine "$APP" 2>/dev/null
STATUS=$?

# permissions can survive a zip badly on some tools; harmless if already correct
chmod +x "$APP/Contents/MacOS/Pynsource" 2>/dev/null

if [ $STATUS -eq 0 ]; then
    say "Done. $APP_NAME can be opened now." note
    exit 0
else
    say "Could not clear the quarantine flag. Open Terminal and run: xattr -dr com.apple.quarantine 'path to Pynsource.app'. Or use System Settings > Privacy & Security > Open Anyway." caution
    exit 1
fi
