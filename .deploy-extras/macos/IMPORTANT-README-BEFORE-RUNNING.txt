PYNSOURCE — PLEASE READ BEFORE YOU DOUBLE-CLICK THE APP
=======================================================

You do NOT need to run anything first. Do this instead:

STEP 1.  Double-click "Pynsource.app".
         macOS will refuse to open it and offer you a "Done" button.

STEP 2.  Open System Settings > Privacy & Security.
         Scroll down to the "Security" section. You will see a line about
         "Pynsource.app" was blocked, with an "Open Anyway" button. Click it.
         Authenticate with your password / Touch ID.

STEP 3.  Double-click "Pynsource.app" again. Now it opens. macOS remembers this
         permanently - you only ever do this once.

Why is this happening?
----------------------
The app is not signed with a paid Apple Developer ID (that is USD $99 per year),
so macOS cannot verify who built it. It is the same for any small independent
Mac app that is not notarised.

If you prefer to skip the dialogs
---------------------------------
Open Terminal (Applications > Utilities > Terminal), type

    xattr -dr com.apple.quarantine

then drag "Pynsource.app" from Finder into the Terminal window (this fills in the
path for you), then press Return. Nothing is downloaded by that command - it only
removes the "this file came from the internet" flag from the app.

About "fix-permissions.command"
-------------------------------
That script does exactly the same thing as the Terminal command above. It is
provided for convenience, but it is itself unsigned, so macOS may refuse to run
it as well (same "Open Anyway" treatment in System Settings). If you have already
got Pynsource.app running via STEP 1-3, you can ignore the script completely.

Troubleshooting
---------------
* "Pynsource is damaged and can't be opened" - re-download the zip; a partially
  downloaded or unzipped-over-an-old-copy app can trigger this.
* Move the app to /Applications before running it for the first time, so the same
  exception applies in future.
* Windows / Linux builds do not need any of this.
