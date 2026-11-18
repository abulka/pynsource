"""
Legacy setuptools metadata: `uv build` and `pip install .` use this. The PyInstaller builds in
CI do not - they run the spec directly.

Version is scraped from src/gui/settings.py so the sdist and the about box agree, and
install_requires is requirements.txt verbatim (one requirements file for the venv and the
package). Linux users must install a wxPython wheel before this pulls wxpython, because there
are none on PyPI - see BUILDING.md, "Linux and wxPython".
"""

import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent

# Scraped rather than imported: src/gui/settings.py sets up logging and imports rego/appdirs at
# import time, which the isolated build environment does not have.
APP_VERSION = re.search(
    r"^APP_VERSION = ([\d.]+)",
    (ROOT / "src" / "gui" / "settings.py").read_text(),
    re.MULTILINE,
).group(1)

requirements = [
    line
    for line in (
        stripped.strip()
        for stripped in (ROOT / "requirements.txt").read_text().splitlines()
    )
    if line and not line.startswith("#")
]

setup(
    name="pynsource",
    version=APP_VERSION,
    url="https://github.com/abulka/pynsource",
    author="Andy Bulka",
    author_email="abulka@gmail.com",

    py_modules=["pynsource_gui", "pynsource_cli"],

    # You need both entries because packages tells setuptools to include all packages found
    # under src, while package_dir tells it to use src as the root of the package hierarchy.
    # Without package_dir setuptools would look for packages relative to the project root;
    # without packages it would include none of them.
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pynsource=pynsource_gui:run",
            "pynsource-cli=pynsource_cli:reverse_engineer",
        ],
    },
)
