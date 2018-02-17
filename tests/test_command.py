import mock

from django.core.management.base import CommandError
from django.core.management import call_command

from tests.base import BaseTest


def exec_cmd(**kwargs):
    call_command('hawkrequest', **kwargs)


class UnauthorizedResponse:
    def __init__(self):
        self.headers = {}
        self.text = 'Unauthorized'


class AuthorizedResponse:
    def __init__(self):
        self.headers = {
            'Server-Authorization': 'xyz',
            'Content-Type': 'text/plain'
        }
        self.text = 'Authorized'


module_import = 'hawkrest.management.commands.hawkrequest.get_requests_module'
cmd_request = 'hawkrest.management.commands.hawkrequest.request'


class TestManagementCommand(BaseTest):

    @mock.patch(module_import, mock.Mock(side_effect=ImportError))
    def test_error_raised_if_requests_not_imported(self):
        with self.assertRaises(CommandError):
            exec_cmd(url=self.url, creds=self.credentials_id)

    def test_error_raised_if_url_not_specified(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds=self.credentials_id)

    def test_error_raised_if_creds_missing(self):
        with self.assertRaises(CommandError):
            exec_cmd(url=self.url)

    def test_error_raises_if_creds_not_found(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds='nonexistent')

    @mock.patch(cmd_request, mock.Mock(return_value=UnauthorizedResponse()))
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_unverified_without_auth_header(self, mock_mohawk):
        exec_cmd(url=self.url, creds=self.credentials_id)
        self.assertFalse(mock_mohawk.called)

    @mock.patch(cmd_request, mock.Mock(return_value=AuthorizedResponse()))
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_verified_with_auth_header(self, mock_mohawk):
        exec_cmd(url=self.url, creds=self.credentials_id)
        self.assertTrue(mock_mohawk.called)
