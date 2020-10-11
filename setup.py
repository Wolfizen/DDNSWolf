#!/bin/env python3

import os.path
import setuptools

from setuptools.command.build_py import build_py as setuptools_build_py

import ddnswolf.version


class CustomBuildCommand(setuptools_build_py):
    def run(self):
        setuptools_build_py.run(self)
        print("Running DDNSWolf custom build steps...")
        self.embed_static_version()

    def embed_static_version(self):
        module_file_name = os.path.join(self.build_lib, "ddnswolf", "version_static.py")
        print(f"Embedding static version -> {module_file_name}")
        with open(module_file_name, "w") as module_file:
            # noinspection PyProtectedMember
            module_file.write(ddnswolf.version._create_static_version_module())


setuptools.setup(
    name="ddnswolf",
    fullname="DDNSWolf",
    version=ddnswolf.version.calculate_full_version(),
    description="Dynamic DNS updater",
    author="Wolfizen",
    author_email="wolfizen@wolfizen.net",
    url="https://wolfizen.net/ddnswolf",
    license="GPLv3+",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    python_requires=">=3.6",
    install_requires=[
        "cloudflare~=2.8",
        "dnspython~=2.0",
        "GitPython~=3.1",
        "netifaces~=0.10",
        "pyhocon~=0.3",
        "requests~=2.24",
    ],
    packages=setuptools.find_namespace_packages(include=["ddnswolf*"]),
    entry_points={
        "console_scripts": [
            "ddnswolf = ddnswolf.main:main"
        ]
    },
    data_files=[
        ("/etc", ["ddnswolf.conf"]),
    ],
    cmdclass={
        "build_py": CustomBuildCommand,
    }
)
