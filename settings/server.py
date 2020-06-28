#!/usr/bin

import os
from os.path import join as join
from .project import ROOT_DIR


#Virtualenv
try:
    VENV = os.environ["VENV"]
except KeyError:
    VENV = ".venv"

VENV_DIR = join(ROOT_DIR,VENV)
VENV_CMD = join(VENV_DIR, "bin", "python") 