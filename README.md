# Odoo HTTP Client

A powerful HTTP client module for Odoo with Postman-like functionality, providing a robust framework for making HTTP
requests and integrating with external APIs.

## Features

- Make HTTP requests from Odoo
- Support for all HTTP methods (GET, POST, PUT, DELETE, etc.)
- Postman-like interface for testing APIs
- Handle different response types (JSON, HTML, text, binary)
- Reusable HTTP connection abstractions
- Extensible architecture for custom HTTP clients

## Technical Features

- Abstract models for HTTP connections
- Connection pooling for better performance
- Comprehensive error handling
- Support for both HTTP and HTTPS
- Easy integration with other modules

## Module Structure

The module is organized into the following components:

- **Abstract Models**: Base classes for HTTP connections
    - `HTTPAbstract`: Base abstract class for all HTTP connections
    - `HTTPPoolAbstract`: Abstract class for HTTP connection pools
    - `HTTPSPoolAbstract`: Abstract class for HTTPS connection pools
    - `PoolManagerAbstract`: Abstract class for managing multiple connection pools

- **Exceptions**: Custom exceptions for error handling
    - `HTTPClientError`: Base exception for all HTTP client errors
    - `ConnectionInitError`: Base exception for connection initialization errors
    - `RequestError`: Exception for request failures
    - And more specialized exceptions

- **Wizard**: User interface for making HTTP requests
    - `HttpRequestWizard`: Transient model for the HTTP request wizard
    - Wizard views and actions

## Using the HTTP Request Wizard

The HTTP Request Wizard provides a Postman-like interface for making HTTP requests directly from Odoo:

1. Navigate to **Settings > Technical > HTTP Request**
2. Enter the URL, select the HTTP method, and configure headers/parameters
3. For GET requests, use the Parameters field to specify query parameters
4. For POST/PUT/PATCH requests, use the Request Body field to specify the payload
5. Click "Send Request" to execute the request
6. View the response in the appropriate tab (JSON, HTML, Text, Binary)

## Using the Abstract Classes in Other Models

You can extend the HTTP client functionality in your own models by inheriting from the appropriate abstract class:

### Basic HTTP Client

```python
from odoo import models


class MyHTTPClient(models.Model):
    _name = 'my.http.client'
    _inherit = 'https.pool.abstract'
    _description = 'My HTTP Client'

    # Configure the connection
    _http_connection = {
        'host': 'api.example.com',
        'timeout': 10.0,
        'retries': 3,
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_TOKEN'
        }
    }

    def call_api_endpoint(self, endpoint, data=None):
        """Call a specific API endpoint"""
        path = f"/{endpoint}"
        return self.post(path, fields=data)
```

### Using Connection Pooling

```python
from odoo import models


class MyPoolManager(models.Model):
    _name = 'my.pool.manager'
    _inherit = 'http.pool.manager.abstract'
    _description = 'My Pool Manager'

    _http_connection = {
        'num_pools': 5,
        'timeout': 5.0,
        'retries': 2
    }

    def call_multiple_apis(self, apis):
        """Call multiple APIs using connection pooling"""
        results = {}
        for api in apis:
            conn = self.connection_from_url(api['url'])
            response = conn.request(
                method=api['method'],
                url=api['path'],
                fields=api.get('data')
            )
            results[api['name']] = response.data
        return results
```

## Error Handling

The module provides comprehensive error handling through custom exceptions:

```python
from odoo import models
from odoo.exceptions import UserError


class MyAPIClient(models.Model):
    _name = 'my.api.client'
    _inherit = 'https.pool.abstract'
    _description = 'My API Client'

    _http_connection = {
        'host': 'api.example.com',
    }

    def safe_api_call(self):
        try:
            response = self.get('/endpoint')
            return response.data
        except RequestError as e:
            # Handle request errors
            raise UserError(f"API request failed: {str(e)}")
        except HTTPClientError as e:
            # Handle other HTTP client errors
            raise UserError(f"HTTP client error: {str(e)}")
```

## Best Practices

1. **Connection Reuse**: Inherit from the abstract classes in your models to reuse connections
2. **Error Handling**: Use try/except blocks to handle exceptions properly
3. **Timeout Configuration**: Always set appropriate timeouts to prevent hanging requests
4. **Connection Pooling**: Use connection pooling for better performance when making multiple requests
5. **Resource Cleanup**: Call `close()` when you're done with a connection to free resources

## Integration with Other Modules

This module is designed to be easily integrated with other Odoo modules, allowing you to dynamically interact with
different APIs. You can use the abstract classes in your custom modules to create specialized API clients for various
services:

- Create REST API clients for third-party services
- Implement webhook handlers for external systems
- Build integration bridges between Odoo and external platforms
- Develop custom connectors for specific business needs

The flexible architecture allows you to adapt the HTTP client to work with any API, regardless of its structure or
authentication requirements.

## Contributing

Contributions to improve this module are welcome! If you have ideas for new features, integrations, or improvements,
please feel free to:

1. Fork the repository
2. Create a branch for your feature
3. Submit a pull request

You can also report issues or suggest enhancements through the GitHub repository.

## Support

If you need assistance with implementing or extending this module, please contact:

- Email: kevinh939@gmail.com
- GitHub: https://github.com/kherney/http_client

## License

AGPL-3
