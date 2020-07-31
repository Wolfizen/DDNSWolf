import ipaddress
from abc import ABC
from typing import Union

from dns import resolver
from dns.rdataclass import RdataClass
from pyhocon import ConfigTree

from dnsden.models.address_update import IPv4AddressUpdate, IPv6AddressUpdate


class DynamicDNSUpdater(ABC):
    """
    The base class for all updaters provided by DNSDen. An updater represents a specific configuration of a dynamic DNS
    service, with its own authentication token and target hostname. An updater is generally responsible for updating a
    single name within a single service/protocol.
    """

    config_type_name: str = NotImplemented
    """
    This class variable defines the name to use in the program configuration to reference this updater. There can only
    be one name per updater, and it cannot conflict with any other updater. This is different from the instance name,
    which refers to the custom identifier given to a particular instance of an updater.
    """

    def __init__(self, name: str, config: ConfigTree):
        self.name = name
        """
        The instance name of this updater. This is set by the user, and uniquely identifies this particular instance
        within the global config.
        """
        self.config = config
        """
        The config for this updater. This config is a local view of only the options for this instance. Use it however
        you want, but consider using the standard names of common fields. Check other protocols for reference.
        """

    def update(self, address_update) -> None:
        """
        Ask the service to change the address of the configured name to be the address in the update. This method should
        not check if the address needs changing, that is done in needs_update().

        :abstract
        :return: None
        :raises If the update was unable to be executed.
        """
        raise NotImplementedError("FIXME: Unimplemented update() in {}".format(type(self).__name__))

    def needs_update(self, address_update: Union[IPv4AddressUpdate, IPv6AddressUpdate]) -> bool:
        """
        Checks if the name configured in this updater has a different address than the provided address and thus
        needs to be updated. Throws an exception if an answer can't be determined.

        Defaults to a simple DNS resolution, supporting IPv4 and IPv6 addresses. For other classes, or other record
        types, override this method.

        It is generally recommended to override this method with an API call to whatever service the updater represents.
        The DNS will not provide as timely an answer as directly asking the authoritative source.

        :param address_update: The address being checked.
        :return True if the address needs updating, False if it does not.
        :raises If it is unknown whether the address needs updating or not.
        """

        if not isinstance(address_update, IPv4AddressUpdate) or isinstance(address_update, IPv6AddressUpdate):
            raise Exception("Unsupported address update for {}: {}".format(type(self).__name__, address_update))

        # Use the system default resolver.
        answers = resolver.resolve(self.config["name"], address_update.rdtype, RdataClass.IN)
        for answer in answers:
            if answer.rdtype == address_update.rdtype:
                return ipaddress.ip_address(answer.address) != address_update.address
        # Assume no RR of the correct type means it needs updating.
        return True
