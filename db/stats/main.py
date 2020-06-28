#!/usr/bin/env python3

__doc__='''
stats.main provide the facilities for generating tables of analysis and visualization
'''

import os
import sys
import importlib


# from concurrent.futures import ThreadPoolExecutor
# executor = ThreadPoolExecutor(5)

# LOGS
import logging
from logging.handlers import RotatingFileHandler
from settings import LOG_DIR

# DB UTILS
from utils import check_tables
from utils import timeit
from utils import connect

#stats: tables and shorcut stats
from settings import STATS, TABLES, REQUIRED_TABLES
from settings.database import ALL_TABLES, REQUIRED_TABLES

# activity
from .day import create_day_tables, delete_day_tables
from .dataset import create_dataset_tables, delete_dataset_tables
from .subject import create_subject_tables, delete_subject_tables

# progression
from .lesson import create_lesson_tables, delete_lesson_tables
from .chapter import create_chapter_tables, delete_chapter_tables

# tasks
from .confusion import create_confusion_tables, delete_confusion_tables
from .decision import create_decision_tables, delete_decision_tables

#skills

from .digits import create_digits_tables, delete_digits_tables
from .tag import create_tag_tables, delete_tag_tables
from .words import create_words_tables, delete_words_tables
from .syllabs import create_syllabs_tables, delete_syllabs_tables


def activity():
	required_tables = ["records", "day", "dataset"]
	tables = ["day", "dataset", "subject"]
	return zip(tables, required_tables)

def skills():
	required_tables= ["records", "records", "records", "records"]
	tables = ["digits", "tag", "words", "syllabs"]
	return zip(tables, required_tables)

def progression():
	required_tables = ["day", "lesson"]
	#required_table_name
	tables = ["lesson", "chapter"]
	return zip(tables, required_tables)

def tasks():
	required_tables = ["records", "chapter"]
	tables = ["decision", "confusion"]
	return zip(tables, required_tables)

# # STATS shortcuts
# def activity(action="create", student=None):
#     '''
#     Activity regroups tables ["day", "dataset", "subject"]
#     that need to be processed in this order
#     each table is stored in .<table>.py file and expose 2 methods
#     create_<table>_tables.py
#     delete_<table>_tables.py
#     day table is required to build dataset and subject is
#     '''
#     required_tables = ["records", "day", "dataset"]
#     tables = ["day", "dataset", "subject"]
#     for req_table, table_name in zip(required_tables, tables):
#         try:
#             table(table_name, action, student, required_table=req_table)
#             # file_func = "{}_{}_tables".format(action,table)
#             # print(file_func)
#             # spec = importlib.import_module(table, file_func)
#             # print(spec)
#             # spec_file = spec.loader.load_module()
#             # print(spec_file)
#             # func = getattr(sys.modules[__name__], spec_file)
#             # print(func)
#             # func(student)
			
#         except Exception as e:
#             logger.critical("STATS - Activity - Error generating tables {}: {}".format(table, e))
			
#     return 

# def progression(action="create", student=None):
#     '''
#     Progression regroups the tables corresponding to progression of the children
#     lesson
#     chapter
#     calling the function <action>_<table_name>
#     both requiring the day table
#     '''
#     required_tables = ["day", "lesson"]
#     #required_table_name
#     tables = ["lesson", "chapter"]
#     for table_name, req_table in zip(tables, required_tables):
#         try:
#             table(table_name, action, student, required_table=req_table)
#             # func_name = "{}_{}_tables".format(action, table)
#             # spec = importlib.import_module(table, func_name)
#             # spec_file = spec.loader.load_module()
#             # func = getattr(sys.modules[__name__], spec_file)
#             # func(student)
#         except Exception as e:
#             logger.warning("STATS - Progression - Error generating tables {}: {}".format(table, e))
#     return 

# def tasks(action="create",student=None):
#     '''
#     regroups the two analyis decision and confusion
#     requires respectively: tag and chapter
#     '''
#     required_tables = ['tag', "chapter"]
#     #["student_tag", ("student_chapter", "student_chapters")]
#     tables = ["decision", "confusion"]
#     for table_name, req_table in zip(tables, required_tables):
#         try:
#             table(table_name, action, student, required_table=req_table)
#             # func = "{}_{}_tables".format(action,table)
			
#             # spec = importlib.import_module(table, func)
#             # spec_file = spec.loader.load_module()
#             # func = getattr(sys.modules[__name__], spec_file)
#             # func(student)
#         except Exception as e:
#             logger.warning("STATS - Tasks - Error generating tables {}: {}".format(table, e))
#     return

# def skills(action="create",student=None):
#     '''
#     skills regroups tables : digits, tags, words, syllabs
#     '''
#     required_tables= ["records", "records", "records", "records"]
#     tables = ["digits", "tag", "words", "syllabs"]
#     for table_name, req_table in zip(tables, required_tables):
#         try:
#             table(table_name, action, student, required_table=req_table)
#             # func = "{}_{}_tables".format(action,table)
#             # spec = importlib.import_module(table, func)
#             # spec_file = spec.loader.load_module()
#             # func = getattr(sys.modules[__name__], spec_file)
			
#             # func(student)
#         except Exception as e:
#             logger.critical("STATS - Skills - Error generating tables {}: {}".format(table, e))
#     return

def stats(action=None, student=None):
	'''
	STATS consists of a list of shorcuts that groups tables into categories
	to preserve the order of execution and dependencies between the tables creation
	defined in settings.database.STATS
	STATS = ["activity", "progression", "tasks", "skills"]
	corresponds to 
	[
		("day","dataset", "subject"), 
		("lesson", "chapter"), 
		("tag", "words", "syllabs", "digits") 
		("confusion", "decision")
	]
	EACH TABLE has a required table
	[
		("records", "day", "dataset"),
		("records", "lesson"),
		("records", "tags", "tags", "records")
		("chapter", "words")
	]
	'''
	# LOGGING
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR,'stats.log'), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	if action in ["update", "create"]:
		db = connect()
		if db.records.count() == 0:
			msg = "Unable to update or create. No records in database. Aborting"    
			return False, msg
		status = True
		if action is None:
			action = "create"
		logger.info("stats(action={},student={})".format(action, student))
	status = True
	for stat_name in ["activity", "progression", "skills", "tasks"]:
		try:
			func = getattr(sys.modules[__name__], stat_name)
			logger.info("{}()".format(stat_name))
			stat = func()
			for table_name, req in list(stat):
				status, msg = table(table_name, action, student, req)
				# if status is False:
				#     break
			# executor.submit(func(action, student))
		except Exception as e:
			msg = "stats() executing table stat called {}() Error:{}".format(stat_name, e)
			logger.warning("{}( action={}, student={}), Error: {}".format(stat_name, action, student, e))
			status = False
	return status, msg

def stat(stat_name, action=None, student=None):
	# LOGGING
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR,'table.{}.log'.format(stat_name)), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	status = True
	msg = ""
	if action is None:
		action ="create"
	if stat_name not in ["activity", "progression", "skills", "tasks"]:
		msg = "stat({}, action={}, student={}) stat {} doesn't exist in STATS".format(stat_name, action, student, stat_name)
		# logger.warning(msg)
		return False, msg
	try:
		func = getattr(sys.modules[__name__], stat_name)
		logger.info("{}()".format(stat_name))
		stat = func()
		for table_name, req in list(stat):
			status, msg = table(table_name, action, student, req)
			# if status is False:
			#     break
		# executor.submit(func(action, student))
	except Exception as e:
		msg = "stats() executing table stat called {}() Error:{}".format(stat_name, e)
		logger.warning("{}( action={}, student={}), Error: {}".format(stat_name, action, student, e))
		status = False
	return status, msg
	# try:
	#     func = getattr(sys.modules[__name__], stat_name)
	#     logger.info("{}(action={}, student={})".format(stat_name, action, student))
	#     return func(action,student)
	# except Exception as e:
	#     msg = "stat({}, action={}, student={}) stat {} Exception {}".format(stat_name, action, student, stat_name, e)
	#     logger.warning(msg)
	#     return False, msg

# TABLES functions
# function <create|delete>_<table_name>_tables()
# dynamically loaded from table file stored in db/stats/<table_name> 
def table(table_name, action, student, required_table=None):
	'''
	TABLE <table_name>, <action>, <student>
	2 functions dynamically loaded from table file stored in db/stats/<table_name>
	depending on the <action>: create, delete, update
	- <action>_<table_name>_tables(student)
	- check for required_table
	'''
	status = True
	msg = ""
	# LOGGING
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR,'table.{}.log'.format(table_name)), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	# print("TABLE: ", table_name, action, student, required_table)
	# print(table_name, action, student, required_table)
	# print(ALL_TABLES)
	#dependency check
	if required_table is None:
		for tbl,req in zip(ALL_TABLES, REQUIRED_TABLES):
			if tbl == table_name:
				# print("table {} requires {}".format(tbl, req))
				required_table = req
	if table_name not in ALL_TABLES:
		msg = "table({}, action={}, student={}) stat {} doesn't exist in STATS".format(table_name, action, student, table_name)
		logger.warning(msg)
		return False, msg
	if required_table not in REQUIRED_TABLES:
		msg = "required table({}, action={}, student={}) table required {} doesn't exist in STATS".format(required_table, action, student, required_table)
		logger.warning(msg)
		return False, msg    
	elif action not in ["create", "delete", "update"]:
		msg = "required table({}, action={}, student={}) action {} not supported".format(table_name, action, student, action)
		logger.warning(msg)
		return False, msg 
	else:
		try:
			#check required tables
			if action in ["create", "update"]:
				db = connect()
				file_func = "table"
				if "student_"+required_table not in db.list_collection_names():
					
					if required_table != "records":
						file_func = "table"
						table(required_table, action, student, None)
				elif student is None:
					if db["student_"+required_table].count() == 0:
						if required_table != "records":
							file_func = "table"
							table(required_table, action, student, None)
				elif student is not None:
					if db["student_"+required_table].count({"student":student}) == 0:
						if required_table != "records":
							file_func = "table"
							table(required_table, action, student, None)
				else:
					pass
			if action == "update":
				file_func = "delete_{}_tables".format(table_name)
				func = getattr(sys.modules[__name__], file_func)
				func(student, None)				
				file_func = "create_{}_tables".format(table_name)
				func = getattr(sys.modules[__name__], file_func)
				return func(student, None)
			
			file_func = "{}_{}_tables".format( action, table_name)
			func = getattr(sys.modules[__name__], file_func)
			func(student)
			
		except Exception as e:
			msg = "table({}, action={}, student={}) => {}() raised an exception. Exception: {}".format(table_name, action, student, file_func, e)
			logger.warning(msg)
			return False, msg
	return status, msg

def tables(action, student=None):
	'''TABLES function to create, delete OR update
	the table in order of declaration in settings.TABLES
	'''
	# LOGGING
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR,'tables.log'), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	msg = ""
	if action in ["create", "update"]:
		db = connect()
		if db.records.count() == 0:
			msg = "No records in database. Aborting"
			logger.critical("No records in database. Aborting")
			return False, msg
	logger.info("stats.main.tables(action={}, student={})".format(action,student))
	if action == "update":
		for table_name in STATS_TABLES:
			table(table_name, "delete",student)
		for table_name, req in zip(STATS_TABLES, REQUIRED_TABLES):
			table(table_name,"create", student, req)
	else:
		for table_name, req in zip(STATS_TABLES, REQUIRED_TABLES):
			table(table_name, action, student, req)
	return True, msg
