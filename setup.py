#!/bin/env python3
# Setuptools stub. See setup.cfg

import os.path
import setuptools

from setuptools.command.build_py import build_py as setuptools_build_py


class DDNSWolfBuildCommand(setuptools_build_py):
    def run(self):
        setuptools_build_py.run(self)
        print("Running DDNSWolf custom build steps...")
        self.embed_static_version()

    def embed_static_version(self):
        module_file_name = os.path.join(self.build_lib, "ddnswolf", "version_static.py")
        print(f"Embedding static version -> {module_file_name}")
        with open(module_file_name, "w") as module_file:
            from ddnswolf import version as ddnswolf_version

            # noinspection PyProtectedMember
            module_file.write(ddnswolf_version._create_static_version_module())


setuptools.setup(
    # setup.cfg does not support defining custom build steps.
    cmdclass={
        "build_py": DDNSWolfBuildCommand,
    },
)
