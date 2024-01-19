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
        param = urllib.parse.urlencode(params, True)
        url = "{resource_url}{resource}?{param}".format(
            resource_url=_RESOURCE_URL, resource=resource, param=param
        )
        print(url)
        return url


class OpendataTransportLocation(OpendataTransportBase):
    """A class for handling locations from Opendata Transport."""

    def __init__(self, session, query=None, x=None, y=None, type_="all", fields=None):
        """Initialize the location."""
        super().__init__(session)

        self.query = query
        self.x = x
        self.y = y
        self.type = type_
        self.fields = (
            fields if fields is not None and isinstance(fields, list) else None
        )

        self.from_name = self.from_id = self.to_name = self.to_id = None

        self.locations = []

    @staticmethod
    def get_station(station):
        """Get the station details."""
        return {
            "name": station["name"],
            "score": station["score"],
            "coordinate_type": station["coordinate"]["type"],
            "x": station["coordinate"]["x"],
            "y": station["coordinate"]["y"],
            "distance": station["distance"],
        }

    async def async_get_data(self):
        """Retrieve the data for the location."""
        params = {}
        if self.query is not None:
            params["query"] = self.query
        else:
            params["x"] = self.x
            params["y"] = self.y

        if self.fields:
            params["fields"] = self.fields

        url = self.get_url("locations", params)

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
            for station in data["stations"]:
                self.locations.append(self.get_station(station))
        except (KeyError, TypeError, IndexError):
            raise exceptions.OpendataTransportError()


class OpendataTransportStationboard(OpendataTransportBase):
    """A class for handling stationsboards from Opendata Transport."""

    def __init__(
        self,
        station,
        session,
        limit=5,
        transportations=None,
        datetime=None,
        type_="departure",
        fields=None,
    ):
        """Initialize the journey."""
        super().__init__(session)

        self.station = station
        self.limit = limit
        self.datetime = datetime
        self.transportations = (
            transportations
            if transportations is not None and isinstance(transportations, list)
            else None
        )
        self.type = type_
        self.fields = (
            fields if fields is not None and isinstance(fields, list) else None
        )

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
        params = {
            "limit": self.limit,
            "type": self.type,
        }
        if str.isdigit(station):
            params["id"] = station
        else:
            params["station"] = station
        if self.datetime:
            params["datetime"] = self.date
        if self.transportations:
            params["transportations"] = self.transportations
        if self.fields:
            params["fields"] = self.fields

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
        except (KeyError, TypeError, IndexError):
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

    def __init__(
        self,
        start,
        destination,
        session,
        limit=3,
        page=0,
        date=None,
        time=None,
        isArrivalTime=False,
        transportations=None,
        direct=False,
        sleeper=False,
        couchette=False,
        bike=False,
        accessibility=None,
        via=None,
        fields=None,
    ):
        """Initialize the connection."""
        super().__init__(session)

        self.limit = limit
        self.page = page
        self.start = start
        self.destination = destination
        self.via = via[:5] if via is not None and isinstance(via, list) else None
        self.date = date
        self.time = time
        self.isArrivalTime = 1 if isArrivalTime else 0
        self.transportations = (
            transportations
            if transportations is not None and isinstance(transportations, list)
            else None
        )
        self.direct = 1 if direct else 0
        self.sleeper = 1 if sleeper else 0
        self.couchette = 1 if couchette else 0
        self.bike = 1 if bike else 0
        self.accessibility = accessibility
        self.fields = (
            fields if fields is not None and isinstance(fields, list) else None
        )

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
                journey = section["journey"]
                connection_info["number"] = journey["name"]
                connection_info["line"] = ''.join(filter(None, [journey["category"], journey["number"]]))
                break

        connection_info["platform"] = connection["from"]["platform"]

        return connection_info

    async def async_get_data(self):
        """Retrieve the data for the connection."""
        params = {
            "from": self.start,
            "to": self.destination,
            "limit": self.limit,
            "page": self.page,
            "isArrivalTime": self.isArrivalTime,
            "direct": self.direct,
            "sleeper": self.sleeper,
            "couchette": self.couchette,
            "bike": self.bike,
        }
        if self.via:
            params["via"] = self.via
        if self.time:
            params["time"] = self.time
        if self.date:
            params["date"] = self.date
        if self.transportations:
            params["transportations"] = self.transportations
        if self.accessibility:
            params["accessibility"] = self.accessibility
        if self.fields:
            params["fields"] = self.fields

        url = self.get_url("connections", params)

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
        except (KeyError, TypeError, IndexError):
            raise exceptions.OpendataTransportError()
