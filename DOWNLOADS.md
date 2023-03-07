# Download Pynsource 

The latest version is `1.84`

[Download](https://github.com/abulka/pynsource/releases/latest) the latest stable release. 👈

Python 3.10 syntax is now supported - see [1.85 beta 2 release](https://github.com/abulka/pynsource/releases/tag/pre-70)

## Mac

Unzip and drag app into the Applications directory.

Mac users please [right click open](https://www.howtogeek.com/205393/gatekeeper-101-why-your-mac-only-allows-apple-approved-software-by-default/) the first time. 
Mac Big Sur, Monterey, Ventura users need to first `xattr -dr com.apple.quarantine /Applications/Pynsource.app`. 

> 🎉 Easier Technique for Mac Users: Right click on the supplied bash script `fix-permissions.command` and choose "Open" to apply the correct permissions to `Pynsource`.
> Then you can copy the app to you Applications/ folder and run it as normal.

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
