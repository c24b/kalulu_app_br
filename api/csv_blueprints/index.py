#/usr/bin/env python3
from flask import Flask, Blueprint, render_template, request
from .activity import csv_activity as a
from .progression import csv_progression as p
from .tasks import csv_tasks as t
from .skills import csv_letters as l 
from .skills import csv_numbers as n
from .admin import csv_admin as m

def get_bp_urls(blueprint):
    temp_app = Flask(__name__) 
    temp_app.register_blueprint(blueprint)
    return [str(p) for p in temp_app.url_map.iter_rules() if not "static" in str(p)]


csv = Blueprint('csv', __name__, url_prefix='/csv', template_folder='../templates')

    
@csv.route("/")
def get():
    root_url = request.base_url.replace("/csv/", "")
    data = {
        "activity": ["{}{}".format(root_url,n) for n  in get_bp_urls(a)],
        "progression": ["{}{}".format(root_url,n) for n  in get_bp_urls(p)],
        "letters": ["{}{}".format(root_url,n) for n  in get_bp_urls(l)],
        "numbers": ["{}{}".format(root_url,n) for n  in get_bp_urls(n)],
        "tasks": ["{}{}".format(root_url,n) for n  in get_bp_urls(t)],
        "admin": ["{}{}".format(root_url,n) for n  in get_bp_urls(m)]
        
        
    }
    return render_template('index.html', data=data)
    # return data