from ipaddress import IPv4Address, IPv6Address

import netifaces

from ddnswolf.models.address_update import AddressUpdate, IPv4AddressUpdate, IPv6AddressUpdate
from ddnswolf.sources.base import AddressSource


class InterfaceAddressSource(AddressSource):

    config_type_name = "interface"

    def __init__(self, *args, **kwargs):
        super(InterfaceAddressSource, self).__init__(*args, **kwargs)

    def provide_addresses(self) -> [AddressUpdate]:
        if self.config["iface"] not in netifaces.interfaces():
            raise Exception("Interface {} does not exist!".format(self.config["iface"]))

        # Interfaces can have any number of addresses, from any address family. This logic selects address families
        # that we can support and constructs an AddressUpdate for each address within that family.
        all_addresses = []
        for address_family, address_data_list in netifaces.ifaddresses(self.config["iface"]).items():
            # IPv4
            if address_family == netifaces.AF_INET:
                for address_data in address_data_list:
                    all_addresses.append(IPv4AddressUpdate(IPv4Address(address_data["addr"])))
            # IPv6
            elif address_family == netifaces.AF_INET6:
                for address_data in address_data_list:
                    # The netifaces library gives back link local addresses with their scope ID attached. The IPv6
                    # address model we use does not support this, we must manually strip it if present.
                    # An example of what we need to sanitize: 'fe80::547b:4b0:ac8c:61a3%wlp51s0'
                    addr: str = address_data["addr"]
                    if "%" in addr:
                        addr = addr[0:addr.find("%")]
                    all_addresses.append(IPv6AddressUpdate(IPv6Address(addr)))

        return all_addresses
