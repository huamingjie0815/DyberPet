# coding:utf-8


class OpenClawException(Exception):
    """Base exception for OpenClaw client"""
    pass


class ConnectionError(OpenClawException):
    """WebSocket connection error"""
    pass


class HandshakeError(OpenClawException):
    """Handshake with gateway failed"""
    pass


class ProtocolError(OpenClawException):
    """Protocol message parsing error"""
    pass


class AuthenticationError(OpenClawException):
    """Authentication failed"""
    pass
