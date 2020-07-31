from abc import ABC

from pyhocon import ConfigTree

from dnsden.models.address_provider import AddressProvider


class AddressSource(AddressProvider, ABC):
    """
    Provides one or more addresses that updaters can pull from. When the address of a source changes,
    any objects subscribing to the source will be notified. Address sources are more specialized address providers
    that have a stanza in the program configuration, and have a smaller configuration of their own for each instance.

    Address sources may return any list of addresses they see fit. Address filters can be used by the consumer to
    select only certain addresses from the provided list.

    Examples of address sources include: an interface on the host, a public IP checker.
    """

    config_type_name: str = NotImplemented
    """
    This class variable defines the name to use in the program configuration to reference this address source. There can
    only be one name per source, and it cannot conflict with any other source. This is different from the instance name,
    which refers to the custom identifier given to a particular instance of a source.
    """

    def __init__(self, config: ConfigTree):
        super(AddressSource, self).__init__()
        self.config = config

    # From AddressProvider: provide_addresses(self) -> [AddressUpdate]:
