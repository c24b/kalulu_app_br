import os
import sys
from settings import STEPS, LOG_DIR, DIRS
import logging
from utils.db import connect
from logging.handlers import RotatingFileHandler
from utils import check_dirs, connect
from .init import init
from .download import download
from .clean import clean
from .insert import insert

def create_steps(steps=STEPS, default_directories=DIRS):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'steps.log'), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	# stream_handler = logging.StreamHandler()
	# stream_handler.setLevel(logging.DEBUG)
	# logger.addHandler(stream_handler)
	status, msg = check_dirs(default_directories, ["ref"]) 
	statuses, msgs = [], []
	if status is False:
		return status, msg
	else:
		# logger.info("STEPS - Executing steps: {}.".format(steps))
		for s in steps:
			f = s
			f = getattr(sys.modules[__name__], s)
			try:
				logger.info("STEPS - Executing {}()".format(s))
				f(default_directories)
				# print(s, status, msg)
			except Exception as e:
				logger.critical("STEPS - {}(). Exception: {}".format(s, e))
		return all(statuses), ",".join(msgs)

def create_step(step, default_directories=DIRS):
	status,msg = True, ""
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'step.{}.log'.format(step)), 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	# stream_handler = logging.StreamHandler()
	# stream_handler.setLevel(logging.DEBUG)
	# logger.addHandler(stream_handler)
	if step not in STEPS:
		msg = "STEP - step {}() doesn't exists. Abort execution".format(step)
		# logger.critical(msg)
		return False, msg
	try:
		status, msg = check_dirs(default_directories)
	except:
		status, msg = check_dirs(DIRS)
	if status is False:
		return status, msg
	else:
		f = getattr(sys.modules[__name__], step)
		try:
			logger.info("STEPS - Execute {}()".format(step))
			try:
				f(default_directories)
			except:
				f(DIRS)
			return status,msg    
		except Exception as e:
			logger.critical("STEPS - Execute {}() : Error : {}".format(step,e))
			return False, e
	return True, ""