# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.sql_db import Cursor
from odoo.exceptions import UserError, AccessError

from contextlib import contextmanager
from typing import Any, Dict, List

import logging

_logger = logging.getLogger(__name__)


class HTTPSPoolWeb(models.AbstractModel):
    """Model class for the odoo backend web view"""
    _name = 'https.pool.web'
    _inherit = 'https.pool.abstract'
    _description = 'HTTP Pool for odoo backend web view'

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """
        Search and fetch data while ensuring data synchronization through an external API.

        Processes a dynamic search operation with pagination and sorting from the model
        and performs data synchronization with an external API before returning results.
        Provides robust error handling and leverages database savepoint for transactional
        safety during API fetch operations.

        Raises:
            UserError: Raised if an exception occurs during the API data fetch process and the
            context does not suppress the error ('not_raise' context is False).
        """
        with self.env.registry.cursor() as cr:
            try:
                with cr.savepoint(flush=False):
                    self.with_context(no_fetch_data=True).fetch_data(cr)
                    _logger.info("")
            except Exception as e:
                _logger.error("")
                if not self.env.context('not_raise', False):
                    raise UserError(e)

        return super(HTTPSPoolWeb, self).search_read(domain, field_names, offset=offset, limit=limit, order=order)

    def write(self, vals):
        """ Override method for the model."""
        self.push_data(self._prepare_context('write', vals=vals))
        return super(HTTPSPoolWeb, self).write(vals)

    def unlink(self):
        """ Override method for the model."""
        self.push_data(self._prepare_context('unlink'))
        return super(HTTPSPoolWeb, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """ Override method for the model."""
        self.push_data(self._prepare_context('create', vals_list))
        return super(HTTPSPoolWeb, self).create(vals_list)

    # Customs abstract's class methods

    def _prepare_context(self, method: str, vals: Dict | List = None, default_context: Dict = None) -> Dict[
        str, List[Dict[str, Any],]]:

        """
        Prepares a context dictionary based on the provided method, values, and default context.

        The function takes a method name, optional values, and an optional default context dictionary
        to construct a new context dictionary. The method name serves as the key, and the associated
        value is determined by processing the instance's records or the provided values. The function
        handles exceptions related to access rights and update issues.

        Parameters:
            method (str): The method name to be used as a key in the context dictionary.
            vals (Dict | List, optional): The values to include in the context. It can be either a
                dictionary or a list. Defaults to None.
            default_context (Dict, optional): The default  context to use as a base. Defaults to None.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary containing the prepared context with the
                method name as the key and processed values for the given context.
        """
        context = default_context is None and {} or default_context
        vals = vals is None and [] or vals

        if isinstance(vals, dict):
            vals = [vals]

        try:
            context.update([(method, {'vals': record and record.read() or vals for record in (self or [None])})])
        except ValueError:
            _logger.error("Not was possible fetch record using read")
            context.update([(method, {})])
        except AccessError as e:
            _logger.error("Not possible get record data bcause not have enough access rights.")
            if not self.env.context.get('not_raise', False):
                raise AccessError(e)
            context.update([(method, {})])

        return context

    def _push_data(self, context: Dict[str, List[Dict[str, Any],]]):
        """
        Push data to a specific method with the given context.

        This method extracts the method name and related data from the
        provided context dictionary and initiates the data push operation.
        If the extracted method or data is missing, the function returns None.
        The function also safely handles web errors during the data push process
        using the '_handle_web_error' context manager.

        Raises:
            Any exceptions raised while pushing data are caught within the
            '_handle_web_error' context manager and handled appropriately.
        """
        method = data = None
        for key, value in context.items():
            method = key
            data = value
        if not (method and data):
            return None
        with self._handle_web_error(method):
            return self.push_data(context)

    def push_data(self, context: Dict[str, List[Dict[str, Any],]]) -> None:
        return

    @api.model
    def fetch_data(self, cr: Cursor) -> Any:
        """
        Fetches data from API to odoo DB given database cursor.

        This method is designed to retrieve data from the given REST API conf to the DB by executing
        specific queries using the provided cursor object. Avoid using self to access the database
        to prevent overload server.

        Parameters:
            cr (Cursor): A database cursor used to execute queries and fetch data.

        Returns:
            Any: Data retrieved from the database using the provided cursor.
        """

        if self.env.context.get('no_fetch_data', False):
            _logger.info("Avoiding API data synchronization given in context, skipping fetch data.")
            return
        return

    @contextmanager
    def _handle_web_error(self, method: str):
        """
        Handles web errors during operations within the context manager. It logs the error and optionally raises a
        UserError exception depending on the provided context.

        Yields
        ------
        None
            Executes the block of code within the context manager.

        Raises
        ------
        UserError
            If an error occurs during the execution of the block and the context does not include 'not_raise' set to
            True, a UserError is raised with the details of the encountered error.
        """

        try:
            yield
        except Exception as e:
            _logger.error("Error in web view try to %s data: %s", method, str(e))
            if not self.env.context.get('not_raise', False):
                raise UserError(f"Error in web view try to {method} data: {str(e)}")
