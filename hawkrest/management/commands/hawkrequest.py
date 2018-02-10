from django.core.management.base import BaseCommand, CommandError
from mohawk import Sender

from hawkrest import HawkAuthentication


DEFAULT_HTTP_METHOD = 'GET'

CMD_OPTIONS = {
    '--url': {
        'action': 'store',
        'type': str,
        'help': 'Absolute URL to request.'
    },
    '--creds': {
        'action': 'store',
        'type': str,
        'help': 'ID for Hawk credentials.'
    },
    '-X': {
        'action': 'store',
        'type': str,
        'help': 'Request method. Default: {}.'.format(DEFAULT_HTTP_METHOD),
        'default': DEFAULT_HTTP_METHOD
    },
    '-d': {
        'action': 'store',
        'type': str,
        'help': 'Query string parameters.'
    }
}


class Command(BaseCommand):
    help = 'Make a Hawk authenticated request'

    def add_arguments(self, parser):
        for opt, config in CMD_OPTIONS.items():
            parser.add_argument(opt, **config)

    def handle(self, *args, **options):
        try:
            import requests
        except ImportError:
            raise CommandError('To use this command you first need to '
                               'install the requests module')
        url = options['url']
        if not url:
            raise CommandError('Specify a URL to load with --url')

        qs = options['d'] or ''
        request_content_type = ('application/x-www-form-urlencoded'
                                if qs else 'text/plain')
        method = options['X']

        creds_key = options['creds']
        credentials = HawkAuthentication().hawk_credentials_lookup(creds_key)

        sender = Sender(credentials,
                        url, method.upper(),
                        content=qs,
                        content_type=request_content_type)

        headers = {'Authorization': sender.request_header,
                   'Content-Type': request_content_type}

        do_request = getattr(requests, method.lower())
        res = do_request(url, data=qs, headers=headers)

        self.stdout.write('{method} -d {qs} {url}'.format(method=method.upper(),
                                                          qs=qs or 'None',
                                                          url=url))
        self.stdout.write(res.text)

        # Verify we're talking to our trusted server.
        self.stdout.write(str(res.headers))
        auth_hdr = res.headers.get('Server-Authorization', None)
        if auth_hdr:
            sender.accept_response(auth_hdr,
                                   content=res.text,
                                   content_type=res.headers['Content-Type'])
            self.stdout.write('<response was Hawk verified>')
        else:
            self.stdout.write('** NO Server-Authorization header **')
            self.stdout.write('<response was NOT Hawk verified>')
