"""Wrapper to get connection details from Opendata Transport."""
import asyncio
import logging

import aiohttp
import urllib.parse

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE_URL = "http://transport.opendata.ch/v1/"


class OpendataTransportBase(object):
    """Representation of the Opendata Transport base class"""

    def __init__(self, session):
        self._session = session

    @staticmethod
    def get_url(resource, params):
        """Generate the URL for the request."""
        param = urllib.parse.urlencode(params)
        url = "{resource_url}{resource}?{param}".format(
            resource_url=_RESOURCE_URL, resource=resource, param=param
        )
        return url


class OpendataTransportStationboard(OpendataTransportBase):
    """A class for handling stationsboards from Opendata Transport."""

    def __init__(self, station, session, limit=5):
        """Initialize the journey."""
        super().__init__(session)
        self.station = station
        self.limit = limit
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.journeys = []

    @staticmethod
    def get_journey(journey):
        """Get the journey details."""
        return {
            "departure": journey["stop"]["departure"],
            "delay": journey["stop"]["delay"],
            "platform": journey["stop"]["platform"],
            "name": journey["name"],
            "category": journey["category"],
            "number": journey["number"],
            "to": journey["to"],
        }

    async def __async_get_data(self, station):
        """Retrieve the data for the station."""
        params = {"limit": self.limit}
        if str.isdigit(station):
            params["id"] = station
        else:
            params["station"] = station

        url = self.get_url("stationboard", params)

        try:
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
                self.journeys.append(self.get_journey(journey))
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()

    async def async_get_data(self):
        """Retrieve the data for the given station."""
        self.journeys = []
        if isinstance(self.station, list):
            for station in self.station:
                await self.__async_get_data(station)
            list.sort(self.journeys, key=lambda journey: journey["departure"])
        else:
            await self.__async_get_data(self.station)


class OpendataTransport(OpendataTransportBase):
    """A class for handling connections from Opendata Transport."""

    def __init__(self, start, destination, session, limit=3):
        """Initialize the connection."""
        super().__init__(session)
        self.limit = limit
        self.start = start
        self.destination = destination
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.connections = dict()

    @staticmethod
    def get_connection(connection):
        """Get the connection details."""
        connection_info = dict()
        connection_info["departure"] = connection["from"]["departure"]
        connection_info["duration"] = connection["duration"]
        connection_info["delay"] = connection["from"]["delay"]
        connection_info["transfers"] = connection["transfers"]

        # Sections journey can be null if there is a walking section at first
        connection_info["number"] = ""
        for section in connection["sections"]:
            if section["journey"] is not None:
                connection_info["number"] = section["journey"]["name"]
                break

        connection_info["platform"] = connection["from"]["platform"]

        return connection_info

    async def async_get_data(self):
        """Retrieve the data for the connection."""
        url = self.get_url(
            "connections",
            {"from": self.start, "to": self.destination, "limit": self.limit},
        )

        try:
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
            for connection in data["connections"]:
                self.connections[index] = self.get_connection(connection)
                index = index + 1
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()
