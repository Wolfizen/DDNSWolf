import ipaddress
import json
from datetime import datetime, timedelta
from typing import Union, Optional

import dns.name
from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from dns.rdatatype import RdataType, UnknownRdatatype

from ddnswolf import util
from ddnswolf.models.address_update import IPv4AddressUpdate, IPv6AddressUpdate
from ddnswolf.protocols.base import DynamicDNSUpdater


class CloudflareDNSUpdater(DynamicDNSUpdater):
    """
    Updater for domains managed by Cloudflare. This updater uses the python Cloudflare
    library to perform the API calls.

    Authentication is done with API access tokens. This updater DOES NOT SUPPORT global
    API keys. Stop using them.

    Required permissions:
        Zone->DNS->Edit
        Include the specific zone where the hostname lives.
    """

    config_type_name = "cloudflare"

    def __init__(self, *args, **kwargs):
        super(CloudflareDNSUpdater, self).__init__(*args, **kwargs)
        self.cf = CloudFlare(token=self.config["token"])
        self._cf_zone = None
        self._cf_zone_last_update = datetime.min

    def update(self, address_update):
        cf_zone = self._get_zone()
        cf_record = self._get_record_for(address_update)
        if cf_record is not None:
            # Record exists. Overwrite its content with the new address.
            self.cf.zones.dns_records.patch(
                cf_zone["id"],
                cf_record["id"],
                data=json.dumps({"content": str(address_update.address)}),
            )
            # Update success! (API throws on error)
        elif self.config["create_records"]:
            # Record does not exist. Create it with sensible defaults. TTL of 1
            # indicates automatic choice by CF.
            self.cf.zones.dns_records.post(
                cf_zone["id"],
                data=json.dumps(
                    {
                        "type": RdataType.to_text(address_update.rdtype),
                        "name": self.config["hostname"],
                        "content": str(address_update.address),
                        "ttl": 1,
                    }
                ),
            )
            # Update success! (API throws on error)
        else:
            raise Exception(
                f"DNS record missing for {address_update.address}, and configuration "
                f"does not allow creating the record."
            )

    def needs_update(
        self, address_update: Union[IPv4AddressUpdate, IPv6AddressUpdate]
    ) -> bool:
        cf_record = self._get_record_for(address_update)
        if cf_record is not None:
            return ipaddress.ip_address(cf_record["content"]) != address_update.address
        # If no resource record is present, the address needs updating. The RR will be
        # created in update().
        return True

    def _get_record_for(
        self, address_update: Union[IPv4AddressUpdate, IPv6AddressUpdate]
    ) -> Optional[dict]:
        """
        Get the record details for the configured name. May return None if no record
        exists.
        """
        cf_zone = self._get_zone()
        for record in self.cf.zones.dns_records.get(
            cf_zone["id"], params={"name": self.config["hostname"]}
        ):
            try:
                if (
                    util.dns_names_equal(record["name"], self.config["hostname"])
                    and RdataType.from_text(record["type"]) == address_update.rdtype
                ):
                    return record
            except UnknownRdatatype:
                pass
        return None

    def _get_zone(self):
        """Get the zone details for the configured name. May return a cached copy."""
        if (
            self._cf_zone_last_update + timedelta(hours=4) > datetime.now()
            and self._cf_zone is not None
        ):
            return self._cf_zone

        # Cloudflare's API requires a large-scope permission to be able to list *all*
        # zones. This permission is not required if specifying the zone by name.
        # Therefore, to avoid asking for that permission, an iterative search is
        # performed to find the correct zone name.
        zone_name = dns.name.from_text(self.config["hostname"])
        while True:
            try:
                # Attempt to get the zone details.
                for zone in self.cf.zones.get(params={"name": str(zone_name)}):
                    if util.dns_names_equal(zone["name"], zone_name):
                        # Found it!
                        self._set_zone(zone)
                        return self._cf_zone
            except CloudFlareAPIError:
                # The zone name we tried is not valid. Move to parent name.
                pass
            try:
                zone_name = zone_name.parent()
            except dns.name.NoParent:
                # No more names to check. Probably invalid configuration.
                raise Exception(
                    f"Could not find the zone for {self.config['hostname']}. Either it "
                    f"is the wrong name or the access token does not have sufficient "
                    f"permissions to read the zone."
                )

    def _set_zone(self, zone):
        """Update the cache of the Cloudflare zone."""
        self._cf_zone = zone
        if zone is not None:
            self._cf_zone_last_update = datetime.now()
        else:
            self._cf_zone_last_update = datetime.min
