import os
from setuptools import setup, find_packages
import sys
print(sys.path)
print("on linux please run: sudo apt-get install dpkg-dev build-essential python3-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev")
with open('.requirement-extras/requirements-linux-22.txt') as f:
    requirements = f.read().splitlines()
setup(
    name='pynsource',
    version='1.0.0',
    url='https://github.com/abuka/pynsource',
    author='Andy Bulka',
    author_email='abulka@gmail.com',

    py_modules=['pynsource_gui'],

    # You need both entries because packages tells setuptools to include all
    # packages found under the src directory, while package_dir tells it to use
    # src as the root directory for the package hierarchy. Without package_dir,
    # setuptools would look for packages relative to the root directory of the
    # project, which would result in the packages not being found. Similarly,
    # without packages, setuptools would not include any packages in the
    # distribution, even though they would be found under src.    
    # 
    # packages=['common'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    # install_requires=[
    #     # Add your requirements here
    # ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pynsource=pynsource_gui:run',
            'pynsource-cli=pynsource_cli:reverse_engineer'
        ],
    },    
)
