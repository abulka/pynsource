After you download and unzip the release, you need to give permission for the app to run on your machine. 
This is because the app is not signed via the Apple Developer program which would otherwise cost me USD $99 per year.
To do this, open a terminal and type:

    xattr -dr com.apple.quarantine ~/Downloads/pynsource-macos-version-1.85/Pynsource.app

otherwise

🎉 Easier Technique: Right click on the supplied bash script "fix-permissions.command" and choose "Open"
