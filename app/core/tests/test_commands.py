"""
Test custom Django management commands.
"""
from unittest.mock import patch  # Simulate whether a database is returning a response or not

from psycopg2 import OperationalError as Psycopg2Error  # error if connect before databse ready

from django.core.management import call_command  # simuilate a command call
from django.db.utils import OperationalError  # another possible eroor if before datase is ready
from django.test import SimpleTestCase


# Provide path to command we are mocking, patches add new arguments to all methods
@patch('core.management.commands.wait_for_db.Command.check')  # check comes from BaseCommand class
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        # ensure check is called with default database
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for database when getting OperationalError

        side_effect pass in various different items handeled differently based on their type

        First 2 times we call mocked method, we want it to raise Psycopg2Error
        Raised if postgres has even started yet and isnt ready to accept connections

        Raise Operational Error (Django) 3 Times
        when postres is ready to accept connections but hasnt created database

        Finally we get true back on the 6th run
        since True is not exception, it knows to return it
        """
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]  # Raise Exceptions that would be raised if db not ready

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
