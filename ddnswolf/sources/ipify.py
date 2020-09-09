from ipaddress import IPv4Address, IPv6Address
from typing import Iterable

import requests

from ddnswolf.models.address_update import AddressUpdate, IPv4AddressUpdate, IPv6AddressUpdate
from ddnswolf.sources.base import AddressSource


class IPIfyAddressSource(AddressSource):
    """
    Obtains the public IP address of a host from the perspective of an external service.
    The service used is https://www.ipify.org/

    This source has no configuration.
    """

    config_type_name = "ipify"

    def __init__(self, *args, **kwargs):
        super(IPIfyAddressSource, self).__init__(*args, **kwargs)

    def provide_addresses(self) -> Iterable[AddressUpdate]:
        addresses = []

        # IPv4
        try:
            response_v4 = requests.get("https://api.ipify.org")
            if response_v4.status_code == 200:
                address_v4 = IPv4AddressUpdate(IPv4Address(response_v4.text))
                addresses.append(address_v4)
                print(f"IPv4 address received from ipify: {address_v4}.")
            else:
                print(f"Unexpected response from ipify IPv4: {response_v4}.")
        except requests.exceptions.ConnectionError:
            print("No IPv4 address received from ipify.")
        # IPv6
        try:
            response_v6 = requests.get("https://api4.ipify.org")
            if response_v6.status_code == 200:
                address_v6 = IPv6AddressUpdate(IPv6Address(response_v6.text))
                addresses.append(address_v6)
                print(f"IPv6 address received from ipify: {address_v6}.")
            else:
                print(f"Unexpected response from ipify IPv6: {response_v6}.")
        except requests.exceptions.ConnectionError:
            print("No IPv6 address received from ipify.")

        return addresses
