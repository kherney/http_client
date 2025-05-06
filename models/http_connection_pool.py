# -*- coding: utf-8 -*-
from typing import Dict

from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
import logging

from .exceptions import (
    HTTPConnectionPoolInitError, HTTPSConnectionPoolInitError,
)

from .http_abstract import HTTPAbstract

_logger = logging.getLogger(__name__)


class HTTPPoolAbstract(HTTPAbstract):
    """Abstract model for HTTP connection pools."""
    _name = 'http.pool.abstract'
    _description = 'HTTP Connection Pool Abstract Model'

    def _init_connection(self):
        """Initialize an HTTP connection pool using the options from _get_options().

        Returns:
            HTTPConnectionPool: The initialized HTTP connection pool

        Raises:
            HTTPConnectionPoolInitError: If an error occurs during initialization
        """
        options = self._get_options()

        # Ensure required host parameter is present
        if 'host' not in options:
            raise ValueError("'host' is required for HTTP connection pool")

        with self._handle_connection_exceptions(HTTPConnectionPoolInitError):
            return HTTPConnectionPool(**options)


class HTTPSPoolAbstract(HTTPAbstract):
    """Abstract model for HTTPS connection pools."""
    _name = 'https.pool.abstract'
    _description = 'HTTPS Connection Pool Abstract Model'

    def _init_connection(self):
        """Initialize an HTTPS connection pool using the options from _get_options().

        Returns:
            HTTPSConnectionPool: The initialized HTTPS connection pool

        Raises:
            HTTPSConnectionPoolInitError: If an error occurs during initialization
        """
        options = self._get_options()

        # Ensure required host parameter is present
        if 'host' not in options:
            raise ValueError("'host' is required for HTTPS connection pool")

        with self._handle_connection_exceptions(HTTPSConnectionPoolInitError):
            return HTTPSConnectionPool(**options)
