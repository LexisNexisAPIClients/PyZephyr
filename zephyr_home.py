import logging
import json
import os


from flask import Flask, request, redirect, session, url_for, jsonify
from pyzephyr.session.zephyr_session import ZephyrSession
from pyzephyr.config.config import get_credentials, get_configuration
from pyzephyr.stories import EpicStorybySprint


app = Flask(__name__)

credentials_file = 'client_credentials.json'
credentials_name = 'zephyr2'

config_file = 'var/vsts_config.json'


@app.route('/')
def index():
    """ Create session

    :return:
    """

    zephyr_creds = get_credentials(credentials_file, credentials_name)

    zephyr_endpoint = get_configuration(config_file)

    vsts_session = ZephyrSession(endpoint=zephyr_endpoint, creds=zephyr_creds)

    session['vsts_session'] = vsts_session.serialize()

    return "<h3>Zephyr!</h3>"


@app.route("/dashboard", methods=["GET"])
def dashboard():

    serialized_vsts_session = session['vsts_session']
    vsts_session = ZephyrSession(**serialized_vsts_session)

    query = EpicStorybySprint(epic_path="NL\\NARS Flowpath",
                              story_path="NL\\App Programs",
                              sprint="NL\Sprint 8",
                              session=vsts_session)

    query.refresh()

    session['vsts_session'] = vsts_session.serialize()

    j = query.__str__()
    jl = [v for v in j.values()]
    return jsonify(jl)


def find_oldest_ancestor(story):
    return None

if __name__ == "__main__":

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

    app.run(debug=False, port=4998)
