import os
from os.path import dirname, abspath, join

# PROJECT
ROOT_DIR = dirname(dirname(abspath(__file__)))

# VENV
VENV_DIR = join(dirname(dirname(abspath(__file__))), '.venv')

# API
API_DIR = join(ROOT_DIR, "api")
NAMESPACE_DIR = join(ROOT_DIR, "namespaces")
CSV_DIR = join(ROOT_DIR, "csv_blueprint")

# BACK
DB_DIR = join(ROOT_DIR, "db")
STEPS_DIR = os.path.join(DB_DIR,"steps")
STATS_DIR = os.path.join(DB_DIR,"stats")

# FRONT
FRONT_DIR = join(ROOT_DIR, "front")

# DOC
DOC_DIR = join(ROOT_DIR, "site")

# ADMIN DIRECTORIES
SETTINGS_DIR = join(ROOT_DIR, "settings")
LOG_DIR = join(ROOT_DIR, "logs")
TEST_DIR = join(ROOT_DIR, "tests")
DOCS_DIR = join(ROOT_DIR, "docs")
CONF_DIR = join(ROOT_DIR, "conf")


# SCRIPTS
STEPS = ["download", "clean", "init", "insert"]
# execute the stats table creation in this order
STATS = ["activity", "progression", "skills", "tasks"]
