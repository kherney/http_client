# -*- coding: utf-8 -*-
{
    'name': "Odoo HTTP Client",
    'sequence': 369,

    'summary': "HTTP client for Odoo with API request functionality",

    'description': """
    This module provides HTTP client functionality for Odoo:

    * Make HTTP requests from Odoo
    * Support for all HTTP methods (GET, POST, PUT, DELETE, etc.)
    * API request interface (Wizard) for testing APIs
    * Handle different response types (JSON, HTML, text, binary)
    * Reusable HTTP connection abstractions
    * Extensible architecture for custom HTTP clients

    Technical Features:

    * Abstract models for HTTP connections
    * Connection pooling for better performance
    * Comprehensive error handling
    * Support for both HTTP and HTTPS
    * Easy integration with other modules
    """,

    'author': "Kevin Herney <kevinh939@gmail.com>",
    'url': "https://github.com/kherney/http_client",
    'maintainer': 'kevinh939@gmail.com',
    'website': "https://kherney.github.io/",

    'category': 'Technical',
    'version': '17.0.0.0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Models Views
        # Wizard Views
        'wizard/http_request_wizard_views.xml',
        # Actions Views
        # Other Views
        # Menus
        'views/menus.xml'
        # Report Templates
        # Mail Templates
        # Component Templates
        # Other Templates
    ],

    'assets': {},

    'application': False,
    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'demo': [],
    'test': ['tests'],
    'external_dependencies': {
        'python': ['urllib3'],
    },
}
