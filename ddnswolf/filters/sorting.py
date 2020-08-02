from ddnswolf.filters.base import AddressFilter
from ddnswolf.models.address_update import AddressUpdate, IPv4AddressUpdate, IPv6AddressUpdate


class BinaryValueSortAddressFilter(AddressFilter):
    """
    Sorts addresses by their binary representation. Addresses with smaller binary values go first.
    Supports only IPv4 and IPv6.
    """

    config_type_name = "sorted"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Sort the list of addresses by their binary representation. Addresses with smaller binary values go first.
        IPv4 addresses are placed before IPv6 addresses. Addresses of unknown type are placed at the end, and compared
        with their AddressUpdate comparator.

        An empty input results in an empty output.
        """

        def sort_key(a: AddressUpdate):
            # IPv4Address and IPv6 address are already comparable by their binary representation. The first value in
            # returned tuple will sort v4 address before v6 addresses, and only compare addresses of the same version.
            if isinstance(a, IPv4AddressUpdate):
                return 0, a.address
            elif isinstance(a, IPv6AddressUpdate):
                return 1, a.address
            else:
                return 2, a

        return sorted(addresses, key=sort_key)
