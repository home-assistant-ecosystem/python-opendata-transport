"""Example to get the details for a connection or a station."""
import asyncio

import aiohttp

from opendata_transport import OpendataTransport
from opendata_transport import OpendataTransportStationboard
from opendata_transport import OpendataTransportLocation


async def main():
    """Example for getting the data."""
    async with aiohttp.ClientSession() as session:
        # Search a station by query
        locations = OpendataTransportLocation(session, query="Stettb")
        await locations.async_get_data()

        # Print the locations data
        print(locations.locations)

        # Print as list
        print(list(map(lambda x: x["name"], locations.locations)))

        # Search a station by coordinates
        locations = OpendataTransportLocation(session, x=47.2, y=8.7)
        await locations.async_get_data()

        # Print the locations data
        print(locations.locations)

        # Print as list
        print(list(map(lambda x: x["name"], locations.locations)))

        print()

        # Get the connection for a defined route
        connection = OpendataTransport(
            "Zürich, Blumenfeldstrasse", "Zürich Oerlikon, Bahnhof", session, 4
        )
        await connection.async_get_data()

        # Print the start and the destination name
        print("Train connections:", connection.from_name, "->", connection.to_name)

        # Print the next three connections
        print(connection.connections)

        # Print the details of the next connection
        print(connection.connections[0])

        print()

        # Get all connections of a station
        stationboard = OpendataTransportStationboard("8591355", session, 4)
        await stationboard.async_get_data()

        # Print the journey data
        print(stationboard.journeys)


if __name__ == "__main__":
    asyncio.run(main())
