"""Exceptions for OpenData transport API client."""


class OpendataTransportError(Exception):
    """General OpenDataError exception occurred."""


class OpendataTransportConnectionError(OpendataTransportError):
    """When a connection error is encountered."""
