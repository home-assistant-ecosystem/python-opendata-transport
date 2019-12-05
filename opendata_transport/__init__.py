"""Wrapper to get connection details from Opendata Transport."""
import asyncio
import logging

import aiohttp
import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "http://transport.opendata.ch/v1/"


class OpendataTransport(object):
    """A class for handling connections from Opendata Transport."""

    def __init__(self, start, destination, loop, session):
        """Initialize the connection."""
        self._loop = loop
        self._session = session
        self.start = start
        self.destination = destination
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.connections = dict()

    async def async_get_data(self):
        """Retrieve the data for the connection."""
        url = "{resource}connections?from={start}&to={dest}".format(
            resource=_RESOURCE, start=self.start, dest=self.destination
        )
        print("Z\u00fcrich, Blumenfeldstrasse")
        print("Zürich, Blumenfeldstrasse")
        print(url)
        print(self.start)
        print(self.destination)
        print(u"{}".format(self.start))
        print(u"\u212B".encode("utf-8"))
        print(u"\u00fc")
        print("ü")
        print("-----------------")
        print(replace_german_umlaute(self.start))
        test1 = replace_german_umlaute(self.start)
        print(u"\u212B".encode("utf-8"))
        print(u"{}".format(test1))
        try:
            with async_timeout.timeout(5, loop=self._loop):
                response = await self._session.get(url, raise_for_status=True)

            _LOGGER.debug("Response from transport.opendata.ch: %s", response.status)
            data = await response.json()
            _LOGGER.debug(data)
        except asyncio.TimeoutError:
            _LOGGER.error("Can not load data from transport.opendata.ch")
            raise exceptions.OpendataTransportConnectionError()
        except aiohttp.ClientError as aiohttpClientError:
            _LOGGER.error("Response from transport.opendata.ch: %s", aiohttpClientError)
            raise exceptions.OpendataTransportConnectionError()

        try:
            self.from_id = data["from"]["id"]
            self.from_name = data["from"]["name"]
            self.to_id = data["to"]["id"]
            self.to_name = data["to"]["name"]
            index = 0
            for conn in data["connections"][1:4]:
                self.connections[index] = dict()
                self.connections[index]["departure"] = conn["from"]["departure"]
                self.connections[index]["duration"] = conn["duration"]
                self.connections[index]["delay"] = conn["from"]["delay"]
                self.connections[index]["transfers"] = conn["transfers"]
                self.connections[index]["number"] = conn["sections"][0]["journey"][
                    "name"
                ]
                self.connections[index]["platform"] = conn["from"]["platform"]
                index = index + 1
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()


# umlaute_dict = {
#     '\xc3\xa4': 'ae',  # U+00E4	   \xc3\xa4
#     '\xc3\xb6': 'oe',  # U+00F6	   \xc3\xb6
#     '\xc3\xbc': 'ue',  # U+00FC	   \xc3\xbc
#     '\xc3\x84': 'Ae',  # U+00C4	   \xc3\x84
#     '\xc3\x96': 'Oe',  # U+00D6	   \xc3\x96
#     '\xc3\x9c': 'Ue',  # U+00DC	   \xc3\x9c
#     '\xc3\x9f': 'ss',  # U+00DF	   \xc3\x9f
# }

umlaute_dict = {
    "\xc3\xbc": "\u00fc",
}


def replace_german_umlaute(unicode_string):
    """."""
    utf8_string = unicode_string.encode("utf-8")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("{}".format(utf8_string))
    print(u"{}".format(utf8_string))
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    for k in umlaute_dict.keys():
        utf8_string = utf8_string.replace(k, umlaute_dict[k])

    return utf8_string.decode()
