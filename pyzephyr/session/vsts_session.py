import logging

from oauthlib.common import generate_token, urldecode
from oauthlib.oauth2 import WebApplicationClient, InsecureTransportError
from oauthlib.oauth2 import TokenExpiredError, is_secure_transport
import requests

from pyzephyr.config.config import LexisConfig

log = logging.getLogger(__name__)


class VSTSSession(requests.Session):
    """A Lexis Web Services API session.

    Creates a WebApplicationClient as part of a Requests Session.
    is-a requests.Session, manages HTTP protocol details.
    has-a WebApplicationClient, manages OAuth2 framework details.

    Provides syntactic sugar for accessing OAuth attributes.
    Inherits all the plumage of the Lexis services_api.
    Implements methods for fetching and refreshing a token from Lexis authentication services.
    Filters resource requests and amends them with valid token.
    """

    def __init__(self,
                 client_id=None,
                 lexis_config=None,
                 redirect_url=None,
                 state=None,
                 token=None,
                 auth_page_location=None,
                 services_api_location=None,
                 token_location=None):
        """Construct a new Lexis client session.

        :param client_id: Id issued with registration of the application.
        :param lexis_config: Dict for creating config object
        :param redirect_url: Redirect URL set as callback during registration. Required when
        requesting an auth code AND a token.

        """
        super().__init__()

        # OAuth scopes not used in the Lexis Web Services API
        # The service demands one, and this is it. Hardcoded.
        scope = ['http://oauth.lexisnexis.com/all']

        checked_state = state or generate_token()

        try:
            self._config = LexisConfig(**lexis_config)
        except KeyError as e:
            log.info("Cannot find configuration for {} in config data".format(e.args[0]))

        self.auth_page_location=auth_page_location
        self.services_api_location=services_api_location
        self.token_location=token_location

        self._client = WebApplicationClient(client_id,
                                            scope=scope,
                                            state=checked_state,
                                            redirect_url=redirect_url)

        if token: self.token = token


    @property
    def authorized(self):
        return bool(self._client.access_token)

    @property
    def auth_page_location(self):
        return self._config.auth_page_location

    @auth_page_location.setter
    def auth_page_location(self, location):
        self._config.auth_page_location = location

    @property
    def auth_url(self):
        return self._config.auth_page_url

    @property
    def client_id(self):
        return self._client.client_id

    @property
    def decorated_auth_url(self):
        """Prep URL used in the get or redirect to the Lexis Authorization Server.

        :return: URI decorated with query string
        """
        return self._client.prepare_request_uri(self._config.auth_page_url,
                                                redirect_uri=self.redirect_url,
                                                scope=self._client.scope,
                                                state=self._client.state)

    @property
    def redirect_url(self):
        return self._client.redirect_url

    @redirect_url.setter
    def redirect_url(self, u):
        self._client.redirect_url = u

    @property
    def services_api_url(self):
        return self._config.services_api_url

    @property
    def services_api_location(self):
        return self._config.services_api_location

    @services_api_location.setter
    def services_api_location(self, location):
        self._config.services_api_location = location

    @property
    def state(self):
        return self._client.state

    @state.setter
    def state(self, s):
        self._client.state = s

    @property
    def token(self):
        return self._client.token

    @token.setter
    def token(self, t):
        self._client.token = t
        self._client._populate_attributes(t)
        self._auto_refresh_token_args = self._client.scope

    @property
    def token_location(self):
        return self._config.token_location

    @token_location.setter
    def token_location(self, location):
        self._config.token_location = location

    @property
    def token_url(self):
        return self._config.token_url

    def fetch_token(self, token_url, authorization_response, credentials, **kwargs):
        """Fetch an access token from Lexis token endpoint.

        Scope is established during authentication.  Changing scope during token negotiation, while allowed by
        the OAuth framework, is not supported.

        :param token_url: Token endpoint URL, must use HTTPS.
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you. Has Code embedded in it.
        :param credentials: Tuple of client id and client secret
        :return: A token dict
        """
        if authorization_response:
            self._client.parse_request_uri_response(authorization_response, state=self.state)
        else:
            raise ValueError('Missing authorization code')

        body = self._client.prepare_request_body(code=self._client.code,
                                                 redirect_uri=self._client.redirect_url, scope=self._client.scope)

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        r = self.post(token_url,
                      auth=credentials,
                      data=dict(urldecode(body)),
                      headers=headers,
                      **kwargs)

        log.debug('Prepared fetch token request body %s', body)
        log.debug('Request to fetch token completed with status %s.', r.status_code)
        log.debug('Request headers were %s', r.request.headers)
        log.debug('Request body was %s', r.request.body)
        log.debug('Response headers were %s and content %s.', r.headers, r.text)

        self._client.parse_request_body_response(r.text)
        log.debug('Obtained token %s.', self._client.token)

        return self.token

    def refresh_token(self, token_url, auth=None, **kwargs):
        """Fetch a new access token using a refresh token.

        :param token_url: The token endpoint, must be HTTPS.
        :param auth: An auth tuple or method as accepted by requests.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not token_url:
            raise ValueError('No token endpoint set for auto_refresh.')

        # Need to nullify token to prevent it from being added to the request
        refresh_token = self.token.get('refresh_token')
        self.token = {}

        body = self._client.prepare_refresh_body(refresh_token=refresh_token, scope=self._client.scope)
        log.debug('Prepared refresh token request body %s', body)

        r = self.post(token_url, data=dict(urldecode(body)), auth=auth, **kwargs)
        log.debug('Request to refresh token completed with status %s.', r.status_code)
        log.debug('Response headers were %s and content %s.', r.headers, r.text)

        self.token = self._client.parse_request_body_response(r.text)
        if 'refresh_token' not in self.token:
            log.debug('No new refresh token given. Re-using old.')
            self.token['refresh_token'] = refresh_token
        return self.token

    def request(self, method, url, data=None, headers=None, **kwargs):
        """Intercept all requests and add token if present.

        When requesting a token for the first time, expect test for token to fail. Simply pass on the request.
        """

        if not is_secure_transport(url):
            raise InsecureTransportError()

        if self.token:
            log.debug('Adding token %s to request.', self.token)
            try:
                url, headers, data = self._client.add_token(url, http_method=method, body=data, headers=headers)

            # Attempt to retrieve and save new access token if expired
            except TokenExpiredError:
                log.debug('Auto refresh is set, attempting to refresh at %s.', self.token_url)
                self.token = self.refresh_token(self.token_url, **kwargs)
                # TODO : callback mechanism so the app can update the token if it's storing it for the user.

        log.debug('Requesting url %s using method %s.', url, method)
        log.debug('Supplying headers %s and data %s', headers, data)
        log.debug('Passing through key word arguments %s.', kwargs)

        return super().request(method, url, headers=headers, data=data, **kwargs)

    def serialize(self):
        """Create a dict that's convenient for web frameworks to save between requests"""
        serializable = dict()
        serializable['client_id'] = self.client_id
        serializable['state'] = self.state
        serializable['token'] = self.token
        serializable['auth_page_location'] = self.auth_page_location
        serializable['services_api_location'] = self.services_api_location
        serializable['token_location'] = self.token_location
        serializable['redirect_url'] = self.redirect_url
        serializable['lexis_config'] = self._config.serialize()
        return serializable

    def __repr__(self):
        """Create a dict that's convenient for web frameworks to save between requests"""
        return str(self.serialize())
