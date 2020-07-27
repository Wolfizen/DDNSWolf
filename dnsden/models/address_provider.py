from abc import ABC

from dnsden.models.address_update import AddressUpdate


class AddressProvider(ABC):
    """
    Provides one or more addresses that providers can pull from. When the address of a provider changes,
    any objects subscribing to the provider will be notified.

    Address providers may return any list of addresses they see fit. Address filters can be used by the consumer to
    select only certain addresses from the provided list.

    Examples of address providers include: an interface on the host, a public IP checker, an address filter subscribing
    to another provider.
    """

    def provide_addresses(self) -> [AddressUpdate]:
        """
        Get the current addresses represented by this provider. This call may involve a network request, system call, or
        other blocking operation. Caching should not be involved unless absolutely necessary, for example with a
        rate-limited API.

        :return The list of addresses represented by this provider.
        """
        raise NotImplementedError("FIXME: Unimplemented provide_addresses() in {}".format(type(self).__name__))
