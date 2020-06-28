#!/usr/bin/python3
# encoding: utf-8

import os
import sys
import subprocess
from datetime import date
import pymongo


from pymongo import MongoClient
from bson.son import SON

from settings import DB_HOST, DB_NAME, DB_PORT

from .files import timeit, convert_jsonl_to_df, convert_df_to_csv


def get_client():
	return MongoClient(DB_HOST, DB_PORT)

def close():
	client = get_client()
	client.close()

def connect(db_name = DB_NAME):
	client = MongoClient()
	db = client[db_name]
	return db

db = connect()
CV = {r["tag"]: r["CV"] for r in db.path.find({"CV": {"$exists": True}})}
lessons_nb = {n["tag"]: n["lesson"]
			  for n in db.path.find({"tag": {"$exists": True}})}
close()
db = connect()
lessons_nb = {n["tag"]: n["lesson"]
		for n in db.path.find({"tag": {"$exists": True}})}

def get_lesson_nb(tag):
	try:
		return lessons_nb[tag]
	except KeyError:
		return None

def get_CV(tag):
	try:
		return CV[tag]
	except KeyError:
		return None

def get_lesson_nb(tag):
	try:
		return lessons_nb[tag]
	except KeyError:
		return None

def get_tag(key, lang=None):
	if lang is None:
		db.path.find_one({"tag":key})
	else:
		db.path.find_one({"tag":key, "lang": lang})

def insert_one(table_name, values):
	db = connect()
	result = db[table_name].insert(values)
	return (True, len(result))


def insert_multi(table_name, values, debug=False):
	db = connect()
	try:
		result = db[table_name].insert_many(values, ordered= False)
		return(True, len(result.inserted_ids))
	except Exception as e:
		print(e)
		return (False, e)

@timeit
def dump_and_drop(archived_dir, db_name=DB_NAME):
	today = date.today()
	d1 = today.strftime("%d-%m-%Y")
	cmd = "mongodump --db {} -o {}/dump-{}".format(db_name, archived_dir, d1)
	print(cmd)
	proc = subprocess.Popen(
		cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = proc.communicate()
	db = connect()
	db.command("dropDatabase")
	# db.drop_database(DB_NAME)

def dump(archived_dir, db_name=DB_NAME):
	today = date.today()
	d1 = today.strftime("%d-%m-%Y")
	cmd = "mongodump --db {} -o {}/dump-{}".format(db_name, archived_dir, d1)
	print(cmd)
	proc = subprocess.Popen(
		cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = proc.communicate()

def get_color(CA):
	if CA >= 75:
		return "green"
	elif CA >= 50:
		return "orange"
	else: 
		return "red"

def check_tables(tables):
	db = connect()

	for table in tables:
		if table not in db.collection_names():
			msg = "Table {} doesn't exists. Aborting executing".format(table)  
			# sys.exit(1)
			return False, msg	
		if db[table].count() == 0:
			msg = "Table {} is empty. Aborting execution".format(table)  
			return False, msg
	return True, ""

def dbtable_to_csvfile(filename="", table_name=""):
	''' if references has been updated in db writ it back to references files'''
	db = connect()
	data = list(db[table_name].find({}, {"_id":0}))
	matrix = convert_jsonl_to_df(data)
	return convert_df_to_csv(matrix)
	
