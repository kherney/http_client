# -*- coding: utf-8 -*-

from contextlib import contextmanager
from odoo.models import BaseModel
from odoo import api
from urllib3.util import make_headers, Timeout
from urllib3.exceptions import (
    HTTPError, TimeoutError, HostChangedError, LocationValueError,
    MaxRetryError, NewConnectionError, ProtocolError, ProxyError,
    SSLError, ReadTimeoutError, ConnectTimeoutError, ClosedPoolError,
    EmptyPoolError, FullPoolError, URLSchemeUnknown
)
from typing import Dict
import urllib.parse

import urllib3
import logging

from .exceptions import (HTTPClientError, ConnectionInitError, RequestError, URLOpenError)

_logger = logging.getLogger(__name__)


class HTTPAbstract(BaseModel):
    """Base abstract model for HTTP connections.

    This model provides common functionality for all connection types.
    """
    _name = 'http.abstract'
    _description = 'HTTP Abstract Model'

    _http_connection = {}
    _connection_cache = {}  # Class-level cache for connections

    @contextmanager
    def _handle_connection_exceptions(self, error_class=ConnectionInitError):
        """Context manager for handling connection exceptions.

        Args:
            error_class: The exception class to use for wrapping exceptions.
                         Defaults to ConnectionInitError.

        Yields:
            None

        Raises:
            ConnectionInitError: If an exception occurs during the connection operation.
        """
        try:
            yield
        except (LocationValueError, ValueError) as e:
            _logger.error("Invalid connection parameters: %s", str(e))
            raise error_class("Invalid connection parameters", e)
        except URLSchemeUnknown as e:
            _logger.error("Unknown URL scheme: %s", str(e))
            raise error_class("Unknown URL scheme", e)
        except (TimeoutError, ConnectTimeoutError) as e:
            _logger.error("Connection timeout: %s", str(e))
            raise error_class("Connection timeout", e)
        except (SSLError, ProxyError) as e:
            _logger.error("SSL or proxy error: %s", str(e))
            raise error_class("SSL or proxy error", e)
        except (ClosedPoolError, EmptyPoolError, FullPoolError) as e:
            _logger.error("Pool error: %s", str(e))
            raise error_class("Pool error", e)
        except NewConnectionError as e:
            _logger.error("Failed to establish a new connection: %s", str(e))
            raise error_class("Failed to establish a new connection", e)
        except HTTPError as e:
            _logger.error("HTTP error: %s", str(e))
            raise error_class("HTTP error", e)
        except Exception as e:
            _logger.error("Unexpected error: %s", str(e))
            raise error_class("Unexpected error", e)

    @contextmanager
    def _handle_request_exceptions(self, method, url, error_class=RequestError):
        """Context manager for handling request exceptions.

        Args:
            method: The HTTP method being used (GET, POST, etc.)
            url: The URL being requested
            error_class: The exception class to use for wrapping exceptions.
                         Defaults to RequestError.

        Yields:
            None

        Raises:
            RequestError: If an exception occurs during the request operation.
        """
        try:
            yield
        except (TimeoutError, ReadTimeoutError, ConnectTimeoutError) as e:
            _logger.error("Request timeout for %s %s: %s", method, url, str(e))
            raise error_class(f"Request timeout for {method} {url}", e)
        except (SSLError, ProxyError) as e:
            _logger.error("SSL or proxy error for %s %s: %s", method, url, str(e))
            raise error_class(f"SSL or proxy error for {method} {url}", e)
        except HostChangedError as e:
            _logger.error("Host changed error for %s %s: %s", method, url, str(e))
            raise error_class(f"Host changed error for {method} {url}", e)
        except MaxRetryError as e:
            _logger.error("Max retries exceeded for %s %s: %s", method, url, str(e))
            raise error_class(f"Max retries exceeded for {method} {url}", e)
        except NewConnectionError as e:
            _logger.error("Connection error for %s %s: %s", method, url, str(e))
            raise error_class(f"Connection error for {method} {url}", e)
        except ProtocolError as e:
            _logger.error("Protocol error for %s %s: %s", method, url, str(e))
            raise error_class(f"Protocol error for {method} {url}", e)
        except HTTPError as e:
            _logger.error("HTTP error for %s %s: %s", method, url, str(e))
            raise error_class(f"HTTP error for {method} {url}", e)
        except Exception as e:
            _logger.error("Unexpected error for %s %s: %s", method, url, str(e))
            raise error_class(f"Unexpected error for {method} {url}", e)

    @classmethod
    def _register_hook(cls):
        """Initialize connection configurations when the model is registered.

        This method is called by Odoo after the model is fully initialized and registered.
        It's the perfect place to initialize any necessary connection configurations.
        """
        _logger.info("Initializing configurations for %s", cls._name)
        # Clear any existing connections for this model
        if cls._name in cls._connection_cache:
            cls._connection_cache[cls._name] = None

    def _init_connection(self):
        """Initialize the connection.

        This method should be implemented by subclasses.

        Returns:
            The initialized connection object
        """
        raise NotImplementedError("Subclasses must implement _init_connection")

    def _get_connection(self):
        """Get the underlying connection object.

        Checks the class-level cache first, then lazily initializes the connection if needed.

        Returns:
            The connection object
        """
        # Try to get the connection from the class-level cache
        if self._name in self._connection_cache and self._connection_cache[self._name]:
            return self._connection_cache[self._name]

        # If not in cache or None, initialize it
        connection = self._init_connection()
        # Store in class-level cache for reuse
        self._connection_cache[self._name] = connection

        return connection

    def _get_options(self) -> Dict:
        """Get default connection options.

        Returns:
            dict: Default connection options
        """

        if not hasattr(self, '_http_connection'):
            raise AttributeError("'_http_connection' attribute not found")
        if not isinstance(self._http_connection, dict):
            raise ValueError("'_http_connection' must be a dictionary")

        return {
            'timeout': Timeout.DEFAULT_TIMEOUT,
            'maxsize': 1,
            'retries': None,
            'block': False,
            'headers': None,
            **self._http_connection,
        }

    @api.model
    def _prepare_url(self, url, params=None):
        """Prepare a URL for a POST PUT request."""
        if params:
            url_parts = list(urllib.parse.urlparse(url))
            query = dict(urllib.parse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urllib.parse.urlencode(query)
            url = urllib.parse.urlunparse(url_parts)
        return url

    def request(self, method, url, fields=None, headers=None, **kwargs):
        """Make an HTTP request.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """

        if headers is None:
            make_headers(accept_encoding=True)

        conn = self._get_connection()
        with self._handle_request_exceptions(method, url):
            return conn.request(method, url, fields=fields, headers=headers, **kwargs)

    def urlopen(self, method, url, body=None, headers=None, **kwargs):
        """Open a connection to the specified URL.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): URL to request
            body (bytes, optional): Request body
            headers (dict, optional): HTTP headers to include in the request
            **kwargs: Additional arguments to pass to the underlying urlopen method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            URLOpenError: If an error occurs during the urlopen operation
        """
        conn = self._get_connection()
        with self._handle_request_exceptions(method, url, URLOpenError):
            return conn.urlopen(method, url, body=body, headers=headers, **kwargs)

    def get(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a GET request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For GET requests, query parameters are passed as 'fields'
        if params:
            fields = params if fields is None else {**fields, **params}
        return self.request('GET', url, fields=fields, headers=headers, **kwargs)

    def post(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a POST request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields or JSON data to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For POST requests, query parameters must be manually encoded in the URL
        url = self._prepare_url(url, params)
        return self.request('POST', url, fields=fields, headers=headers, **kwargs)

    def put(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a PUT request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields or JSON data to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For PUT requests, query parameters must be manually encoded in the URL
        url = self._prepare_url(url, params)
        return self.request('PUT', url, fields=fields, headers=headers, **kwargs)

    def delete(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a DELETE request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For DELETE requests, query parameters are passed as 'fields'
        if params:
            fields = params if fields is None else {**fields, **params}
        return self.request('DELETE', url, fields=fields, headers=headers, **kwargs)

    def head(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a HEAD request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For HEAD requests, query parameters are passed as 'fields'
        if params:
            fields = params if fields is None else {**fields, **params}
        return self.request('HEAD', url, fields=fields, headers=headers, **kwargs)

    def options(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make an OPTIONS request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For OPTIONS requests, query parameters are passed as 'fields'
        if params:
            fields = params if fields is None else {**fields, **params}
        return self.request('OPTIONS', url, fields=fields, headers=headers, **kwargs)

    def patch(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a PATCH request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields or JSON data to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For PATCH requests, query parameters must be manually encoded in the URL
        url = self._prepare_url(url, params)
        return self.request('PATCH', url, fields=fields, headers=headers, **kwargs)

    def trace(self, url, fields=None, headers=None, params=None, **kwargs):
        """Make a TRACE request.

        Args:
            url (str): URL to request
            fields (dict, optional): Form fields to include in the request
            headers (dict, optional): HTTP headers to include in the request
            params (dict, optional): Query parameters to include in the request
            **kwargs: Additional arguments to pass to the underlying request method

        Returns:
            urllib3.response.HTTPResponse: The HTTP response

        Raises:
            RequestError: If an error occurs during the request
        """
        # For TRACE requests, query parameters are passed as 'fields'
        if params:
            fields = params if fields is None else {**fields, **params}
        return self.request('TRACE', url, fields=fields, headers=headers, **kwargs)

    def close(self):
        """Close the connection and clear it from the cache.

        Raises:
            HTTPClientError: If an error occurs during the operation
        """
        try:
            # Get connection from class-level cache
            connection = None
            if self._name in self._connection_cache:
                connection = self._connection_cache[self._name]

            if connection:
                with self._handle_connection_exceptions(HTTPClientError):
                    connection.close()

            # Clear from class-level cache
            if self._name in self._connection_cache:
                self._connection_cache[self._name] = None

            _logger.debug("Closed connection for %s", self._name)
        except Exception as e:
            _logger.error("Error closing connection for %s: %s", self._name, str(e))
            raise HTTPClientError(f"Error closing connection for {self._name}: {str(e)}")
