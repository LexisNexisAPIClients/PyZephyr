import json
import logging
from urllib.parse import urlunparse

log = logging.getLogger(__name__)


def get_credentials(file_name, name):
    """
    Keep credentials secure.

    Do not store credentials in the source file where they will end up in the source repository.
    Do not include secrets to any session objects.
    Always load secrets on demand from a secure store.

    Multiple credentials may be stored in the JSON encoded credentials file.

    :param file_name: application credentials file
    :param name: name of one set of credentials to fetch ID and Secret

    :return: tuple (client_id, client_secret)
    """

    client_id = ''
    client_secret = ''

    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
            try:
                client_id = data['credentials'][name]['client_id']
                client_secret = data['credentials'][name]['client_secret']
            except KeyError:
                log.info("Cannot find credentials for {} in {}".format(name, file_name))

    except FileNotFoundError:
        log.info("Cannot find credentials file: %s" % file_name)

    return client_id, client_secret


class LexisConfig():
    def __init__(self,
                 redirect_url=None,
                 auth_page_path=None,
                 token_path=None,
                 location=None,
                 auth_page_location=None,
                 token_location=None,
                 services_api_location=None):

        self._redirect_url = redirect_url
        self._auth_page_path = auth_page_path
        self._token_path = token_path
        self._location = location
        self._auth_page_location = auth_page_location
        self._token_location = token_location
        self._services_api_location = services_api_location

        # required, catch keyerror
        # TODO: add a try block and check for keyerror then raise custom error if found
        auth = location['auth']
        services_api = location['services-api']

    @classmethod
    def test_double(cls):
        kwargs = dict()
        kwargs['redirect_url'] = "http://127.0.0.1:4999/callback"
        kwargs['auth_page_path'] = "/oauth/v2/authorize"
        kwargs['token_path'] = "/oauth/v2/token"
        kwargs['location'] = {"auth":
                                {"scheme": "https",
                                 "netloc": "auth-api.lexisnexis.com"},
                            "services-api":
                                {"scheme": "https",
                                 "netloc": "services-api.lexisnexis.com"},
                            "dev_auth":
                                {"scheme": "http",
                                 "netloc": "dvc7720.lexisnexis.com:39143"}}
        kwargs['auth_page_location'] = 'auth'
        kwargs['token_location'] = 'auth'
        kwargs['services_api_location'] = 'services-api'
        
        return cls(**kwargs)

    @property
    def auth_page_location(self):
        return self._auth_page_location

    @auth_page_location.setter
    def auth_page_location(self, location):
        self._auth_page_location = location

    @property
    def auth_page_url(self):
        scheme = self._location[self.auth_page_location]['scheme']
        netloc = self._location[self.auth_page_location]['netloc']
        path = self._auth_page_path
        parts = scheme, netloc, path, '', '', ''
        url = urlunparse(parts)
        return url

    @property
    def services_api_location(self):
        return self._services_api_location

    @services_api_location.setter
    def services_api_location(self, location):
        self._services_api_location = location

    @property
    def services_api_url(self):
        """Calculate configured location of the API. This is the endpoint LexisNexis publishes

        Path is the version of the API, and is completed in the service_api module. Version is bound
        to the services_api module.
        """
        scheme = self._location[self.services_api_location]['scheme']
        netloc = self._location[self.services_api_location]['netloc']
        path = ''
        parts = scheme, netloc, path, '', '', ''
        url = urlunparse(parts)
        return url

    @property
    def token_location(self):
        return self._token_location

    @token_location.setter
    def token_location(self, location):
        self._token_location = location

    @property
    def token_url(self):
        scheme = self._location[self.token_location]['scheme']
        netloc = self._location[self.token_location]['netloc']
        path = self._token_path
        parts = scheme, netloc, path, '', '', ''
        url = urlunparse(parts)
        return url

    def serialize(self):
        serializable = dict()
        serializable['redirect_url'] = self._redirect_url
        serializable['auth_page_path'] = self._auth_page_path
        serializable['token_path'] = self._token_path
        serializable['location'] = self._location
        serializable['auth_page_location'] = self._auth_page_location
        serializable['token_location'] = self._token_location
        serializable['services_api_location'] = self._services_api_location

        return serializable


def get_lexis_config(file_name):
    """
    Load configuration settings  and guard for missing ones
    """

    try:
        with open(file_name, 'r') as f:
            data = json.load(f)

    except FileNotFoundError:
        log.info("Cannot find configuration file: %s" % file_name)

    return data
