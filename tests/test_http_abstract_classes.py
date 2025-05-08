# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
from odoo.tests import tagged
import json


@tagged('class_inheritance')
class TestHttpAbstractClasses(TransactionCase):
    """Test HTTP abstract classes by inheriting from them"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test the abstract classes
        cls.http_pool = cls.env['http.pool.abstract']
        cls.https_pool = cls.env['https.pool.abstract']
        cls.pool_manager = cls.env['http.pool.manager.abstract']

        # Use httpbin.org for testing
        host = 'httpbin.org'
        for class_abstract in (cls.http_pool, cls.https_pool):
            class_abstract._set_http_connection({'host': host})

    def _test_pool_abstract(self, pool):
        """Helper method to test HTTP/HTTPS pool abstract classes"""

        # Test GET request
        response = pool.get('/get')
        self.assertEqual(response.status, 200)

        # Test POST request
        test_data = '{"test": "value"}'
        headers = {'Content-Type': 'application/json'}
        response = pool.post('/post', body=test_data, headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['json'], {"test": "value"})

        # Test PUT request
        response = pool.put('/put', body=test_data, headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['json'], {"test": "value"})

        # Test DELETE request
        response = pool.delete('/delete')
        self.assertEqual(response.status, 200)

    def test_http_pool_abstract(self):
        """Test HTTP pool abstract class"""
        self._test_pool_abstract(self.http_pool)

    def test_https_pool_abstract(self):
        """Test HTTPS pool abstract class"""
        self._test_pool_abstract(self.https_pool)

    def test_pool_manager_abstract(self):
        """Test pool manager abstract class"""
        # Set options for pool manager with multiple pools
        self.pool_manager._set_http_connection({'num_pools': 10})

        # Test connection_from_host
        conn = self.pool_manager.connection_from_host('httpbin.org', scheme='https')
        self.assertTrue(conn)

        # Test connection_from_url
        conn = self.pool_manager.connection_from_url('https://httpbin.org')
        self.assertTrue(conn)

        # Test making requests to multiple hosts with different headers

        # First host: httpbin.org
        # Define custom headers for httpbin.org
        httpbin_headers = {
            'Content-Type': 'application/json',
            'X-Custom-Header': 'httpbin-value'
        }

        # Test GET request to httpbin.org with custom headers
        response = self.pool_manager.get('https://httpbin.org/headers', headers=httpbin_headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        # Verify custom header was sent
        self.assertEqual(data['headers']['X-Custom-Header'], 'httpbin-value')

        # Test POST request to httpbin.org with custom headers
        test_data = '{"test": "value"}'
        response = self.pool_manager.post('https://httpbin.org/post', body=test_data, headers=httpbin_headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['json'], {"test": "value"})
        self.assertEqual(data['headers']['X-Custom-Header'], 'httpbin-value')

        # Second host: postman-echo.com
        # Define different custom headers for postman-echo.com
        postman_headers = {
            'Content-Type': 'application/json',
            'X-Custom-Header': 'postman-value'
        }

        # Test GET request to postman-echo.com with custom headers
        response = self.pool_manager.get('https://postman-echo.com/headers', headers=postman_headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        # Verify custom header was sent
        self.assertEqual(data['headers']['x-custom-header'], 'postman-value')

        # Test POST request to postman-echo.com with custom headers
        test_data = '{"test": "different-value"}'
        response = self.pool_manager.post('https://postman-echo.com/post', body=test_data, headers=postman_headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['json'], {"test": "different-value"})
        self.assertEqual(data['headers']['x-custom-header'], 'postman-value')

        # Verify that we can switch back to the first host with its specific headers
        response = self.pool_manager.get('https://httpbin.org/headers', headers=httpbin_headers)
        self.assertEqual(response.status, 300)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['headers']['X-Custom-Header'], 'httpbin-value')

        # Test pool_kwargs to set default headers for a specific host
        pool_kwargs = {'headers': {'X-Pool-Header': 'pool-value'}}
        conn = self.pool_manager.connection_from_host('httpbin.org', scheme='https', pool_kwargs=pool_kwargs)

        # Make request without explicit headers to verify pool headers are used
        response = conn.request('GET', '/headers')
        self.assertEqual(response.status, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['headers']['X-Pool-Header'], 'pool-value')

        # Test clear method
        self.pool_manager.clear()
