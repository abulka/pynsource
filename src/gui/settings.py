import os
import sys

# Test override: force Community Edition even when registered (or on Linux).
#   PYNSOURCE_FORCE_COMMUNITY=1 bin/run       (env var, works for GUI, CLI, tests)
#   bin/run --community                        (CLI flag, stripped from sys.argv here
#                                              so wx/click arg handling never sees it)
FORCE_COMMUNITY = False
if os.environ.get("PYNSOURCE_FORCE_COMMUNITY"):
    FORCE_COMMUNITY = True
if "--community" in sys.argv:
    FORCE_COMMUNITY = True
    sys.argv = [a for a in sys.argv if a != "--community"]

# The diagram canvas is free for everyone. PRO_EDITION now gates optional
# module visualisation (ALSM), which is the only paid feature.
PRO_EDITION = True
ALSM_PARSING = False
# True when Pro is free by platform (Linux) rather than licensed. The About box uses this so it
# does not advertise a paid licence to Linux users.
PRO_EDITION_FREE = False
ASYNC_BACKGROUND_REFRESH = False  # devel purposes only

APP_VERSION = 1.88

# PATCH marker does not affect version checking, its just an annotation in the about box.
# Use it with a future APP_VERSION to make betas e.g. "beta 2"
# Or use it with the current APP_VERSION to make post release patches e.g. "2"
PATCH = ""  # leave blank to turn off patch/beta annotation in about box

APP_VERSION_FULL = f"{APP_VERSION}"
if PATCH:
    APP_VERSION_FULL += f"-{PATCH}"

if FORCE_COMMUNITY:
    # Explicit test override wins over licence check and Linux force-Pro.
    PRO_EDITION = False
    registered_to = ""
    enter_license = lambda name, serial: None  # dummy function, same as no-rego case
    print(f"Running Community Edition (forced by --community / PYNSOURCE_FORCE_COMMUNITY)")
else:
    try:
        import rego
    except ModuleNotFoundError:
        # print("rego functionality not found")
        PRO_EDITION = False
        registered_to = ""
        enter_license = lambda name, serial: None  # dummy function when no rego library e.g. running from community source or snap
    else:
        PRO_EDITION = rego.are_registered(APP_VERSION)
        registered_to = rego.get_stored_serial_info()["name"] if rego.get_stored_serial_info() else ""
        enter_license = lambda name, serial: rego.enter_license(name, serial, APP_VERSION)

    # Linux editions are Pro-free: Pro is decided by platform, not by a licence file.
    #
    # Every Linux delivery route (AppImage, snap, distro package) ships with module
    # visualisation enabled. A licence file is not viable there: snaps cannot read
    # or write one (HOME is per-revision sandboxed, so registering would not survive
    # an update) and the various Linux packaging routes have no way to share one.
    # So on Linux we skip the licence check entirely - which also means the
    # AppImage/snap must bundle alsm (module visualisation).
    if sys.platform.startswith("linux"):
        PRO_EDITION = True
        PRO_EDITION_FREE = True
        registered_to = "Linux users"

if PRO_EDITION:
    try:
        import alsm
        # raise ModuleNotFoundError()
        ALSM_PARSING = True
    except ModuleNotFoundError:
        ALSM_PARSING = False
    if not ALSM_PARSING:
        print(f"Python Module Visualisation could not be enabled - 'alsm' package not installed 😳")
        if sys.platform.startswith("linux"):
            # Linux runs Pro by default, so this is the normal user-facing case, not a dev error
            print(f"  👉 Install it with: pip install alsm  (then restart Pynsource)")
        else:
            print(f"  👉 This is a config error when debugging and developing the PRO version of pynsource, which only the author can do.")
            print(f"  👉 Andy, please run: pip install ../alsm-parsers/alsm/ (see alsm README.md for more info)")

if not PRO_EDITION and not FORCE_COMMUNITY:
    print(f"Running Community Edition")

# APP_ICON_PATH = "/home/andy/.pyenv/versions/3.7.1/lib/python3.7/site-packages/wx/py/Py.ico"
APP_ICON_PATH = "media/pynsource.ico"

LOG_TO_CONSOLE = False
