from ipaddress import IPv4Address, IPv6Address


class AddressUpdate:
    """
    An update of one of the address sources that DNSDen is monitoring. Most often this update will represent an address
    on a network interface. The address identified by this update may not be an "updated" address, i.e. this object will
    be created regardless of if the address actually changed or not.

    For address types other than IPv4 and IPv6, subclass this and add it to your protocol file.
    """

    def __init__(self, update_source):
        """:param update_source: """
        # TODO Add type to update_source
        self.update_source = update_source


class IPv4AddressUpdate:
    """An update for an Internet Protocol version 4 address."""

    def __init__(self, address: IPv4Address):
        self.address = address


class IPv6AddressUpdate:
    """An update for an Internet Protocol version 6 address."""

    def __init__(self, address: IPv6Address):
        self.address = address
