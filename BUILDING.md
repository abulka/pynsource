# To run Pynsource from source code

You need Python 3.6 or higher. Running with later versions of Python gives you the ability to parse newer Python syntax e.g. importing code into Pynsource containing the [walrus operator](https://realpython.com/lessons/assignment-expressions/) needs at least Pynsource running under Python 3.8 to work. The latest tested version is Python 3.10.

> Note Pynsource relies on the package [typed-ast](https://pypi.org/project/typed-ast/) for the ability to parse *both* Python 2 and Python 3. This package takes a while to get updated when a new Python gets released, so you might want to play it safe and run via Python 3.10 when Python 3.11 comes out.

For Mac or Windows run the following commands:

    $ git clone https://github.com/abulka/pynsource.git
    $ cd pynsource
    $ pip3 install -r requirements.txt
    $ ./bin/run           (Mac, Linux) or
    $ .\bin\run-win10.bat (Windows 10)

For installing under Linux, run the provided script (more information below).

If you have installed from requirements.txt and still getting errors, you might need to update your pip packages to the latest versions. For example on Mac or Linux you can run `pip install $(pip list --outdated --format=columns |tail -n +3|cut -d" " -f1) --upgrade`. Note this bash command can upgrade some packages too high (pip dependency resolver is not smart) e.g. `idna` 3.2 is too high for `requests`, in which case to repair the situation uninstall both `pip uninstall requests idna` then just install `pip install requests` which fixes things.

## Ubuntu Linux Users

Latest 2023 approach: Build pynsource as a package - see [instructions below](#building-pynsource-as-a-package)

or...

Please use the script `bin/install-linux-18.04` to pip install needed Ubuntu dependencies, including a wxPython wheel specific to `Ubuntu 18.04`. Use the script `bin/install-linux-20.04` if you are installing on `Ubuntu 20.04`.  If you are using a different version of Ubuntu simply copy and edit the script `bin/install-linux-nn.nn` and change the url of wxpython accordingly, to contain the ubuntu distro version number. Browse the wxpython versions available [here](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/).

Fedora Linux Users: can use the script `bin/install-linux-fedora-33` see [detailed steps](INSTALL-TIPS.md).

## A note on wxPython

The GUI toolkit [wxpython](https://wxpython.org/) that `Pynsource` relies on  needs a ‘proper’ **framework/shared** Python environment to run in, which ideally means using your main Python e.g. brew Python on a Mac or an official install from python.org for Windows 10. The default Python 3 on Ubuntu 18.04 is fine too. 

If you need to use a virtual environment I recommend that you use `pyenv` to first install the version of python that you need. You must use a [pyenv](https://github.com/pyenv/pyenv) framework/shared Python environment for building and running Pynsource. To achieve this, pass a special flag when installing Python through `pyenv` - see [this issue](https://github.com/abulka/pynsource/issues/68#issuecomment-605612292) for more info. E.g. `PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.8.6` on Mac or e.g. `PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.8.8` on linux.  When running under vscode, ensure you enter the path to the python interpreter correctly, to work around a [subtle vscode issue](https://github.com/microsoft/vscode-python/issues/16604).

## latest wxpython installation tips
See also https://stackoverflow.com/questions/71821635/pip-cannot-install-wxpython-for-python-3-10-32-bit/75542856#75542856 on installing `wxpython` on linux.

Linux users: This approach happens to build the wxpython wheel ourselves rather than using the sometime limited choice of prebuilt wheels. This works on `intel x86` and also on ubuntu `arm` (tested on ubuntu arm virtual machine running under UTM on mac M1 processor). You will first need to run:

    $ sudo apt-get install dpkg-dev build-essential python3-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev

    $ pip install attrdict3 (see https://github.com/wxWidgets/Phoenix/issues/2225)


Or simply use the ready-to-go prebuilt binary executables of pynsource for all platforms, incl ubuntu, mint, popos (all ubuntu based) 🎉 - see [Downloads](DOWNLOADS.md)

## Running the tests

Download the source code, install the dependencies (see above) then

```
./bin/testall            (Mac, Linux) or
.\bin\testall-win10.bat  (Windows 10)
```

from the root of the project. You may need to alter the version of Python being invoked by the script e.g. `python` or `python3`.

The environment variable `TRAVIS` is set by the script to avoid tests that involve loading the wxPython package - this is especially needed on Travis and GitHub actions. It may also not be possible on your machine if you are running certain Python environments e.g. I had a problem with a framework pyenv install on my Mac running any tests that imported `wx`, even though Pynsource itself ran OK.  P.S. The subset of packages `requirements-travis.txt` is all you need to run the tests, and these exclude wx.

### Current Test Suite status

- Tests run through Travis, controlled by  `.travis.yml` ![Travis test status](https://github.com/abulka/pynsource/workflows/Python%20application/badge.svg)
- Tests also run through GitHub Actions, controlled by `.github/workflows/pythonapp.yml` ![Tests github actions workflow status](https://github.com/abulka/pynsource/actions/workflows/python-tests.yml/badge.svg)

# Building pynsource as a package

You can build pynsource as a package with

    $ python setup.py sdist
    
This will create a `dist` directory containing a `pynsource-<version>.tar.gz` file. You can then install this package with
    
    $ pip install dist/pynsource-<version>.tar.gz

or install in dev mode with 

    $ pip install -e .

which actually installs lots of packages.

Run with:

    pynsource

uninstall with

    $ pip uninstall pynsource

## Why do this?

Installing pynsource as a package gives you two entry points
    
        $ pynsource
        $ pynsource-cli

Typing `pynsource` will run the GUI - which might be an easier way to launch pynsource than invoking python etc.

Typing `pynsource-cli` is the command line interface. The command line interface is useful for batch processing of python files, e.g. to generate an analysis dump the structure of each python file. It won't produce diagrams though. So you can e.g. `pynsource-cli blah.py`.

## virtual environments

If you are using a virtual environment, ensure you install the package into the virtual environment. E.g. if you are using `pyenv` to manage your virtual environments, you can do this with    

    $ pyenv activate <your-virtual-env>
    $ pip install -e .
    $ pynsource

or if you are using venv

    $ source venv/bin/activate
    $ pip install -e .
    $ pynsource
