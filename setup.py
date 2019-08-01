"""WE1S Chomp: A Digital Humanities Web Scraper

For detailed documentation and instructions, see:
- http://we1s.ucsb.edu/
- https://github.com/seangilleran/we1s_chomp
"""

from setuptools import setup

setup(
    name="we1s_chomp",
    version="0.1.0",
    description="A Digital Humanities Web Scraper",
    author="Sean Gilleran",
    author_email="sgilleran@gmail.com",
    packages=["we1s_chomp"],
    install_requires=[
        "beautifulsoup4",
        "bleach",
        "dateparser",
        "html5lib",
        "nbfilter",
        "regex",
        "requests",
        "selenium",
        "unidecode"
    ],
    license="MIT",
    url="https://github.com/seangilleran/we1s_chomp",
)
