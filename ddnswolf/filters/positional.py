from typing import Union

from ddnswolf.filters.base import AddressFilter
from ddnswolf.models.address_update import AddressUpdate


class NthAddressFilter(AddressFilter):
    """Selects the Nth address in the list."""

    config_type_name = "nth"

    def __init__(self, index: Union[str, int]):
        """
        :param index: The index in the input list to select. Indices starting from the end can be specified with
        negative numbers.
        """
        super(NthAddressFilter, self).__init__()
        self.index = int(index)

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Selects the address located at index. If there is no address at that index, an empty list is returned.
        """
        try:
            # Negative indices are handled nicely by the Python standard library.
            return addresses[self.index]
        except IndexError:
            return []


class FirstAddressFilter(AddressFilter):
    """Selects the first address in the list."""

    config_type_name = "first"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Selects the first address in the list. If there are no addresses in the list, an empty list is returned.
        """
        return addresses[0:1]


class LastAddressFilter(AddressFilter):
    """Selects the last address in the list."""

    config_type_name = "last"

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Selects the last address in the list. If there are no addresses in the list, an empty list is returned.
        """
        return addresses[-1:]


