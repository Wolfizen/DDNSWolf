from abc import ABC

from pyhocon import ConfigTree

from ddnswolf.models.address_provider import AddressProvider


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

    def __init__(self, name: str, config: ConfigTree):
        super(AddressSource, self).__init__()
        self.name = name
        """
        The instance name of this source. This is set by the user, and uniquely identifies this particular instance
        within the global config.
        """
        self.config = config
        """
        The config for this source. This config is a local view of only the options for this instance. Use it however
        you want, but consider using the standard names of common fields. Check other sources for reference.
        """

    # From AddressProvider: provide_addresses(self) -> Iterable[AddressUpdate]:
