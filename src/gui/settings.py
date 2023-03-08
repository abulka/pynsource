PRO_EDITION=True
ALSM_PARSING=False
NATIVE_LINES_OGL_LIKE=False
ASYNC_BACKGROUND_REFRESH=False  # devel purposes only

APP_VERSION = 1.84

# PATCH marker does not affect version checking, its just an annotation in the about box.
# Use it with a future APP_VERSION to make betas e.g. "beta 2"
# Or use it with the current APP_VERSION to make post release patches e.g. "2"
PATCH = "patched to use python 3.10 - beta2"  # leave blank to turn off patch/beta annotation in about box

LOCAL_OGL = True # use local copy of ogl.py, otherwise use wxPython's

APP_VERSION_FULL = f"{APP_VERSION}"
if PATCH:
    APP_VERSION_FULL += f"-{PATCH}" 

try:
    import rego
except ModuleNotFoundError:
    # print("rego functionality not found")
    PRO_EDITION=False
    registered_to = ""
    enter_license = lambda name, serial : None # dummy function when no rego library e.g. running from community source or snap
else:
    PRO_EDITION = rego.are_registered(APP_VERSION)
    registered_to = rego.get_stored_serial_info()["name"] if rego.get_stored_serial_info() else ""
    enter_license = lambda name, serial : rego.enter_license(name, serial, APP_VERSION)

if PRO_EDITION:
    try:
        import alsm
        # raise ModuleNotFoundError()
        ALSM_PARSING = True
    except ModuleNotFoundError:
        ALSM_PARSING = False
    if not ALSM_PARSING:
        print(f"Python Module Visualisation could not be enabled - 'alsm' package not installed 😳")
        print(f"  👉 This is a config error when debugging and developing the PRO version of pynsource, which only the author can do.")
        print(f"  👉 Andy, please run: pip install ../alsm-parsers/alsm/ (see alsm README.md for more info)")

if not PRO_EDITION:
    print(f"Running Community Edition")

# APP_ICON_PATH = "/home/andy/.pyenv/versions/3.7.1/lib/python3.7/site-packages/wx/py/Py.ico"
APP_ICON_PATH = "media/pynsource.ico"

LOG_TO_CONSOLE = False
