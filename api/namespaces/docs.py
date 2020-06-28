from flask import Blueprint, render_template, abort
import os
import subprocess
from flask import current_app,send_from_directory
from flask import Blueprint, render_template, abort
from utils.db import connect
from utils.files import convert_raw_data

ns_docs = Blueprint('docs', __name__, url_prefix='/docs')

@ns_docs.route('<path:path>')
def send_docs(path):
    return send_from_directory('site', path)

@ns_docs.route('/')
def send_doc_index():
    return send_from_directory('site', 'index.html')
