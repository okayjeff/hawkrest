import mock

from django.core.management.base import CommandError
from django.core.management import call_command

from tests.base import BaseTest


def exec_cmd(**kwargs):
    call_command('hawkrequest', **kwargs)


class UnauthorizedResponse:
    """
    Mock unauthorized response object that omits 'Server-Authorization' key.
    """
    def __init__(self):
        self.headers = {}
        self.text = 'Unauthorized'


class AuthorizedResponse:
    """
    Mock authorized response object with 'Server-Authorization' key.
    """
    def __init__(self):
        self.headers = {
            'Server-Authorization': 'xyz',
            'Content-Type': 'text/plain'
        }
        self.text = 'Authorized'


class TestManagementCommand(BaseTest):

    @classmethod
    def setUpTestData(cls):
        cls.url = 'http://testserver.com'
        cls.creds = 'script-user'

    def test_error_raised_if_requests_not_imported(self):
        pass

    def test_error_raised_if_url_not_specified(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds=self.creds)

    def test_error_raised_if_creds_missing(self):
        with self.assertRaises(CommandError):
            exec_cmd(url=self.url)

    def test_error_raises_if_creds_not_found(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds='nonexistent')

    @mock.patch('requests.get', mock.Mock(return_value=UnauthorizedResponse()))
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_unverified_without_auth_header(self, mock_mohawk):
        exec_cmd(url=self.url, creds=self.creds)
        self.assertFalse(mock_mohawk.called)

    @mock.patch('requests.get', mock.Mock(return_value=AuthorizedResponse()))
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_verified_with_auth_header(self, mock_mohawk):
        exec_cmd(url=self.url, creds=self.creds)
        self.assertTrue(mock_mohawk.called)
