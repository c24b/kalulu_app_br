from .config import config
HOST =  config["FILES_SERVER"]["host"]
LOGIN = config["FILES_SERVER"]["login"]
SRC_DIR = config["FILES_SERVER"]["dir"]
SSH_CMD = "{}@{}:{}".format(LOGIN, HOST, SRC_DIR)

