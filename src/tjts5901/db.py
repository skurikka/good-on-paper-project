import logging
from os import environ
from flask_mongoengine import MongoEngine

db = MongoEngine()
logger = logging.getLogger(__name__)

def init_db(app) -> None:
    """
    Init the db connection
    """

    mongodb_url = environ.get("MONGO_URL")
    if mongodb_url is not None:
        app.config["MONGODB_SETTINGS"] = {
            "host": mongodb_url,
        }
        logger.info("Database connection string found, using it.",
                    # You can use the `extra` parameter to add extra information to the log message.
                    # This is useful for debugging, but should be removed in production.
                    extra={"MONGO_URL": mongodb_url} if app.debug else {})

    else:
        logger.warning("No database connection string found in env, using defaults.",
                       extra={"MONGODB_SETTINGS": app.config.get("MONGODB_SETTINGS")} if app.debug else {})

    
    db.init_app(app)
