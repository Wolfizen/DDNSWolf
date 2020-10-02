#!/bin/env python3

from setuptools import setup, find_namespace_packages


setup(
    name="ddnswolf",
    version="0",
    author="Wolfizen",
    author_email="wolfizen@wolfizen.net",
    description="Dynamic DNS updater",
    url="https://wolfizen.net/ddnswolf",
    packages=find_namespace_packages(include=["ddnswolf.*"]),
)
