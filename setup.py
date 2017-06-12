import subprocess
import sys

from setuptools import find_packages, setup


def get_long_description():
    cmd = "pandoc -f markdown_github -t rst README.md --no-wrap"
    try:
        return subprocess.check_output(cmd, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError:
        return ""

VERSION = "1.0.0"

setup(
    name="libweb",
    version=VERSION,
    author="Steve McMaster",
    author_email="mcmaster@hurricanelabs.com",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    zip_safe=False,
    url="http://python-libweb.readthedocs.org",
    description="Python Web Service Parsing Library",
    long_description=get_long_description(),
    install_requires=[
        "dnspython" if sys.version_info[0] == 2 else "dnspython3",
        "requests",
        "defusedxml",
        "lxml",
        "html5lib",
        "jsonpath-rw-ext",
        "relatime",
        "tzlocal",
        "filemagic",
        # "feedparser",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
    ],
    bugtrack_url="https://github.com/HurricaneLabs/libweb/issues",
)
