PYNSOURCE - macOS blocks the app the first time. Here is exactly what to do.


1. Double-click "Pynsource".

2. macOS shows a box:

       "Pynsource" Not Opened
       Apple could not verify "Pynsource" is free of malware that may harm your
       Mac or compromise your privacy.

                                                        [ Done ]  [ Move to Bin ]

   Click  Done.        <-- NOT "Move to Bin"

3. Open  System Settings > Privacy & Security  and scroll to the bottom. You will see

       "Pynsource" was blocked to protect your Mac.        [ Open Anyway ]

   Click  Open Anyway.
   A second dialog asks the same thing - click  Open Anyway  again.
   Then enter your password or use Touch ID.

4. Double-click "Pynsource" again. It opens normally from now on.

That is all, and you only ever do it once. It happens because the app is not signed
with a paid Apple Developer ID (USD $99 a year), so macOS cannot verify who built it -
the same as any small independent Mac app that is not notarised.

Prefer the Terminal? One line, no dialogs:

    xattr -dr com.apple.quarantine /Applications/Pynsource.app

(nothing is downloaded by that command - it only removes the "came from the internet"
flag from the app you already have).
