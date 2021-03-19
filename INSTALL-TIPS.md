# Fedora installation tips

Fedora Linux Users: can use the script `bin/install-linux-fedora-33` in conjunction with Python 3.8. There is no wxpython wheel for Python 3.9 so simply install Python 3.8 using [pyenv](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) e.g.

    $ sudo dnf install make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel
    $ curl https://pyenv.run | bash

Remember to update your `.bashrc` and restart your shell. 

Now that `pyenv` is installed, install a version of Python

    $ sudo dnf install python3-devel
    $ PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.8.8

Now that a specific version of Python is installed, activate it globally or just locally

    $ cd pynsource
    $ pyenv local 3.8.8

Run the script that installs Pynsource and its dependencies

    $ bin/install-linux-fedora-33

Finally, run Pynsource

    $ bin/run

Alternatively run the prebuilt [Fedora Pynsource binary](https://github.com/abulka/pynsource/releases/download/version-1.77/pynsource-1.77-fedora-33.zip) from the terminal like this

    `./Pynsource`

and it should start up ok, even though it is of a type `application/x-sharedlib`. Unfortunately double clicking on the executable from file manager in Fedora doesn't seem to work.
