"""
Copyright (c) 2015-2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import requests

from . import exceptions

_RESOURCE = 'http://transport.opendata.ch/v1/'


class OpendataTransport(object):
    """A class for handling connections from Opendata Transport."""

    def __init__(self, start, destination):
        """Initialize the connection."""
        self.start = start
        self.destination = destination
        self.from_name = self.from_id = self.to_name = self.to_id = None
        self.connections = dict()

    def get_data(self):
        url = '{resource}connections?from={start}&to={dest}'.format(
            resource=_RESOURCE, start=self.start, dest=self.destination)
        response = requests.get(url, timeout=5)

        if response.status_code != requests.codes.ok:
            raise exceptions.OpendataTransportConnectionError()

        data = response.json()

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
        except IndexError:
            raise exceptions.OpendataTransportError()
