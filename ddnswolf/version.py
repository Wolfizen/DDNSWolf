#!/bin/env python3
"""
Tools to calculate the current version identifier of the project. To use this file,
either import it in another python module and call calculate_full_version() or run this
file as a script.
"""
import logging
from abc import ABC
from importlib.util import spec_from_loader, module_from_spec

from pkg_resources import parse_version

logger = logging.getLogger(__name__)


release_version = "2"
"""
Public release number. This is used to identify releases, package versions, etc. This
is incremented every time the project is ready for a public release. The first commit
having a particular version number is the commit identified by that version. All later
commits with the same identifier are development builds, coming later in the order. 

DDNSWolf uses a modification of standard semantic versioning. Releases primarily
increment the major version number, using the minor version for hotfixes immediately
following release. "Bugfix" versions should never be used, preferring to
increment the minor version instead. Major releases with no lesser version numbers are
a single number with no ".0.0". Minor versions follow with no ".0" at the end.

Examples:
    First version: 1
    Update to third version: 3.1
"""


class VersionInfo(ABC):
    """
    This class knows how to find the other parts of the version specifier. The release
    version is known, but the build number and snapshot build status must be calculated
    based on the state of the project repository.

    See DynamicVersionInfo for implementation.
    """

    def is_snapshot_build(self) -> bool:
        """
        Determines if the current project state is a snapshot not tied to any particular
        commit.

        If the git repo has any change from HEAD (working directory or index) it is
        considered a snapshot.

        :return: True if the current state is a snapshot with no specific version.
        """
        return NotImplemented

    def get_build_number(self) -> int:
        """
        Calculate the development build number for the current state of the project.
        Build numbers are based on git history. The build number increments for each
        commit. The current build number is defined as the total number of commits above
        the current commit, plus one for the current commit, plus one if it is a
        snapshot. Initial-commit is build 1.

        This build number retains its lattice property for merge commits - the build
        number of a merge commit will be greater than the build numbers of each parent
        commit.

        :return: Current build number.
        """
        return NotImplemented

    def is_primary_release(self) -> bool:
        """
        Determines if the current project state is the first commit of a primary
        release. Only the first commit having a particular release version is the
        canonical commit identified by that version. Every commit after it (sharing the
        same release version) is a later version and needs a build number attached.

        If the logic of this function is substantially modified, such as changing the
        path of the version module, the release version MUST be incremented. If it is
        not, this function cannot know if it is a primary release when one or more of
        its parents are incompatible.

        :return: True if the current commit is the first commit having its release
                 version.
        """
        return NotImplemented

    def get_full_version(self) -> str:
        """
        Calculate the complete version identifier for the current state of the project.

        * If the current commit is the first commit of a release, then the version
          identifier is only that release. Example: `3`
        * If the current commit is not the first commit of a release, then the version
          identifier is the release plus the build number. Example: `10.4-r256`
        * If the current commit is a snapshot, then the version identifier is the
          version it would be if the current changes were committed plus the snapshot
          identifier.

        :return: The authoritative version number for the current commit.
        """
        version = release_version
        if not self.is_primary_release():
            version += f"-r{self.get_build_number()}"
        if self.is_snapshot_build():
            version += "-dev"
        return version


class DynamicVersionInfo(VersionInfo):
    """
    Gets version information from the state of the git repo.
    """

    def __init__(self):
        super(DynamicVersionInfo, self).__init__()
        # Deferred import to avoid importing a module that doesn't need to be present
        # in a deployed build.
        from git import Repo

        self.project_repo = Repo(path=None)

    def is_snapshot_build(self) -> bool:
        return self.project_repo.is_dirty(untracked_files=True)

    def get_build_number(self) -> int:
        return (
            # Bump for snapshot
            (1 if self.is_snapshot_build() else 0)
            # Current commit
            + 1
            # All ancestors
            + len(list(self.project_repo.head.commit.iter_parents()))
        )

    def is_primary_release(self) -> bool:
        if self.is_snapshot_build():
            # Treat snapshot builds as descending from HEAD
            parent_commits = [self.project_repo.head.commit]
        else:
            parent_commits = self.project_repo.head.commit.iter_parents()

        for parent_commit in parent_commits:
            try:
                parent_version_module = module_from_spec(
                    spec_from_loader(__name__ + "_dynamic", loader=None)
                )
                exec(
                    parent_commit.tree["ddnswolf"]["version.py"].data_stream.read(),
                    parent_version_module.__dict__,
                )
                # noinspection PyUnresolvedReferences
                if parse_version(
                    parent_version_module.release_version
                ) == parse_version(release_version):
                    return False
            except KeyError:
                # Parent does not have a version.py file, assume release is different.
                pass
        return True


class StaticVersionInfo(VersionInfo):
    """
    Gets version information from static values. Used when building the project
    as the built copy of the project will not have the git repo available.
    """

    def __init__(self, snapshot_build: bool, build_number: int, primary_release: bool):
        self.snapshot_build = snapshot_build
        self.build_number = build_number
        self.primary_release = primary_release

    def is_snapshot_build(self) -> bool:
        return self.snapshot_build

    def get_build_number(self) -> int:
        return self.build_number

    def is_primary_release(self) -> bool:
        return self.primary_release

    def __repr__(self) -> str:
        """
        :return: A valid python constructor that replicates this instance.
        """
        return (
            f"{type(self).__name__}({self.snapshot_build}, "
            f"{self.build_number}, "
            f"{self.primary_release})"
        )


class SimpleVersionInfo(VersionInfo):
    """
    If the git module fails to import, this class is the fallback.
    """

    def __init__(self):
        pass

    def is_snapshot_build(self) -> bool:
        return False

    def get_build_number(self) -> int:
        return 0

    def is_primary_release(self) -> bool:
        return True


def _create_static_version_module() -> str:
    """
    Generates a python module that contains a StaticVersionInfo copy of the current
    DynamicVersionInfo information.
    :return:
    """
    dynamic = DynamicVersionInfo()
    static = StaticVersionInfo(
        dynamic.is_snapshot_build(),
        dynamic.get_build_number(),
        dynamic.is_primary_release(),
    )
    return f"""
# Dynamically generated file! See ddnswolf.version

from ddnswolf.version import {StaticVersionInfo.__name__}


embedded_version_info = {repr(static)}
"""


def get_full_version() -> str:
    """
    CALL THIS TO GET THE PROJECT VERSION. If a StaticVersionInfo object is present
    in ddnswolf.version_static, it will be used. Otherwise use DynamicVersionInfo. If
    the git module is not available, a SimpleVersionInfo object will be used.
    """
    # Static version
    try:
        from . import version_static

        return version_static.embedded_version_info.get_full_version()
    except ImportError:
        # Dynamic version
        try:
            return DynamicVersionInfo().get_full_version()
        except ImportError:
            # Empty version
            logger.warning(
                "`git` module is missing. DDNSWolf cannot calculate an accurate"
                + " version number."
            )
            return SimpleVersionInfo().get_full_version()


if __name__ == "__main__":
    print(get_full_version(), end="")
