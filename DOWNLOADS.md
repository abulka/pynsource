# Download Pynsource 

The latest version is `1.85`

[Download](https://github.com/abulka/pynsource/releases/latest) the latest stable release. 👈

Python 3.10 syntax is now supported - see [1.85 beta 2 release](https://github.com/abulka/pynsource/releases/tag/pre-70)

## Mac (Homebrew — no Gatekeeper dialogs)

```bash
brew install --cask abulka/pynsource/pynsource
```

Install into `/Applications`, no unzipping, no Gatekeeper prompt (the cask clears the
quarantine flag for you). Tap: [abulka/homebrew-pynsource](https://github.com/abulka/homebrew-pynsource).

Upgrade with plain `brew upgrade`, or `brew upgrade --cask abulka/pynsource/pynsource` —
**not** `brew upgrade --cask pynsource`, which is Homebrew's own long-abandoned 1.84 cask
(Intel, and disabled since 2026-09-01 because it fails the macOS Gatekeeper check; that is
also why `brew info pynsource` shows a red `disabled` and a Rosetta caveat).

This build is **Apple silicon (arm64) only**.

## Mac (zip download)

Unzip and drag app into the Applications directory.

> **Mac users:** macOS will block the app the first time you double-click it. Click **Done**
> (not "Move to Bin"), then **System Settings > Privacy & Security** > scroll to the bottom >
> **Open Anyway** (a second dialog asks again - click it again), then authenticate. Full steps
> are in `IMPORTANT-README-BEFORE-RUNNING.txt` inside the download. Alternative, no dialogs:
> `xattr -dr com.apple.quarantine /Applications/Pynsource.app`

## Windows 10

Unzip and run the installer.

## Linux

Unzip and run the standalone executables available. These are named Ubuntu but run in any debian based system like Mint 21 etc.

The benefit of the binaries is that they run via the latest version of Python available, and will be able to parse advanced Python syntax like the walrus operator or Python 3.10 match-case syntax. They can also be registered with a Pro license (Python snaps cannot).

Special rare builds running version 1.77:
 * [Ubuntu Linux 16.0.4 download](http://bit.ly/pynsource-1-77-ubuntu-16) (unzip and run the executable) 
 * [Ubuntu Fedora 31 download](https://github.com/abulka/pynsource/releases/download/version-1.77/pynsource-1.77-fedora-31.zip) (unzip and run the executable via the terminal e.g. `./Pynsource`)

## Ubuntu Snap Installation

Visit [Linux snap installer](http://bit.ly/pynsource-snap) (one-click install on any Ubuntu distro) or simply

    sudo snap install pynsource

Note re snaps under Ubuntu 16.04 Due to a bug in Snapcraft, if you are trying to install the snap on Ubuntu 16.04 the GUI installer will not work and you will have to install from the terminal.

    sudo snap install pynsource
    sudo snap install core
    pynsource 

> Limitation: The Ubuntu Snap still uses Python 3.6 so cannot parse Python 3.10 syntax. The Canonical snap build system is buggy and poorly documented so I have not been able to get it to work with Python 3.10 yet.

## Pro Edition

An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) is also available with extra features 
like zoom and the ability to drag to connect shapes.

Simply download the regular builds and then purchase an rego key from [here](http://pynsource.com/pricing.html).

## Changelog

View the [Changelog](CHANGELOG.md)
