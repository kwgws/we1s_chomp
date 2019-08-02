from setuptools import setup

import we1s_chomp


setup(
    name=we1s_chomp.__name__,
    version=we1s_chomp.__version__,
    description=we1s_chomp.__description__,
    author=we1s_chomp.__author__,
    author_email=we1s_chomp.__email__,
    packages=[we1s_chomp.__name__],
    install_requires=[
        "beautifulsoup4",
        "bleach",
        "dateparser",
        "html5lib",
        "nbfilter",
        "regex",
        "requests",
        "selenium",
        "unidecode",
    ],
    license=we1s_chomp.__license__,
    url=we1s_chomp.__url__,
)
