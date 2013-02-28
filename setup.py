import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a
# top level
# README file and 2) it's easier to type in the README file than to put
# a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
#### METADATA ####
    # Package name
    name = "pysms",
    # Package version
    version = "0.2",
    # Author description
    author = "Jaka Hudoklin",
    author_email = "jakahudoklin@gmail.com",
    # Package description
    description = ("Python library for sending sms-es"),
    long_description = read('README.md'),
    # Package license
    license = "GNU",
    # Searh data
    keywords = "sms send nexmo najdisi",
    url = "https://github.com/offlinehacker/pysms",
    # Package classifiers
    classifiers = [
        # Dev phase
        "Development Status :: 4 - Beta",

        # Topic
        "Topic :: Communications :: Chat",
        "Topic :: Communications :: Telephony",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",

        # Language
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",

        # License
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    # Install requierments
    install_requires = [
        "six",
        "phonenumbers",
        "colander",

        "mechanize",

        "pyserial",
        "smspdu"
    ],
    tests_require = [
        "stubserver",
        "mock"
    ],

### Installation speciffic ###
    test_suite="pysms.tests",
    packages = find_packages(),
)
