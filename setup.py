#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
# Website: https://nexuzy.in
#
# Licensed under the MIT License. See the LICENSE file in the project
# root for the full license text.
# --------------------------------------------------------------------

"""Packaging metadata for Nexuzy Sheet."""

from setuptools import setup, find_packages

from nxsheet import (VERSION, COMPANY, COMPANY_URL, SUPPORT_EMAIL,
                     LICENSE_NAME)

with open("README.md", "r", encoding="utf8") as readme_file:
    long_description = readme_file.read()

setup(
    name="nxsheet",
    version=VERSION,
    author=COMPANY,
    author_email=SUPPORT_EMAIL,
    description="Nexuzy Sheet is an Excel-like spreadsheet workspace written "
                "in Python with PyQt6.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=COMPANY_URL,
    project_urls={
        "Website": COMPANY_URL,
        "Source Code": "https://github.com/david0154/nexuzy-sheet",
        "Bug Tracker": "https://github.com/david0154/nexuzy-sheet/issues",
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": {
            "nxsheet = nxsheet.main:main",
            "nexuzy-sheet = nxsheet.main:main",
        }
    },
    package_data={"nxsheet": [
            "share/*",
            "share/*/*",
            "share/*/*/*",
            "share/*/*/*/*",
            "share/*/*/*/*/*",
        ]
    },
    data_files=[
        ("share/applications", ["nxsheet.desktop"]),
    ],
    license=LICENSE_NAME,
    keywords=["spreadsheet", "excel", "nxsheet", "nexuzy", "xlsx", "csv"],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.1",
        "PyQt6>=6.4",
        "markdown2>=2.3",
        "pymupdf>=1.23.0",
    ],
    extras_require={
        "matplotlib": ["matplotlib>=1.1.1"],
        "pyenchant": ["pyenchant>=1.1"],
        "dateutil": ["python-dateutil>=2.7.0"],
        "money": ["py-moneyed>=2.0"],
        "excel-import": ["openpyxl>=3.0.7", "pycel>=1.0b30"],
        "rpy2": ["rpy2>=3.4"],
        "plotnine": ["plotnine>=0.8"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering",
    ],
)
