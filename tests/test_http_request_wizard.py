# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
import json


@tagged('wizard_request')
class TestHttpRequestWizard(TransactionCase):
    """Test HTTP Request Wizard functionality with httpbin.org"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a wizard instance for testing
        cls.wizard = cls.env['http.request.wizard'].create({
            'url': 'https://httpbin.org',
        })

    def test_get_request(self):
        """Test GET request to httpbin.org/get"""
        wizard = self.wizard.copy({'url': 'https://httpbin.org/get', 'method': 'get'})
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['url'], 'https://httpbin.org/get')

    def test_post_request(self):
        """Test POST request to httpbin.org/post"""
        test_data = '{"test": "value"}'
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/post',
            'method': 'post',
            'body': test_data,
            'headers': 'Content-Type: application/json'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['url'], 'https://httpbin.org/post')
        self.assertEqual(response['json'], {"test": "value"})

    def test_put_request(self):
        """Test PUT request to httpbin.org/put"""
        test_data = '{"test": "value"}'
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/put',
            'method': 'put',
            'body': test_data,
            'headers': 'Content-Type: application/json'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['url'], 'https://httpbin.org/put')
        self.assertEqual(response['json'], {"test": "value"})

    def test_delete_request(self):
        """Test DELETE request to httpbin.org/delete"""
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/delete',
            'method': 'delete'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['url'], 'https://httpbin.org/delete')

    def test_patch_request(self):
        """Test PATCH request to httpbin.org/patch"""
        test_data = '{"test": "value"}'
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/patch',
            'method': 'patch',
            'body': test_data,
            'headers': 'Content-Type: application/json'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['url'], 'https://httpbin.org/patch')
        self.assertEqual(response['json'], {"test": "value"})

    def test_head_request(self):
        """Test HEAD request to httpbin.org/get"""
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/get',
            'method': 'head'
        })
        result = wizard.make_request()

        # Verify response - HEAD requests don't have a body
        self.assertEqual(wizard.response_status, 200)
        self.assertFalse(wizard.response_json)

    def test_options_request(self):
        """Test OPTIONS request to httpbin.org/get"""
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/get',
            'method': 'options'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        # OPTIONS typically returns headers with allowed methods
        self.assertTrue(wizard.response_headers)
        self.assertIn('Allow:', wizard.response_headers)

    def test_get_with_params(self):
        """Test GET request with URL parameters"""
        wizard = self.wizard.copy({
            'url': 'https://httpbin.org/get',
            'method': 'get',
            'params': 'param1=value1\nparam2=value2'
        })
        result = wizard.make_request()

        # Verify response
        self.assertEqual(wizard.response_status, 200)
        self.assertTrue(wizard.response_json)

        # Parse JSON response
        response = json.loads(wizard.response_json)
        self.assertEqual(response['args'], {'param1': 'value1', 'param2': 'value2'})
