#!/usr/bin/env python3
import os
import json
import time

from flask import Flask,  make_response, request, send_from_directory
from flask_restx import Api, Resource, fields, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

from celery import Celery
from celery.task.control import inspect
from itertools import chain


from settings.api import TESTING, DEBUG
from settings.api import HOST, PORT, DESCRIPTION, TITLE, authorizations

from namespaces import *
from csv_blueprints import *

# APP definition
app = Flask(TITLE, static_folder="site")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app)

#APP configuration
app.config.update(
	HOST=HOST,
	PORT=PORT,
	DEBUG= DEBUG,
	TESTING = TESTING,
	CELERY_BROKER_URL='redis://localhost:6379/0',
	CELERY_RESULT_BACKEND='redis://localhost:6379/0',
)

# Celery Configuration
def make_celery( app ):
	celery = Celery('app', backend=app.config['CELERY_RESULT_BACKEND'],
					broker=app.config['CELERY_BROKER_URL'],
					include=['celery_tasks.app_task'])
	TaskBase = celery.Task
	class ContextTask(TaskBase):
		abstract = True
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return TaskBase.__call__(self, *args, **kwargs)
	celery.Task = ContextTask
	return celery
def list_celery_task( ):
	i = inspect()
	i.registered_tasks()
	try:
		t = set(chain.from_iterable( i.registered_tasks().values() ))
		print("registered_tasks={}".format( t ))
	except AttributeError:
		print("celery not active")


api = Api(app=app,  version='1.1', title=TITLE,
		  description=DESCRIPTION, authorizations=authorizations, validate=True, base_url="/api", catch_all_404s=False)

## JSON namespaces
api.add_namespace(ns_activity)
api.add_namespace(ns_progression)
api.add_namespace(ns_tasks)
api.add_namespace(ns_numbers)
api.add_namespace(ns_letters)

api.add_namespace(ns_admin)

# api.add_namespace(ns_status)


## CSV blueprints

app.register_blueprint(csv_activity)
app.register_blueprint(csv_progression)
app.register_blueprint(csv_tasks)
app.register_blueprint(csv_numbers)
app.register_blueprint(csv_letters)
app.register_blueprint(csv_admin)
app.register_blueprint(csv)

# doc
app.register_blueprint(ns_docs)



celery = make_celery(app)
app.celery = celery
list_celery_task()

if __name__ == "__main__":
#	app.run(host="127.0.0.1", port=5000, debug=True)
 	# app.run(host='0.0.0.0',port=5000, debug=True)
	app.run(host=HOST, port=PORT, debug=True)