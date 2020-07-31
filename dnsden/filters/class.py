from dnsden.filters.base import AddressFilter
from dnsden.models.address_update import AddressUpdate, IPv4AddressUpdate, IPv6AddressUpdate


class PrivateAddressFilter(AddressFilter):
    """Selects addresses within the reserved private address range for its family. Supports only IPv4 and IPv6."""

    config_type_name = "private"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Selects private IPv4 or IPv6 addresses. Only addresses that are within the specifically designated multiple-use
        non-Internet routable blocks are considered private. The relative ordering of addresses is preserved.

        Addresses that are not IPv4 or IPv6 are not included in the result.

        The accuracy of this function depends on the implementation and recent updates of the official ipaddress module.
        """

        def is_private(a):
            if isinstance(a, IPv4AddressUpdate):
                return a.address.is_private
            elif isinstance(a, IPv6AddressUpdate):
                return a.address.is_private
            else:
                return False

        return filter(is_private, addresses)


class PublicAddressFilter(AddressFilter):
    """Selects addresses within the public address range for its family. Supports only IPv4 and IPv6."""

    config_type_name = "public"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Selects public IPv4 or IPv6 addresses. Only addresses that are within the specifically designated global
        Internet routable blocks are considered private. The relative ordering of addresses is preserved.

        Addresses that are not IPv4 or IPv6 are not included in the result.

        The accuracy of this function depends on the implementation and recent updates of the official ipaddress module.
        """

        def is_public(a):
            if isinstance(a, IPv4AddressUpdate):
                return a.address.is_private
            elif isinstance(a, IPv6AddressUpdate):
                return a.address.is_private
            else:
                return False

        return filter(is_public, addresses)

