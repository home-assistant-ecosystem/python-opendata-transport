"""Tests for python-opendata-transport."""

import pytest

from opendata_transport import (
    OpendataTransportLocation,
    OpendataTransportStationboard,
    OpendataTransport,
)
from opendata_transport import exceptions


class DummyResponse:
    """A dummy response to simulate aiohttp.ClientResponse."""

    def __init__(self, status, json_data):
        """Initialize with a status code and JSON data."""
        self.status = status
        self._json_data = json_data

    async def json(self):
        """Simulate the json() method of aiohttp.ClientResponse."""
        return self._json_data


class DummySession:
    """A dummy session to simulate aiohttp.ClientSession."""

    def __init__(self, response):
        """Initialize with a predefined response."""
        self._response = response

    async def get(self, url, raise_for_status=True):
        """Simulate an HTTP GET request."""
        return self._response


@pytest.mark.asyncio
async def test_location_success():
    """Test successful retrieval of location data."""
    dummy_json = {
        "stations": [
            {
                "name": "Bern",
                "score": 10,
                "coordinate": {"type": "WGS84", "x": 7.439, "y": 46.948},
                "distance": 0,
            }
        ]
    }
    session = DummySession(DummyResponse(200, dummy_json))
    location = OpendataTransportLocation(session, query="Bern")
    await location.async_get_data()
    assert location.locations[0]["name"] == "Bern"


@pytest.mark.asyncio
async def test_location_keyerror():
    """Test handling of missing keys in location data."""
    session = DummySession(DummyResponse(200, {}))
    location = OpendataTransportLocation(session, query="Bern")
    with pytest.raises(exceptions.OpendataTransportError):
        await location.async_get_data()


@pytest.mark.asyncio
async def test_stationboard_success():
    """Test successful retrieval of stationboard data."""
    dummy_json = {
        "stationboard": [
            {
                "stop": {
                    "departure": "2024-01-01T12:00:00+01:00",
                    "delay": 0,
                    "platform": "1",
                },
                "name": "IC 1",
                "category": "IC",
                "number": "1",
                "to": "Geneva",
            }
        ]
    }
    session = DummySession(DummyResponse(200, dummy_json))
    stationboard = OpendataTransportStationboard("Bern", session)
    await stationboard.async_get_data()
    assert stationboard.journeys[0]["name"] == "IC 1"


@pytest.mark.asyncio
async def test_stationboard_keyerror():
    """Test handling of missing keys in stationboard data."""
    session = DummySession(DummyResponse(200, {}))
    stationboard = OpendataTransportStationboard("Bern", session)
    with pytest.raises(exceptions.OpendataTransportError):
        await stationboard.async_get_data()


@pytest.mark.asyncio
async def test_connection_success():
    """Test successful retrieval of connection data."""
    dummy_json = {
        "from": {"id": "8507000", "name": "Bern"},
        "to": {"id": "8503000", "name": "Geneva"},
        "connections": [
            {
                "from": {
                    "departure": "2024-01-01T12:00:00+01:00",
                    "delay": 0,
                    "platform": "1",
                },
                "duration": "01:00:00",
                "transfers": 0,
                "sections": [
                    {"journey": {"name": "IC 1", "category": "IC", "number": "1"}}
                ],
            }
        ],
    }
    session = DummySession(DummyResponse(200, dummy_json))
    connection = OpendataTransport("Bern", "Geneva", session)
    await connection.async_get_data()
    assert connection.connections[0]["departure"] == "2024-01-01T12:00:00+01:00"


@pytest.mark.asyncio
async def test_connection_keyerror():
    """Test handling of missing keys in connection data."""
    session = DummySession(DummyResponse(200, {}))
    connection = OpendataTransport("Bern", "Geneva", session)
    with pytest.raises(exceptions.OpendataTransportError):
        await connection.async_get_data()
