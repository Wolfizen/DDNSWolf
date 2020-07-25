from dns import resolver
from dns.rdataclass import RdataClass
from dns.rdatatype import RdataType

from dnsden.models.address_update import IPv4AddressUpdate, IPv6AddressUpdate


class DynamicDNSUpdater:
    """
    The base class for all updaters provided by DNSDen. An updater represents a specific configuration of a dynamic DNS
    service, with its own authentication token and target hostname. An updater is generally responsible for updating a
    single name within a single service/protocol.
    """

    def __init__(self, config):
        self.config = config

    def update(self, address_update):
        """
        Ask the service to change the address of the configured name to be the address in the update. This method should
        not check if the address needs changing, that is done in needs_update().

        :abstract
        :return: None
        """

        print("FIXME: Unimplemented update() in {}".format(self.__name__))

    def needs_update(self, address_update) -> bool:
        """
        Checks if the name configured in this updater has a different address than the provided address and thus
        needs to be updated.

        Defaults to a simple DNS resolution, supporting IPv4 and IPv6 addresses. For other classes, or other record
        types, override this method.

        It is generally recommended to override this method with an API call to whatever service the updater represents.
        The DNS will not provide as timely an answer as directly asking the authoritative source.
        """

        if isinstance(address_update, IPv4AddressUpdate):
            question_rdtype = RdataType.A
        elif isinstance(address_update, IPv6AddressUpdate):
            question_rdtype = RdataType.AAAA
        else:
            # Unsupported address update.
            print("Unsupported address update for {}: {}".format(self.__name__, address_update))
            return False

        # Use the system default resolver
        answers = resolver.resolve(self.config["name"], question_rdtype, RdataClass.IN)
        for answer in answers:
            if answer.rdtype == question_rdtype:
                # TODO Figure out the field name for the address
                print(answer)
                return True
