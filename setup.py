#!/bin/env python3
# https://setuptools.readthedocs.io/en/latest/

from setuptools import setup, find_namespace_packages


setup(
    name="ddnswolf",
    version="0",
    author="Wolfizen",
    author_email="wolfizen@wolfizen.net",
    description="Dynamic DNS updater",
    url="https://wolfizen.net/ddnswolf",
    license="GPLv3+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    packages=find_namespace_packages(include=["ddnswolf.*"]),
)
