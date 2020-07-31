from abc import ABC

from dnsden.models.address_update import AddressUpdate


class AddressFilter(ABC):
    """
    Filters a list of AddressUpdates based on a consistent behavior particular to the filter class. The original source
    for a filters' addresses is an AddressSource. Multiple filters may be chained together, narrowing the list of
    addresses each time. These filters are intended to enable the selection of particular addresses from a source, when
    that source returns multiple addresses of the same family.

    Filters may require additional arguments besides the input list. These arguments will be given to their
    constructor, and filters should save these arguments on the instance to be used in the filter function.

    Filter arguments will be given as strings. Filters should raise an error if the arguments are incorrectly
    formatted. For example, if a number is required and a non-number is given, that is an error condition. Other
    problems with the input should generally fail silently, returning empty and possibly logging a warning.

    Generally, a new instance of the filter object is created each time it needs to be used. Users of a filter object
    should not absolutely assume that a filter will not store state. This state may be benign, like a persistent
    socket connection or other resource. Caveat emptor.
    """

    config_type_name: str = NotImplemented
    """
    This class variable defines the name to use in the program configuration to reference this address filter. There can
    only be one name per filter, and it cannot conflict with any other filter. This is the only name a filter will have,
    instances of the filter are anonymous.
    """

    def __init__(self):
        super(AddressFilter, self).__init__()

    def filter(self, addresses: [AddressUpdate]) -> [AddressUpdate]:
        """
        Performs a filter operation on a list of addresses. Filters may alter their behavior according to the arguments
        given when they were initialized. Each filter class should perform the same filter operation each time,
        i.e. be idempotent.

        :abstract
        :param addresses: The input addresses.
        :return: The addresses after filtering.
        """
        raise NotImplementedError("FIXME: Unimplemented filter() in {}".format(type(self).__name__))
