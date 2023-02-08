"""
Flask Application
=================

This is the default entrypoint for our application.
Flask tutorial: https://flask.palletsprojects.com/en/2.2.x/tutorial/

"""

import logging
from os import environ
from typing import Dict, Optional
from datetime import date

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    Response,
    request,
)

from .utils import get_version
from .db import init_db


def create_app(config: Optional[Dict] = None) -> Flask:
    """
    Application factory for creating a new Flask instance.

    :param name: The name of the application.
    """
    flask_app = Flask(__name__, instance_relative_config=True)

    flask_app.config.from_mapping(
        SECRET_KEY='dev',
        BRAND="Good on paper bid",
        NOW=date.today(),
    )

    # load the instance config, if it exists, when not testing
    if config is None:
        flask_app.config.from_pyfile('config.py', silent=True)
    else:
        flask_app.config.from_mapping(config)

    # Initialize logging early, so that we can log the rest of the initialization.
    from .logging import init_logging  # pylint: disable=import-outside-toplevel
    init_logging(flask_app)

    # Set flask config variable for "rich" loggin from environment variable.
    flask_app.config.from_envvar("RICH_LOGGING", silent=True)

    init_logging(flask_app)

    # Init db connection
    init_db(flask_app)

    from .auth import init_auth
    init_auth(flask_app)


    # Register blueprints
    from . import views  # pylint: disable=import-outside-toplevel
    flask_app.register_blueprint(views.bp, url_prefix='')

    return flask_app


# Load environment variables from .env file, if present. See the `dotenv` file for a
# template and how to use it.
load_dotenv()

# Create the Flask application.
app = create_app()

# Initialize "rich" output if enabled. It produces more human readable logs.
# You need to install `flask-rich` to use this.
if app.config.get("RICH_LOGGING"):
    from flask_rich import RichApplication
    RichApplication(app)
    app.logger.info("Using [blue]rich[/blue] interface for logging")


@app.route("/server-info")
def server_info() -> Response:
    """
    A simple endpoint for checking the status of the server.

    This is useful for monitoring the server, and for checking that the server is
    running correctly.
    """

    database_ping: bool = False

    response = {
        "database_connectable": database_ping,
        "version": get_version(),
        "build_date": environ.get("BUILD_DATE", None)
    }

    # Response with pong if ping is provided.
    ping = request.args.get("ping", None)
    if ping is not None:
        response["pong"] = f"{ping}"

    return jsonify(response)
