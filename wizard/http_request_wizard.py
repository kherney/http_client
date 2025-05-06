# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import base64
import mimetypes
from ..models.http_connection_pool import HTTPSPoolAbstract


class HttpRequestWizard(models.TransientModel):
    _name = 'http.request.wizard'
    _inherit = 'https.pool.abstract'
    _description = 'HTTP Request Wizard'

    # Input fields
    url = fields.Char(string='URL', required=True, help="The URL to send the request to")
    method = fields.Selection([
        ('get', 'GET'),
        ('post', 'POST'),
        ('put', 'PUT'),
        ('delete', 'DELETE'),
        ('head', 'HEAD'),
        ('options', 'OPTIONS'),
        ('patch', 'PATCH'),
        ('trace', 'TRACE')
    ], string='Method', default='get', required=True, help="HTTP method to use")
    params = fields.Text(string='Parameters', help="HTTP parameters in key=value format, one per line")
    headers = fields.Text(string='Headers', help="HTTP headers in key:value format, one per line")
    body = fields.Text(string='Request Body', help="Request body content")

    # Response fields
    response_status = fields.Integer(string='Status Code', readonly=True)
    response_headers = fields.Text(string='Response Headers', readonly=True)
    response_binary = fields.Binary(string='Binary Response', readonly=True, attachment=False)
    response_filename = fields.Char(string='Filename', readonly=True)
    response_json = fields.Text(string='JSON Response', readonly=True)
    response_html = fields.Html(string='HTML Response', readonly=True, sanitize=False)
    response_text = fields.Text(string='Text Response', readonly=True)

    # Computed field to display the appropriate response
    response_display = fields.Text(string='Response', compute='_compute_response_display')
    content_type = fields.Char(string='Content Type', readonly=True)

    def _get_options(self):
        """Override to extract host from URL"""
        options = super(HttpRequestWizard, self)._get_options()

        # Extract host from URL if not already set
        if 'host' not in options and self.url:
            # Remove protocol
            url = self.url
            if '://' in url:
                url = url.split('://', 1)[1]

            # Extract host
            host = url.split('/', 1)[0]
            if ':' in host:  # Handle port in host
                host, port = host.split(':', 1)
                options['port'] = int(port)

            options['host'] = host

        return options

    def _parse(self, field: str, splitter=':', delimiter='\n'):
        """Pars from text field to dictionary"""
        headers_dict = {}
        column = getattr(self, field)
        if column:
            for line in column.strip().split(delimiter):
                if splitter in line:
                    key, value = line.split(splitter, 1)
                    headers_dict[key.strip()] = value.strip()
        return headers_dict

    @api.depends('response_binary', 'response_json', 'response_html', 'response_text')
    def _compute_response_display(self):
        """Compute the display field based on the response type"""
        for record in self:
            if record.response_json:
                record.response_display = record.response_json
            elif record.response_text:
                record.response_display = record.response_text
            elif record.response_binary:
                record.response_display = f"Binary content: {record.response_filename}"
            elif record.response_html:
                record.response_display = "HTML content (see HTML tab)"
            else:
                record.response_display = "No response"

    def make_request(self):
        """Make the HTTP request and process the response"""
        self.ensure_one()

        # Clear previous response
        self.response_status = False
        self.response_headers = False
        self.response_binary = False
        self.response_filename = False
        self.response_json = False
        self.response_html = False
        self.response_text = False
        self.content_type = False

        try:
            # initialize the params column used in get requests
            params = None
            # Parse headers
            headers = self._parse('headers')

            # Parse parameters just for get methods
            if self.method == 'get':
                params = self._parse('params', splitter='=', delimiter='\n')

            # Extract path from URL
            url = self.url
            if '://' in url:
                url = url.split('://', 1)[1]

            path = '/'
            if '/' in url and url.index('/') > 0:
                path = '/' + url.split('/', 1)[1]

            # Make the request
            response = self.request(
                method=self.method,
                url=path,
                body=self.body if self.body else None,
                headers=headers,
                fields=params,
            )

            # Process response
            self.response_status = response.status

            # Process headers
            headers_text = ""
            for key, value in response.headers.items():
                headers_text += f"{key}: {value}\n"
            self.response_headers = headers_text

            # Get content type
            content_type = response.headers.get('Content-Type', '')
            self.content_type = content_type

            # Process response body based on content type
            data = response.data

            if content_type:
                # Binary content
                if 'application/octet-stream' in content_type or 'image/' in content_type or 'audio/' in content_type or 'video/' in content_type:
                    self.response_binary = base64.b64encode(data)

                    # Try to determine filename
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=', 1)[1].strip('"\'')
                    else:
                        # Generate filename based on content type
                        ext = mimetypes.guess_extension(content_type.split(';')[0].strip()) or ''
                        filename = f"response{ext}"

                    self.response_filename = filename

                # JSON content
                elif 'application/json' in content_type:
                    try:
                        json_data = json.loads(data.decode('utf-8'))
                        self.response_json = json.dumps(json_data, indent=2)
                    except json.JSONDecodeError:
                        self.response_text = data.decode('utf-8', errors='replace')

                # HTML content
                elif 'text/html' in content_type:
                    self.response_html = data.decode('utf-8', errors='replace')

                # Text content
                elif 'text/' in content_type:
                    self.response_text = data.decode('utf-8', errors='replace')

                # Other content types
                else:
                    try:
                        # Try to decode as text
                        self.response_text = data.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        # If it fails, treat as binary
                        self.response_binary = base64.b64encode(data)
                        self.response_filename = "response"
            else:
                # No content type, try to guess
                try:
                    # Try to parse as JSON
                    json_data = json.loads(data.decode('utf-8'))
                    self.response_json = json.dumps(json_data, indent=2)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    try:
                        # Try to decode as text
                        self.response_text = data.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        # If it fails, treat as binary
                        self.response_binary = base64.b64encode(data)
                        self.response_filename = "response"

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'http.request.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }

        except Exception as e:
            self.response_text = f"Error: {str(e)}"
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'http.request.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }
