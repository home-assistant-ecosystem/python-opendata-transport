"""Wrapper to get connection details from Opendata Transport."""
import asyncio
import logging

import aiohttp
import async_timeout
import urllib.parse

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE_URL = "http://transport.opendata.ch/v1/"


class OpendataTransportBase(object):
    """Representation of the Opendata Transport base class"""

    def __init__(self, loop, session):
        self._loop = loop
        self._session = session

    def get_url(self, resource, params):
        """Generate the URL for the request."""
        param = urllib.parse.urlencode(params)
        url = "{resource_url}{resource}?{param}".format(
            resource_url=_RESOURCE_URL, resource=resource, param=param
        )
        return url


class OpendataTransportStationboard(OpendataTransportBase):
    """A class for handling stationsboards from Opendata Transport."""

    def __init__(self, station, loop, session, limit=5):
        """Initialize the journey."""
        super().__init__(loop, session)
        self.station = station
        self.limit = limit
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.journeys = []

    def __get_journey_dict(self, journey):
        """Get the journey details."""
        journeyinfo = dict()
        journeyinfo["departure"] = journey["stop"]["departure"]
        journeyinfo["delay"] = journey["stop"]["delay"]
        journeyinfo["platform"] = journey["stop"]["platform"]
        journeyinfo["name"] = journey["name"]
        journeyinfo["category"] = journey["category"]
        journeyinfo["number"] = journey["number"]
        journeyinfo["to"] = journey["to"]

        return journeyinfo

    async def __async_get_data(self, station):
        """Retrieve the data for the station."""
        params = {"limit": self.limit}
        if str.isdigit(station):
            params["id"] = station
        else:
            params["station"] = station

        url = self.get_url("stationboard", params)

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
            for journey in data["stationboard"]:
                self.journeys.append(self.__get_journey_dict(journey))
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()

    async def async_get_data(self):
        """Retrieve the data for the given station."""
        if isinstance(self.station, list):
            for station in self.station:
                await self.__async_get_data(station)
            list.sort(self.journeys, key=lambda journey: journey["departure"])
        else:
            await self.__async_get_data(self.station)


class OpendataTransport(OpendataTransportBase):
    """A class for handling connections from Opendata Transport."""

    def __init__(self, start, destination, loop, session, limit=3):
        """Initialize the connection."""
        super().__init__(loop, session)
        self.limit = limit
        self.start = start
        self.destination = destination
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.connections = dict()

    def __get_connection_dict(self, conn):
        """Get the connection details."""
        conninfo = dict()
        conninfo["departure"] = conn["from"]["departure"]
        conninfo["duration"] = conn["duration"]
        conninfo["delay"] = conn["from"]["delay"]
        conninfo["transfers"] = conn["transfers"]

        # Sections journey can be null if there is a walking section at first
        conninfo["number"] = ""
        for section in conn["sections"]:
            if section["journey"] is not None:
                conninfo["number"] = section["journey"]["name"]
                break

        conninfo["platform"] = conn["from"]["platform"]

        return conninfo

    async def async_get_data(self):
        """Retrieve the data for the connection."""
        url = self.get_url(
            "connections",
            {"from": self.start, "to": self.destination, "limit": self.limit},
        )

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
            for conn in data["connections"]:
                self.connections[index] = self.__get_connection_dict(conn)
                index = index + 1
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()
