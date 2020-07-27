from abc import ABC

from pyhocon import ConfigTree

from dnsden.models.address_provider import AddressProvider


class AddressSource(AddressProvider, ABC):
    """
    Provides a source of one or more addresses that providers can pull from. When the address of a source changes,
    all providers referencing the source will be

    Address sources
    """

    def __init__(self, config: ConfigTree):
        super(AddressSource, self).__init__()
        self.config = config
