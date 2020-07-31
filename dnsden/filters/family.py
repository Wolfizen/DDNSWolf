from dnsden.filters.base import AddressFilter
from dnsden.models.address_update import AddressUpdate, IPv4AddressUpdate, IPv6AddressUpdate


class IPv4AddressFilter(AddressFilter):
    """Selects only IPv4 addresses."""

    config_type_name = "ipv4"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """Selects only IPv4 addresses. The relative ordering of the IPv4 addresses is left as-is."""
        return filter(lambda a: isinstance(a, IPv4AddressUpdate), addresses)


class IPv6AddressFilter(AddressFilter):
    """Selects only IPv6 addresses."""

    config_type_name = "ipv6"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """Selects only IPv6 addresses. The relative ordering of the IPv6 addresses is left as-is."""
        return filter(lambda a: isinstance(a, IPv6AddressUpdate), addresses)
