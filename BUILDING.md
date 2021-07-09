### To run from source code ###

You need Python 3.6 or higher. Running with later versions of Python gives you the ability to parse newer Python syntax e.g. importing code into Pynsource containing the [walrus operator](https://realpython.com/lessons/assignment-expressions/) needs at least Pynsource running under Python 3.8 to work. 

> Note Pynsource relies on the package [typed-ast](https://pypi.org/project/typed-ast/) for the ability to parse *both* Python 2 and Python 3. This package takes a while to get updated when a new Python gets released, so you might want to play it safe and run via Python 3.9 when Python 3.10 comes out.

For Mac or Windows run the following commands:

    $ git clone https://github.com/abulka/pynsource.git
    $ cd pynsource
    $ pip3 install -r requirements.txt
    $ ./bin/run           (Mac, Linux) or
    $ .\bin\run-win10.bat (Windows 10)

For installing under Linux, run the provided script (more information below).

If you have installed from requirements.txt and still getting errors, you might need to update your pip packages to the latest versions. For example on Mac or Linux you can run `pip install $(pip list --outdated --format=columns |tail -n +3|cut -d" " -f1) --upgrade`. Note this bash command can upgrade some packages too high (pip dependency resolver is not smart) e.g. `idna` 3.2 is too high for `requests`, in which case to repair the situation uninstall both `pip uninstall requests idna` then just install `pip install requests` which fixes things.

Ubuntu Linux Users: Please use the script `bin/install-linux-18.04` to pip install needed Ubuntu dependencies, including a wxPython wheel specific to `Ubuntu 18.04`. Use the script `bin/install-linux-20.04` if you are installing on `Ubuntu 20.04`.  If you are using a different version of Ubuntu simply copy and edit the script `bin/install-linux-nn.nn` and change the url of wxpython accordingly, to contain the ubuntu distro version number. Browse the wxpython versions available [here](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/).

Fedora Linux Users: can use the script `bin/install-linux-fedora-33` see [detailed steps](INSTALL-TIPS.md).

### A note on wxPython

The GUI toolkit [wxpython](https://wxpython.org/) that `Pynsource` relies on  needs a ‘proper’ **framework/shared** Python environment to run in, which ideally means using your main Python e.g. brew Python on a Mac or an official install from python.org for Windows 10. The default Python 3 on Ubuntu 18.04 is fine too. 

If you need to use a virtual environment I recommend that you use `pyenv` to first install the version of python that you need. You must use a [pyenv](https://github.com/pyenv/pyenv) framework/shared Python environment for building and running Pynsource. To achieve this, pass a special flag when installing Python through `pyenv` - see [this issue](https://github.com/abulka/pynsource/issues/68#issuecomment-605612292) for more info. E.g. `PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.8.6` on Mac or e.g. `PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.8.8` on linux.  When running under vscode, ensure you enter the path to the python interpreter correctly, to work around a [subtle vscode issue](https://github.com/microsoft/vscode-python/issues/16604).

Or simply use the ready-to-go prebuilt binary executables 🎉 - see [Downloads](DOWNLOADS.md)
