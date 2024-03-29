from ipaddress import IPv4Address, IPv6Address
from typing import Iterable

import netifaces

from ddnswolf.exceptions import DDNSWolfUserException
from ddnswolf.models.address_update import (
    AddressUpdate,
    IPv4AddressUpdate,
    IPv6AddressUpdate,
)
from ddnswolf.sources.base import AddressSource


class InterfaceAddressSource(AddressSource):
    """
    Provides addresses of local network interfaces. Interfaces can have any number of
    addresses, this source will return ALL of them. It is important to use address
    filters to select the appropriate address for your use.

    Interfaces are identified by their canonical "interface name." This is an OS-level
    concept and your particular OS will have its own naming scheme.
    """

    config_type_name = "interface"

    def __init__(self, *args, **kwargs):
        super(InterfaceAddressSource, self).__init__(*args, **kwargs)

    def provide_addresses(self) -> Iterable[AddressUpdate]:
        if self.config["iface"] not in netifaces.interfaces():
            raise DDNSWolfUserException(
                f"Interface {self.config['iface']} does not exist!"
            )

        # Interfaces can have any number of addresses, from any address family. This
        # logic selects address families that we can support and constructs an
        # AddressUpdate for each address within that family.
        all_addresses = []
        for address_family, address_data_list in netifaces.ifaddresses(
            self.config["iface"]
        ).items():
            # IPv4
            if address_family == netifaces.AF_INET:
                for address_data in address_data_list:
                    all_addresses.append(
                        IPv4AddressUpdate(IPv4Address(address_data["addr"]))
                    )
            # IPv6
            elif address_family == netifaces.AF_INET6:
                for address_data in address_data_list:
                    # The netifaces library gives back link local addresses with their
                    # scope ID attached. The IPv6 address model we use does not support
                    # this, we must manually strip it if present. An example of what we
                    # need to sanitize: 'fe80::547b:4b0:ac8c:61a3%wlp51s0'
                    addr: str = address_data["addr"]
                    if "%" in addr:
                        addr = addr[0 : addr.find("%")]
                    all_addresses.append(IPv6AddressUpdate(IPv6Address(addr)))

        return all_addresses
