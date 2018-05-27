"""
Copyright (c) 2015-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio
import logging

import aiohttp
import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'http://transport.opendata.ch/v1/'


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
        url = '{resource}connections?from={start}&to={dest}'.format(
            resource=_RESOURCE, start=self.start, dest=self.destination)

        try:
            with async_timeout.timeout(5, loop=self._loop):
                response = await self._session.get(url)

            _LOGGER.debug(
                "Response from transport.opendata.ch: %s", response.status)
            data = await response.json()
            _LOGGER.debug(data)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Can not load data from transport.opendata.ch")
            raise exceptions.OpendataTransportConnectionError()

        try:
            self.from_id = data['from']['id']
            self.from_name = data['from']['name']
            self.to_id = data['to']['id']
            self.to_name = data['to']['name']
            index = 0
            for conn in data['connections'][1:4]:
                self.connections[index] = dict()
                self.connections[index]['departure'] = \
                    conn['from']['departure']
                self.connections[index]['duration'] = conn['duration']
                self.connections[index]['transfers'] = conn['transfers']
                self.connections[index]['number'] = \
                    conn['sections'][0]['journey']['name']
                self.connections[index]['platform'] = conn['from']['platform']
                index = index + 1
        except (TypeError, IndexError):
            raise exceptions.OpendataTransportError()
