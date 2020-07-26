from ipaddress import IPv4Address, IPv6Address

from dns.rdatatype import RdataType


class AddressUpdate:
    """
    An update of one of the address sources that DNSDen is monitoring. Most often this update will represent an address
    on a network interface. The address identified by this update may not be an "updated" address, i.e. this object will
    be created regardless of if the address actually changed or not.

    For address types other than IPv4 and IPv6, subclass this and add it to your protocol file.
    """

    def __init__(self):
        pass


class IPv4AddressUpdate(AddressUpdate):
    """An update for an Internet Protocol version 4 address."""

    def __init__(self, address: IPv4Address):
        super(IPv4AddressUpdate, self).__init__()
        self.address = address
        self.rdtype = RdataType.A
        """The DNS record type that represents this kind of address."""


class IPv6AddressUpdate(AddressUpdate):
    """An update for an Internet Protocol version 6 address."""

    def __init__(self, address: IPv6Address):
        super(IPv6AddressUpdate, self).__init__()
        self.address = address
        self.rdtype = RdataType.AAAA
        """The DNS record type that represents this kind of address."""
