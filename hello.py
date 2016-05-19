import logging
import os

from flask import Flask, request, redirect, session, url_for
from pyzephyr.session.vsts_session import VSTSSession
from pyzephyr.config.config import get_credentials, get_lexis_config


app = Flask(__name__)

credentials_file = 'client_credentials.json'
credentials_name = 'kellykx'

config_file = 'var/lexis_config.json'

redirect_url = 'http://127.0.0.1:4999/callback'

auth_page_location = 'auth'
token_location = 'auth'


@app.route('/')
def hello():
    """ Create session to get and manage tokens.

    :return: redirect user-agent to VSTS authorization page
    """

    client_id, secret = get_credentials(credentials_file, credentials_name)
    lexis_config = get_lexis_config(config_file)

    vsts_session = VSTSSession(lexis_config=lexis_config, client_id=client_id, redirect_url=redirect_url)

    vsts_session.auth_page_location = auth_page_location
    vsts_session.token_location = token_location

    session['vsts_session'] = vsts_session.serialize()

    return redirect(vsts_session.decorated_auth_url)


@app.route("/callback", methods=["GET"])
def callback():
    """ Retrieve an access token.

    User has been redirected from the provider to this registered callback URL.

    This redirection comes with an authorization code included on the redirect URL.
    Extract it and use it to fetch an access token.

    Client secret from credentials is required, along with the authorization code, to get a token.
    """

    serialized_vsts_session = session['vsts_session']
    vsts_session = VSTSSession(**serialized_vsts_session)

    token_endpoint = vsts_session.token_url

    credentials = get_credentials(credentials_file, credentials_name)

    vsts_session.fetch_token(token_endpoint, request.url, credentials)

    session['vsts_session'] = vsts_session.serialize()

    return redirect(url_for('.dashboard'))


@app.route("/dashboard", methods=["GET"])
def dashboard():

    serialized_vsts_session = session['vsts_session']
    vsts_session = VSTSSession(**serialized_vsts_session)

    session['vsts_session'] = vsts_session.serialize()

    return  # a page


@app.route("/flowpath", methods=["GET"])
def sources():

    serialized_vsts_session = session['vsts_session']
    vsts_session = VSTSSession(**serialized_vsts_session)

    session['vsts_session'] = vsts_session.serialize()

    return  # a page


if __name__ == "__main__":
    os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', 'True')
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)

    logging.basicConfig(
        filename='var/pyzephyr.log',
        level=logging.DEBUG,
        format='%(asctime)s  %(process)-7s %(name)-20s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    )
    log = logging.getLogger("pyzephyr")
    log.addHandler(logging.NullHandler())
    log.info('###### Starting PyZephyr App #####')

    app.run(debug=False, port=4999)
