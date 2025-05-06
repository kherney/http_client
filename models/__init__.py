# -*- coding: utf-8 -*-
"""
HTTP Client Models.

This package contains the models for the HTTP client module:
- http_abstract: Base abstract class for HTTP connections
- exceptions: Custom exceptions for error handling
- http_connection_pool: HTTP and HTTPS connection pool implementations
- http_pool_manager: Pool manager implementation for managing multiple connection pools
"""

from . import (
    http_abstract,
    exceptions,
    http_connection_pool,
    http_pool_manager,
)
