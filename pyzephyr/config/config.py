import json
import logging
from urllib.parse import urlunparse

log = logging.getLogger(__name__)

class ZephyrConfig:
    """ Maintain endpoint to analytics service and a set of BasicAuth credentials to access it
    """
    def __init__(self, endpoint=None, creds=None):
        self._endpoint = endpoint
        self._creds = creds

    @property
    def analytics_endpoint(self):
        """Calculate configured location of the API.
        """
        scheme = self._endpoint['scheme']
        netloc = self._endpoint['netloc']
        path = self._endpoint['odata']
        parts = scheme, netloc, path, '', '', ''
        url = urlunparse(parts)
        return url

    @property
    def client_id(self):
        return self._creds['client_id']

    @property
    def client_secret(self):
        return self._creds['client_secret']

    @property
    def auth(self):
        """
        :return: tuple of client id and secret suitable for requests auth helper
        """
        a = (self._creds['client_id'], self._creds['client_secret'])
        return a

    def serialize(self):
        serializable = dict()
        serializable['endpoint'] = self._endpoint
        serializable['creds'] = self._creds
        return serializable


def get_configuration(config_file):
    """
    Load configuration settings
    """
    data = None

    try:
        with open(config_file, 'r') as f:
            data = json.load(f)

    except FileNotFoundError:
        log.info("Cannot find configuration file: %s" % config_file)

    return data

def get_credentials(creds_file, creds_to_use):
    """
    Keep credentials secure.

    Do not store credentials in the source file where they will end up in the source repository.
    Do not include secrets to any session objects.
    Always load secrets on demand from a secure store.

    Multiple credentials may be stored in the JSON encoded credentials file.

    :param creds_file: application credentials file
    :param creds_to_use: name of one set of credentials to fetch ID and Secret

    :return: tuple (client_id, client_secret)
    """

    creds = dict()

    try:
        with open(creds_file, 'r') as f:
            data = json.load(f)
            try:
                creds['client_id'] = data[creds_to_use]['client_id']
                creds['client_secret'] = data[creds_to_use]['client_secret']
            except KeyError:
                log.info("Cannot find credentials for {} in {}".format(creds_to_use, creds_file))

    except FileNotFoundError:
        log.info("Cannot find credentials file: %s" % creds_file)

    return creds
