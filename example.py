"""
Copyright (c) 2015-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio
import aiohttp

from opendata_transport import OpendataTransport


async def main():
    async with aiohttp.ClientSession() as session:
        data = OpendataTransport('Bex', 'Vevey', loop, session)
        await data.async_get_data()

        # Print the start and the destination name
        print("Train connections:", data.from_name, "->", data.to_name)

        # Print the next three connections
        print(data.connections)

        # Print the details of the next connection
        print(data.connections[0])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
