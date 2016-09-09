import logging
import requests

from pyzephyr.config.config import ZephyrConfig

log = logging.getLogger(__name__)


class ZephyrSession(requests.Session):
    """A VSTS REST API session.

    is-a requests.Session, manages HTTP protocol details.

    Filters resource requests and amends them with valid auth.
    """

    def __init__(self, endpoint=None, creds=None):
        """Construct a new client session.
        :param config: dict w description of the endpoint
        :param creds: dict w package of BasicAuth credentials
        """
        super().__init__()

        try:
            self._config = ZephyrConfig(endpoint, creds)
        except KeyError as e:
            log.info("Cannot find configuration for {} in config data".format(e.args[0]))

    def get(self, odata_query, **kwargs):
        """Intercept requests and add authentication

        only Basic Auth supported
        """

        analytics_endpoint = self._config.analytics_endpoint

        log.debug('Requesting odata_query %s from %s', odata_query, analytics_endpoint)

        url = build_analytics_query_url(analytics_endpoint, odata_query=odata_query)

        log.debug('[GET] %s', url)

        r = super().get(url, auth=self._config.auth, **kwargs)

        r.encoding = r.apparent_encoding

        log.debug('Response %s', r.__repr__())

        return r

    def serialize(self):
        """Create a dict that's convenient for web frameworks to save between requests"""
        serializable = dict(self._config.serialize())
        return serializable

    def __repr__(self):
        return str(self.serialize())

def build_analytics_query_url(analytics_endpoint, odata_query=None):
    """
    :param analytics_endpoint: url of the vsts analytics service
    :param odata_query: query expressed in odata syntax
    :return: url for odata query
    """
    url = analytics_endpoint
    if odata_query:
        url += odata_query

    return url