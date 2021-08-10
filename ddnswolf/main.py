import logging
import importlib.resources
import os.path
import time
from datetime import timedelta, datetime
from typing import List

from pyhocon import ConfigFactory, ConfigTree, ConfigException

import ddnswolf.version
from ddnswolf import util
from ddnswolf.exceptions import (
    DDNSWolfUserException,
    DDNSWolfProgramException,
    log_exception,
)
from ddnswolf.filters.base import AddressFilter
from ddnswolf.protocols.base import DynamicDNSUpdater
from ddnswolf.sources.base import AddressSource


logger = logging.getLogger(None)


class DDNSWolfApplication:
    def __init__(
        self,
        sources: List[AddressSource],
        updaters: List[DynamicDNSUpdater],
        check_interval: timedelta,
    ):
        self.sources = sources
        self.updaters = updaters
        self.check_interval = check_interval
        self.active = False

    def run(self):
        self.active = True
        last_update = datetime.min
        while self.active:
            now = datetime.now()
            if last_update + self.check_interval <= now:
                self.update_now()
                last_update = now
            else:
                time.sleep(((last_update + self.check_interval) - now).total_seconds())

    def update_now(self) -> None:
        """
        Runs all updaters. Current implementation is to defer to
        .update_from_subscriptions()
        """
        for updater in self.updaters:
            updater.update_from_subscriptions()

    @classmethod
    def from_config(
        cls, config: ConfigTree = None, config_path: str = None
    ) -> "DDNSWolfApplication":
        """
        Create a DDNSWolfApplication from a configuration file. Errors in the
        configuration will not be tolerated. An exception will be raised if there are
        problems. The init from config path is separated from the actual init path to
        allow the use of this program as a library to make one's own updater, without
        being restricted to a particular configuration format.
        """
        # Read config from file if needed.
        if config is None:
            config = cls.read_config(config_path)

        # Global options.
        check_interval = timedelta(seconds=config.get_int("check_interval_seconds"))

        # Load source objects.
        util.import_all_submodules("ddnswolf.sources")
        source_classes = {
            source_cls.config_type_name: source_cls
            for source_cls in util.find_all_subclasses(AddressSource)
        }
        sources = {}
        for source_name, source_config in config.get_config("sources").items():
            try:
                source_type_name = source_config.get_string("type")
                source_cls = source_classes[source_type_name]
                sources[source_name] = source_cls(source_name, source_config)
            except KeyError as ex:
                # noinspection PyUnboundLocalVariable
                raise DDNSWolfUserException(
                    f"Could not find a source with the type {source_type_name}."
                ) from ex

        # Load updater objects.
        util.import_all_submodules("ddnswolf.protocols")
        updater_classes = {
            updater_cls.config_type_name: updater_cls
            for updater_cls in util.find_all_subclasses(DynamicDNSUpdater)
        }
        updaters: List[DynamicDNSUpdater] = []
        for updater_name, updater_config in config.get_config("updaters").items():
            try:
                updater_type_name = updater_config.get_string("type")
                updater_cls = updater_classes[updater_type_name]
                updaters.append(updater_cls(updater_name, updater_config))
            except KeyError as ex:
                # noinspection PyUnboundLocalVariable
                raise DDNSWolfUserException(
                    f"Could not find an updater with the name {updater_type_name}."
                ) from ex

        # Parse and connect updater subscriptions.
        #   "What the hell is this?" you may ask. This is an evil and amazing solution
        # to parsing a filter string. This is an example filter string:
        # "nth(1, ipv6(my_interface))". This filter gets the second IPv6 address of the
        # my_interface source. This format was chosen for its simplicity and ease of
        # understanding. Rather than write our own parser for this, we use Python's
        # knowledge of parsing functions and evaluate the filter string as a Python
        # expression.
        #   The filter names are each defined as a function that will construct the
        # appropriate filter object. Filters are converted to providers with
        # .as_provider() to enable chaining, such that the final object is a provider
        # that runs through all filters starting at the original source.
        #   For example, 'nth' will be a function that constructs a new NthAddressFilter
        # with the first argument as its index, and then converts it to a provider using
        # the second argument as the parent provider. Address sources are also defined
        # in the eval environment, to be the original provider for the chain. They are
        # left as themselves because they are already providers.
        subscription_eval_locals = {}
        subscription_eval_locals.update(sources)
        util.import_all_submodules("ddnswolf.filters")
        for filter_cls in util.find_all_subclasses(AddressFilter):

            def create_this_filter(*args):
                parent_source = args[-1]
                filter_args = args[0:-1]
                # We are performing an unsafe operation on purpose. Any mismatched
                # arguments will be caught by the filter constructor or during the
                # filter() call. The fault is on the configuring user, not us.
                # noinspection PyArgumentList
                return filter_cls(*filter_args).as_provider(parent_source)

            subscription_eval_locals[filter_cls.config_type_name] = create_this_filter

        for updater in updaters:
            for subscription_str in updater.config.get_list("subscriptions"):
                try:
                    computed_provider = eval(
                        subscription_str, {}, subscription_eval_locals
                    )
                    updater.subscribe(computed_provider)
                except NameError as ex:
                    raise DDNSWolfUserException(
                        f"Unknown filter or source: {ex}"
                    ) from ex

        return DDNSWolfApplication(list(sources.values()), updaters, check_interval)

    @staticmethod
    def read_config(config_path: str = None) -> ConfigTree:
        if config_path is not None:
            try_paths = [config_path]
        else:
            try_paths = [
                os.path.join(os.path.curdir, "ddnswolf.conf"),
                os.path.abspath(os.path.join(os.path.sep, "etc", "ddnswolf.conf")),
            ]

        first_valid_path = next(filter(os.path.exists, try_paths), None)
        if first_valid_path is None:
            raise DDNSWolfUserException(
                f"Unable to find a configuration. Attempted paths: "
                f"{', '.join(try_paths)}"
            )

        try:
            config = ConfigFactory.parse_file(first_valid_path)
        except ConfigException as ex:
            raise DDNSWolfProgramException(
                f"Unable to load configuration at {first_valid_path}"
            ) from ex
        if len(config) == 0:
            raise DDNSWolfUserException(f"Empty configuration at {first_valid_path}")

        return config


def main():
    # noinspection PyBroadException
    try:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s/%(name)s %(message)s"
        )
        logger.info(
            "\n" + importlib.resources.read_text("ddnswolf", "logo.txt", "utf-8")
        )
        logger.info(f"== DDNSWolf version {ddnswolf.version.get_full_version()} ==")
        app = DDNSWolfApplication.from_config()
        app.run()
    except Exception as ex:
        log_exception(logger, ex)


if __name__ == "__main__":
    main()
