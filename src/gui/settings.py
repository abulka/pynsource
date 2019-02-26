import wx


PRO_EDITION=True
NATIVE_LINES_OGL_LIKE=False
ASYNC_BACKGROUND_REFRESH=False  # devel purposes only
APP_VERSION = 1.72

try:
    import rego
except ModuleNotFoundError:
    # print("rego functionality not found")
    PRO_EDITION=False
    registered_to = ""
else:
    PRO_EDITION = rego.are_registered(APP_VERSION)
    registered_to = rego.get_stored_serial_info()["name"] if rego.get_stored_serial_info() else ""
    enter_license = lambda name, serial : rego.enter_license(name, serial, APP_VERSION)

if not PRO_EDITION:
    print("Running Community Edition")


DEFAULT_COMMENT_FONT_SIZE = 10 if "wxGTK" in wx.PlatformInfo else 14
DEFAULT_CLASS_HEADING_FONT_SIZE = 12 if "wxGTK" in wx.PlatformInfo else 14
DEFAULT_CLASS_ATTRS_METHS_FONT_SIZE = 9 if "wxGTK" in wx.PlatformInfo else 10
DEFAULT_ASCII_UML_FONT_SIZE = 10 if "wxGTK" in wx.PlatformInfo else 14

# APP_ICON_PATH = "/home/andy/.pyenv/versions/3.7.1/lib/python3.7/site-packages/wx/py/Py.ico"
APP_ICON_PATH = "media/pynsource.ico"

