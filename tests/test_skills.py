import unittest
import pymongo
import requests
import random
from sshtunnel import SSHTunnelForwarder

from settings.database import DB_NAME, DB_HOST, DB_URI
from settings.api import API_URL

# respectively in words, syllabs and digits