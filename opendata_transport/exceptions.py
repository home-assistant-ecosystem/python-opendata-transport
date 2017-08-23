"""
Copyright (c) 2015-2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""


class OpendataTransportError(Exception):
    """General MyStromError exception occurred."""

    pass


class OpendataTransportConnectionError(OpendataTransportError):
    """When a connection error is encountered."""

    pass
