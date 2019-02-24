PRO_EDITION=True
NATIVE_LINES_OGL_LIKE=False
ASYNC_BACKGROUND_REFRESH=False  # devel purposes only
APP_VERSION = 1.71

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

