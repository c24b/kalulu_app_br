#!/usr/bin/env python3
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import argparse


from settings import ROOT_DIR, RAW_DIR, CLEAN_DIR, ARCHIVED_DIR, LOG_DIR, REFERENCES_DIR, DIRS
from settings import STEPS, STATS
from settings import config

from utils import timeit, dir_empty, dir_exists
from db import create_step, create_steps
# from steps import create_step
# from steps import create_steps

from db import stats, stat 
from db import tables, table

if not dir_exists(LOG_DIR):
	os.makedirs(LOG_DIR)

### PARSE CMD ARGS
parser = argparse.ArgumentParser()
parser.add_argument("--from", help="Source folder", action="store_true", default=RAW_DIR)
parser.add_argument(
	"--to", help="Target dir", action="store_true", default=CLEAN_DIR)
parser.add_argument("--old", help="Archived folder", action="store_true", default=ARCHIVED_DIR)
parser.add_argument("--ref", help="References folder", action="store_true", default=REFERENCES_DIR)
parser.add_argument("--steps", help="Execute the steps: init, insert", action="store_true")
parser.add_argument("--stats", help="Execute the stats: create, delete OR update", default=None)
parser.add_argument("--tables", help="Tables: create, delete OR update stats", default=None)

parser.add_argument("--step", help="STEP: specify the step='download,clean,init,insert'")
parser.add_argument("--stat", help="STAT: specify the stat category to execute")
parser.add_argument("--table", help="TABLE: specify the table you want to rebuild")
parser.add_argument("--download", help="Download the files from document server: check settings", action="store_true")
parser.add_argument("--student", help="Execute for one student specifying his <id>", default=None)
# parser.add_argument("--classroom", help="Execute for one classroom specifying his <id>", default=None)
### LOGGER
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'run.log'), 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# show in cmd
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

@timeit
def cmd(args):
	'''
	Main function in shell to launch process:
	if --download: take the config settings: execute [download, clean, init, insert, stats]
	if no arguments: execute [init, insert, stats]   
	''' 
	### STEPS/STEP: init and populate db
	
	logger.info(args)
	status = True
	msg = ""
	## STEPS is True: create the steps: [init, insert]
	if args.steps is True:
		logger.info("STEPS option is activated: execute only the steps")
		## STEPS is True and download is False: create the steps: [init, insert]
		## from files/clean
		if args.download is not False:
			logger.info("with --download")
			# logger.info("- arguments {}".format(args))
			logger.info("create_steps(): download, clean, init, insert") 
			status, msg = create_steps()
			return status, msg
		else:
			logger.info("create_steps(): init, insert")
			logger.info("create_steps(): init from files in {}, insert from files in {}".format(args.dirs["ref"], args.dirs["to"]))
			logger.info("remove download and clean")
			steps = STEPS
			# removed_steps = ["download"]
			removed_steps = ["download", "clean"]
			for del_s in removed_steps:
				steps.remove(del_s)
			for step in steps:
				status, msg = create_step(step)
				if status is False:
					logger.critical("STEP {}() is {}. {}".format(step,status, msg))
					break
			return status, msg
	# STEP: specify the step between 'download,clean,init,insert' accept multiple steps coma separated
	elif args.step is not None:
		logger.info("STEP option is activated: execute only the steps mentionned")
		for step in args.step.split(","):
			logger.info("STEP {}()".format(args.step))
			status, msg = create_step(step.strip())
			if status is False:
				logger.critical("STEP {}() is {}. {}".format(step,status, msg))
				break
		return status, msg

	### STATS : generate stats
	elif args.stats in ["create", "delete", "update"]:
		logger.info("STATS option is activated: only {} all stats".format(args.stats))
		logger.info("STATS stats({},{})".format(args.stats, args.student))
		if args.stats == "create":
			status, msg = stats(args.stats, args.student)
		elif args.stats == "delete":
			status, msg = stats(args.stats, args.student)
		else:
			#update
			stats("delete", args.student)
			status, msg = stats("create", args.student)
		return status, msg
	# STAT: specify the stat between 'activity, tasks, skills, progression' multiple stats accepted coma separated
	elif args.stat is not None:
		logger.info("STAT option is activated. Only create specified stats {}".format(args.stats))
		for stat_name in args.stat.split(","):
			logger.info("STAT {}({})".format(stat_name.strip(), args.student))
			stat(stat_name, action="create", student=args.student)
		return status, msg
	### TABLES: generate TABLES for STATS create delete or update   
	elif args.tables in ["create", "delete", "update"]:
		logger.info("TABLES option is activated. {} all the tables".format(args.tables))
		status, msg = tables(action=args.tables, student=args.student)
		return status, msg
	#TABLE specify the table between 'day,chapter,lesson,...', multiple tables accepteds  coma sperated   
	elif args.table is not None:
		logger.info("TABLE option is activated. Create only the table: {}".format(args.table))
		table_names = args.table.split(",")
		for tablename in table_names:
			logger.info("TABLE({},{}) option is activated".format(tablename.strip(), args.student))
			status, msg = table(tablename, action="create", student=args.student, required_table=None)
		return status, msg
		
	### COMPLETE SCRIPT
	elif args.download is not False:
		logger.info("Complete execution with download: download, clean, init, insert, stats")
		create_steps()
		status, msg = stats("create", args.student)
		return satus, msg
	else:
		steps = STEPS
		logger.info("No arguments in cmd: falling back to settinngs.json")
		if config["FILES_SERVER"]["activate"] is False:
			# raw directory provided by user 

			raw_data_dir = config["FILES_SERVER"]["dir"]
				
			# if raw_directory provided by user doesn't exists
			if not dir_exists(raw_data_dir) or dir_empty(raw_data_dir):
				# fall back to default CLEAN_DIR
				if not dir_exists(CLEAN_DIR) or dir_empty(CLEAN_DIR):
					# trying to get default RAW_DIR
					if not dir_exists(RAW_DIR) or dir_empty(RAW_DIR):
						msg = "No download option activated and no data found in both provided dir: {} and RAW dir: {}".format(raw_data_dir, RAW_DIR)
						logger.critical(msg)
						return False, msg
					else:
						steps.remove("download")
				else:
					steps.remove("download")
					steps.remove("clean")
			else:
				RAW_DIR = raw_data_dir
				steps.remove("download")
				if not dir_exists(CLEAN_DIR):
					os.makedirs(CLEAN_DIR)
		logger.info("Execute: {}".format(", ".join(steps))) 
		create_steps(steps)
		status, msg = stats("create", args.student)
		return status, msg
		



if __name__ == "__main__":
	# steps = ["download", "clean", "init", "insert", "stats"]
	# logger.info('### RUN')
	# logger.debug("Script Arguments: {}".format(args.__dict__))
	cmd(parser.parse_args())
	quit()