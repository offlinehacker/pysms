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
    name = "najdismsgw",
    version = "0.2",
    author = "Jaka Hudoklin",
    author_email = "jakahudoklin@gmail.com",
    description = ("Najdi.si sms gateway, that fetches mails using imap and sends then as smses."),
    license = "GNU",
    keywords = "najdi.si sms gateway",
    url = "https://github.com/offlinehacker/najdismsgw",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    entry_points="""
        [console_scripts]
        najdismsgw = najdismsgw.sender:main
        """,

)
