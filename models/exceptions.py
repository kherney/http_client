# -*- coding: utf-8 -*-
"""
Custom exceptions for HTTP client module.
"""
from odoo.exceptions import UserError


class HTTPClientError(UserError):
    """Base exception for all HTTP client errors."""

    def __init__(self, message):
        super(HTTPClientError, self).__init__(message)


class ConnectionInitError(HTTPClientError):
    """Base exception for connection initialization errors."""

    def __init__(self, message, original_error=None):
        self.original_error = original_error
        if original_error:
            message = f"{message} - Original error: {str(original_error)}"
        super(ConnectionInitError, self).__init__(message)


class PoolManagerInitError(ConnectionInitError):
    """Exception raised when initializing a PoolManager fails."""

    def __init__(self, message, original_error=None):
        super(PoolManagerInitError, self).__init__(
            f"Failed to initialize Pool Manager: {message}", original_error)


class HTTPConnectionPoolInitError(ConnectionInitError):
    """Exception raised when initializing an HTTP connection pool fails."""

    def __init__(self, message, original_error=None):
        super(HTTPConnectionPoolInitError, self).__init__(
            f"Failed to initialize HTTP Connection Pool: {message}", original_error)


class HTTPSConnectionPoolInitError(ConnectionInitError):
    """Exception raised when initializing an HTTPS connection pool fails."""

    def __init__(self, message, original_error=None):
        super(HTTPSConnectionPoolInitError, self).__init__(
            f"Failed to initialize HTTPS Connection Pool: {message}", original_error)


class RequestError(HTTPClientError):
    """Exception raised when a request fails."""

    def __init__(self, message, original_error=None):
        self.original_error = original_error
        if original_error:
            message = f"{message} - Original error: {str(original_error)}"
        super(RequestError, self).__init__(message)


class URLOpenError(HTTPClientError):
    """Exception raised when urlopen fails."""

    def __init__(self, message, original_error=None):
        self.original_error = original_error
        if original_error:
            message = f"{message} - Original error: {str(original_error)}"
        super(URLOpenError, self).__init__(message)
