import ipaddress
import itertools
from abc import ABC
from typing import Union, List

from dns import resolver
from dns.rdataclass import RdataClass
from pyhocon import ConfigTree

from ddnswolf.models.address_provider import AddressProvider
from ddnswolf.models.address_update import IPv4AddressUpdate, IPv6AddressUpdate, AddressUpdate


class DynamicDNSUpdater(ABC):
    """
    The base class for all updaters provided by DDNSWolf. An updater represents a specific configuration of a dynamic DNS
    service, with its own authentication token and target hostname. An updater is generally responsible for updating a
    single name within a single service/protocol.
    """

    config_type_name: str = NotImplemented
    """
    This class variable defines the name to use in the program configuration to reference this updater. There can only
    be one name per updater, and it cannot conflict with any other updater. This is different from the instance name,
    which refers to the custom identifier given to a particular instance of an updater.
    """

    def __init__(self, name: str, config: ConfigTree, subscriptions: List[AddressProvider] = None):
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
        self.subscriptions = subscriptions if subscriptions is not None else []
        """
        The active subscriptions for this updater. Updaters need a source for the addresses they are interested in.
        Each updater stores a list of the providers from which they want to receive and possibly update addresses.
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

    def subscribe(self, provider: AddressProvider) -> None:
        """
        Subscribes this updater to the provider. No automatic processing becomes scheduled as a part of this call, it
        merely appends the provider to this updater's list of subscriptions. Other logic must then cause the updates to
        happen, by either calling needs_update() then update(), or update_from_subscriptions() which will handle it all.
        """
        self.subscriptions.append(provider)

    def update_from_subscriptions(self) -> None:
        """
        Asks each subscription to provide addresses, collects them all into one list, cleans that list such that there
        is only one address per address family, and finally submits those addresses to be updated.

        It is important to clean the list of duplicate addresses per family, because most updater protocols allow only
        a single address per record type. If your updater supports that, override this method and change the behavior.
        The cleanup process picks the first global address for each subclass of AddressUpdate. If there are no public
        addresses, then the first address of any kind is picked.
        """
        print("Starting update for {}...".format(self.name))

        all_addresses = list(itertools.chain(*map(lambda p: p.provide_addresses(), self.subscriptions)))
        print("Addresses received from subscriptions: {}.".format(", ".join(map(str, all_addresses))))

        cleaned_addresses = {}
        for addr in all_addresses:
            # Only one address per type allowed.
            if type(addr) not in cleaned_addresses:
                cleaned_addresses[type(addr)] = addr
            # Prefer global addresses over non-global ones.
            elif (isinstance(addr, IPv4AddressUpdate) or isinstance(addr, IPv6AddressUpdate))\
                    and addr.address.is_global and not cleaned_addresses[type(addr)].address.is_global:
                cleaned_addresses[type(addr)] = addr
        if sorted(all_addresses) != sorted(cleaned_addresses.values()):
            print("!! Some addresses were removed, subscriptions provided multiple within the same family.")

        for addr in cleaned_addresses.values():
            # noinspection PyBroadException
            try:
                if self.needs_update(addr):
                    print("Sending update for address {}.".format(addr))
                    self.update(addr)
                else:
                    print("Update not needed for address {}.".format(addr))
            except Exception as ex:
                print("An error occurred while updating address {}: {}.".format(addr, ex))

        print("Update finished for {}.".format(self.name))
