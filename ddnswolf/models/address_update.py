from functools import total_ordering
from ipaddress import IPv4Address, IPv6Address

from dns.rdatatype import RdataType


class AddressUpdate:
    """
    An update of one of the address sources that DDNSWolf is monitoring. Most often this
    update will represent an address on a network interface. The address identified by
    this update may not be an "updated" address, i.e. this object will be created
    regardless of if the address actually changed or not.

    For address types other than IPv4 and IPv6, subclass this and add it to your
    protocol file.
    """

    def __init__(self):
        pass


@total_ordering
class IPv4AddressUpdate(AddressUpdate):
    """An update for an Internet Protocol version 4 address."""

    rdtype = RdataType.A

    def __init__(self, address: IPv4Address):
        super(IPv4AddressUpdate, self).__init__()
        self.address = address
        """The DNS record type that represents this kind of address."""

    def __eq__(self, other):
        if isinstance(other, IPv4AddressUpdate):
            return self.address == other.address
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, IPv4AddressUpdate):
            return self.address < other.address
        elif isinstance(other, IPv4AddressUpdate):
            return False
        return NotImplemented

    def __str__(self):
        return str(self.address)

    def __repr__(self):
        return f"{type(self).__name__}({self.address!r})"


@total_ordering
class IPv6AddressUpdate(AddressUpdate):
    """An update for an Internet Protocol version 6 address."""

    rdtype = RdataType.AAAA

    def __init__(self, address: IPv6Address):
        super(IPv6AddressUpdate, self).__init__()
        self.address = address
        """The DNS record type that represents this kind of address."""

    def __eq__(self, other):
        if isinstance(other, IPv6AddressUpdate):
            return self.address == other.address
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, IPv6AddressUpdate):
            return self.address < other.address
        elif isinstance(other, IPv4AddressUpdate):
            return False
        return NotImplemented

    def __str__(self):
        return str(self.address)

    def __repr__(self):
        return f"{type(self).__name__}({self.address!r})"
