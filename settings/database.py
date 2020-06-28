from .config import config

DB_NAME = config["DB"]["name"]
DB_HOST = config["DB"]["host"]
DB_PORT = config["DB"]["port"]
DB_URI =  config["DB"]["URI"]

REF_TABLES = ["datasets", "students", "files", "path"]
INSERT_TABLES = ["records", "games"]

ALL_TABLES = ["day","dataset", "subject", "lesson", "chapter", "tag", "words", "syllabs", "digits", "confusion", "decision"]
REQUIRED_TABLES = ["records", "day", "dataset", "day", "lesson", "records", "records", "records", "records", "chapter", "words"]

TABLES = REF_TABLES + INSERT_TABLES + ALL_TABLES