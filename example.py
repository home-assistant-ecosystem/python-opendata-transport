"""Example to get the details for a connection."""
import asyncio
import aiohttp

from opendata_transport import OpendataTransport
from opendata_transport import OpendataTransportStationboard


async def main():
    async with aiohttp.ClientSession() as session:
        data = OpendataTransport(
            "Zürich, Blumenfeldstrasse", "Zürich Oerlikon, Bahnhof", loop,
            session, 4
        )
        await data.async_get_data()

        # Print the start and the destination name
        print("Train connections:", data.from_name, "->", data.to_name)

        # Print the next three connections
        print(data.connections)

        # Print the details of the next connection
        print(data.connections[0])

        data = OpendataTransportStationboard(
            "Zürich Oerlikon, Bahnhof", loop, session, 4
        )
        await data.async_get_data()

        print(data.journeys)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
