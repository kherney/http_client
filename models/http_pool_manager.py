# -*- coding: utf-8 -*-

from urllib3.poolmanager import PoolManager
from typing import Dict

import urllib3
import logging

from .http_abstract import HTTPAbstract
from .exceptions import (
    HTTPClientError, PoolManagerInitError,
)

_logger = logging.getLogger(__name__)


class PoolManagerAbstract(HTTPAbstract):
    """Abstract model for pool managers.

    This model provides functionality for managing multiple connection pools.
    """
    _name = 'http.pool.manager.abstract'
    _description = 'HTTP Pool Manager Abstract Model'

    def _init_connection(self):
        """Initialize a pool manager using the options from _get_options().

        Returns:
            PoolManager: The initialized pool manager

        Raises:
            PoolManagerInitError: If an error occurs during initialization
        """
        options = self._get_options()

        # Set default num_pools if not specified
        if 'num_pools' not in options:
            options['num_pools'] = 10

        with self._handle_connection_exceptions(PoolManagerInitError):
            return PoolManager(**options)

    def connection_from_host(self, host, port=None, scheme='http', pool_kwargs=None):
        """Get a connection from the pool for the specified host.

        Args:
            host (str): Host to connect to
            port (int, optional): Port to connect to
            scheme (str, optional): URL scheme (http or https)
            pool_kwargs (dict, optional): Additional arguments to pass to the connection pool constructor

        Returns:
            urllib3.connectionpool.HTTPConnectionPool: The connection pool

        Raises:
            HTTPClientError: If an error occurs during the operation
        """
        conn = self._get_connection()
        try:
            with self._handle_connection_exceptions(HTTPClientError):
                return conn.connection_from_host(
                    host=host,
                    port=port,
                    scheme=scheme,
                    pool_kwargs=pool_kwargs
                )
        except Exception as e:
            _logger.error("Error getting connection from host %s:%s: %s", host, port, str(e))
            raise HTTPClientError(f"Error getting connection from host {host}:{port}: {str(e)}")

    def connection_from_url(self, url, pool_kwargs=None):
        """Get a connection from the pool for the specified URL.

        Args:
            url (str): URL to connect to
            pool_kwargs (dict, optional): Additional arguments to pass to the connection pool constructor

        Returns:
            urllib3.connectionpool.HTTPConnectionPool: The connection pool

        Raises:
            HTTPClientError: If an error occurs during the operation
        """
        conn = self._get_connection()
        try:
            with self._handle_connection_exceptions(HTTPClientError):
                return conn.connection_from_url(
                    url=url,
                    pool_kwargs=pool_kwargs
                )
        except Exception as e:
            _logger.error("Error getting connection from URL %s: %s", url, str(e))
            raise HTTPClientError(f"Error getting connection from URL {url}: {str(e)}")

    def clear(self):
        """Clear the connection pools.

        Raises:
            HTTPClientError: If an error occurs during the operation
        """
        conn = self._get_connection()
        try:
            with self._handle_connection_exceptions(HTTPClientError):
                conn.clear()
        except Exception as e:
            _logger.error("Error clearing connection pools: %s", str(e))
            raise HTTPClientError(f"Error clearing connection pools: {str(e)}")
