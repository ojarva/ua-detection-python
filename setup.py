import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "uaparser",
    version = "0.1.0",
    author = "Olli Jarva",
    author_email = "olli@jarva.fi",
    description = ("Library for parsing browser user agents"),
    license = "MIT",
    keywords = "browser user-agent parser",
    url = "https://github.com/ojarva/ua-detection-python",
    packages=['uaparser'],
    long_description=read('README.rst'),
    download_url = "https://github.com/ojarva/ua-detection-python",
    bugtracker_url = "https://github.com/ojarva/ua-detection-python/issues",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
)

