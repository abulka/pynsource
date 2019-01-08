# import wx
import os

PYNSOURCE_CONFIG_FILE = "pynsource.ini"
PYNSOURCE_CONFIG_DIR = "PyNSource"


def InitConfig():
    # config_dir = os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), PYNSOURCE_CONFIG_DIR)
    config_dir = "."
    try:
        os.makedirs(config_dir)
    except OSError:
        pass
    user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
    print("Pynsource config file", user_config_file)

    # shelf = shelve.open(user_config_file)
    # shelf["users"] = ["David", "Abraham"]
    # shelf.sync() # Save

    from configobj import ConfigObj  # easy_install configobj

    config = ConfigObj(
        user_config_file
    )  # doco at http://www.voidspace.org.uk/python/configobj.html
    print(config)
    config["keyword1"] = 100
    config["keyword2"] = "hi there"
    value1 = config["keyword1"]
    value2 = config["keyword2"]
    # config['section1']['keyword3'] = "hi there"
    print(config)
    config.write()


print("hi")
InitConfig()
