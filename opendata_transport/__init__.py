"""Wrapper to get connection details from Opendata Transport."""
import asyncio
import logging

import aiohttp
import async_timeout
import urllib.parse

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

    def __get_connection_dict(self, conn):
        conninfo = dict()
        conninfo["departure"] = conn["from"]["departure"]
        conninfo["duration"] = conn["duration"]
        conninfo["delay"] = conn["from"]["delay"]
        conninfo["transfers"] = conn["transfers"]
        conninfo["number"] = conn["sections"][0]["journey"]["name"]
        conninfo["platform"] = conn["from"]["platform"]

        return conninfo

    async def async_get_data(self):
        """Retrieve the data for the connection."""
        param = urllib.parse.urlencode({ 'from': self.start, 'to': self.destination })
        url = "{resource}connections?{param}".format(resource=_RESOURCE, param=param)

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
            for conn in data["connections"][:3]:
                self.connections[index] = self.__get_connection_dict(conn)
                index = index + 1
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()

