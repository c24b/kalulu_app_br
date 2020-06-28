# ENV
import os
from .project import CONF_DIR, ROOT_DIR, API_DIR, VENV_DIR, FRONT_DIR, DOC_DIR
import json
print(ROOT_DIR)
settings_f = "settings.json" 
with open(os.path.join(ROOT_DIR, settings_f)) as settings_file:
    config = json.load(settings_file)
    config["ENVIRONNEMENT"]["dir"] = ROOT_DIR
    config["ENVIRONNEMENT"]["conf"] = CONF_DIR
    config["FRONT"]["dir"] = FRONT_DIR
    config["API"]["dir"] = API_DIR
    config["DOC"]["dir"] = DOC_DIR
    config["VENV_DIR"] = VENV_DIR
    
