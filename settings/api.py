#!/usr/bin/env python
from .config import config


if config["SSL"]["activate"]:
    API_URL = "https://"+config["API"]["hostname"]
else:
    if config["ENVIRONNEMENT"]["ENV"] in ["test","testing", "local"]:
        API_URL = "http://"+config["API"]["host"]
    else:
        API_URL = "http://"+config["API"]["hostname"]

PORT = config["API"]["port"]
HOST = config["API"]["host"]

TITLE ="Kalulu API"
DESCRIPTION = "View records, stats and metrics of 'Kalulu' Game App"

TOKEN = config["API"]["token"]
SUDO_TOKEN = config["API"]["sudo_token"]

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

STATIC_DIR="static"
TEMPLATE_DIR="templates"
RESTPLUS_VALIDATE=True
DEBUG = True
TESTING = True
