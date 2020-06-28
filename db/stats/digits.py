#!/usr/bin/python3
# encoding: utf-8

__doc__ = ''' 
Generate digit statistics
'''

from operator import itemgetter
import itertools
import statistics

from utils  import connect, get_color
from utils  import timeit


@timeit
def create_student_identification_table(student=None):
	'''
	CREATE student_identification
	numbers table correspond to specific task on identifying numbers
	corresponds to crabs + jellyfish

	### Methods

	FROM records 
	WHERE dataset='numbers' and game matchs [crabs, jellyfish]
	GROUP BY student, subject, subject
	FILTER timespent != -1
	CREATE timespents [timespent, timespent, ...]
	
	CREATE games unique[game, game, ...] 
	CREATE tags unique [tag, tag, ...]
	SUM score, nb_records
	CALCULATE %CA, color(%CA)
	OUT student_identification

	### Output
	
	```json
	{
	"_id" : ObjectId("5df40a5898f28e7c4f6729ca"),
	"games" : [
		"ants",
		"crabs",
		"jellyfish"
	],
	"classroom": 30,
	"score" : 2589,
	"nb_records" : 2809,
	"student" : 3051,
	"subject" : "numbers",
	"dataset" : "numbers",
	"timespent" : 886.749968,
	"%CA" : 92.17,
	"color" : "green"
	}
	```
	'''
	
	pipeline = [
		{
			"$match": {
				"subject": "numbers",
				"game": {"$in": ["crabs", "jellyfish"]},
				# "group": {"$ne": "guest"}
			}
		},
		{
			"$group": {
				"_id": {
					"student":"$student",
					"subject": "$subject",
					"dataset": "$dataset",
					"classroom": "$classroom"
				},
				"timespent": {
					"$push": {
						"$cond":[
							{"$gt":["$elapsedTime", 0]},
							"$elapsedTime",
							None
						]
					}
				},
				"games": {"$addToSet": "$game"},
				# "tags": {"$addToSet": "$value"},
				"score": {"$sum": "$score"},
				"nb_records": {"$sum": 1},
			}
		},
		{
			"$project": {
				"_id": 0,
				"games": "$games",
				"score": "$score",
				# "tags": "$tags",
				"nb_records": "$nb_records",
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"subject": "$_id.subject",
				"dataset": "$_id.dataset",
				"timespent": {"$sum": "$timespent"},
				"%CA": {"$round":[{"$multiply": [{"$divide": ["$score", "$nb_records"]}, 100]}, 2]}
			}
		},
		{
			"$out": "student_identification"
		}
	]
	if student is not None:
		pipeline[0] = {
			"$match": {
				"subject": "numbers",
				"game": {"$in": ["crabs", "jellyfish"]},
				"student": int(student)
				# "group": {"$ne": "guest"}
			}
		}
		pipeline[-1] = {"$merge": "student_identification"}
	db = connect()
	if student is None:
		db.student_identification.drop()
	db.records.aggregate(pipeline, allowDiskUse=True)
	if student is None:
		for n in db.student_identification.find({}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_identification.update({"_id": n["_id"]}, {"$set": {"color": color}})        
	else:
		for n in db.student_identification.find({"student":int(student)}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_identification.update({"_id": n["_id"]}, {"$set": {"color": color}})
@timeit
def create_student_association_table(student=None):
	'''
	CREATE student_identification
	numbers table correspond to specific task on identifying numbers
	corresponds to ants + turtles
	
	### Methods

	FROM records 
	WHERE dataset='numbers' and game matchs [turtles, ants]
	GROUP BY student, subject, subject
	FILTER timespent != -1
	CREATE timespents [timespent, timespent, ...]
	
	CREATE games unique[game, game, ...] 
	CREATE tags unique [tag, tag, ...]
	SUM score, nb_records
	CALCULATE %CA, color(%CA)
	OUT student_identification

	### Output
	
	```json
	{
	"_id" : ObjectId("5df40a5898f28e7c4f6729ca"),
	"games" : [
		"ants",
		"crabs",
		"jellyfish"
	],
	"classroom": 30,
	"score" : 2589,
	"nb_records" : 2809,
	"student" : 3051,
	"subject" : "numbers",
	"dataset" : "numbers",
	"timespent" : 886.749968,
	"%CA" : 92.17,
	"color" : "green"
	}
	```
	'''
	pipeline = [
		{
			"$match": {
				"subject": "numbers",
				"game": {"$in": ["ants", "turtle"]},
				# "group": {"$ne": "guest"}
			}
		},
		{
			"$group": {
				"_id": {
					"student":"$student",
					"subject": "$subject",
					"dataset": "$dataset",
					"classroom": "$classroom"
				},
				"timespent": {
					"$push": {
						"$cond":[
							{"$gt":["$elapsedTime", 0]},
							"$elapsedTime",
							None
						]
					}
				},
				"games": {"$addToSet": "$game"},
				# "tags": {"$addToSet": "$value"},
				"score": {"$sum": "$score"},
				"nb_records": {"$sum": 1},
			}
		},
		{
			"$project": {
				"_id": 0,
				"games": "$games",
				"score": "$score",
				# "tags": "$tags",
				"nb_records": "$nb_records",
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"subject": "$_id.subject",
				"dataset": "$_id.dataset",
				"timespent": {"$sum": "$timespent"},
				"%CA": {"$round":[{"$multiply": [{"$divide": ["$score", "$nb_records"]}, 100]}, 2]}
			}
		},
		{
			"$out": "student_association"
		}
	]
	db = connect()
	if student is not None:
		pipeline[0] = {
			"$match": {
				"subject": "numbers",
				"game": {"$in": ["ants", "turtle"]},
				"student": int(student)
				# "group": {"$ne": "guest"}
			}
		}
		pipeline[-1] = {"$merge": "student_association"}
	else:
		db.student_association.drop()
	db.records.aggregate(pipeline, allowDiskUse=True)
	if student is None:
		for n in db.student_association.find({}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_association.update({"_id": n["_id"]}, {"$set": {"color": color}})        
	else:
		for n in db.student_association.find({"student":int(student)}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_association.update({"_id": n["_id"]}, {"$set": {"color": color}})
@timeit
def create_student_counting_table(student=None):
	'''
	CREATE student_counting
	numbers table correspond to specific task on counting numbers
	caterpillar
	### Methods

	FROM records 
	WHERE dataset='numbers' and game matchs [caterpillar]
	GROUP BY student, subject, subject
	FILTER timespent != -1
	CREATE timespents [timespent, timespent, ...]
	
	CREATE games unique[game, game, ...] 
	CREATE tags unique [tag, tag, ...]
	SUM score, nb_records
	CALCULATE %CA, color(%CA)
	OUT student_counting

	### Output
	
	```json
	{
	"_id" : ObjectId("5df40a7298f28e7c4f6730ba"),
	"games" : [
		"caterpillar"
	],
	"score" : 2308,
	"nb_records" : 2695,
	"student" : 3284,
	"subject" : "numbers",
	"dataset" : "numbers",
	"timespent" : 2489.583685,
	"%CA" : 85.64,
	"color" : "green"
	}
	```
	'''
	pipeline = [
		{
			"$match": {
				"subject": "numbers",
				"game": {"$in": ["caterpillar"]},
				# "group": {"$ne": "guest"},
			}
		},
		{
			"$group": {
				"_id": {
					"student":"$student",
					"subject": "$subject",
					"dataset": "$dataset",
					"classroom": "$classroom"

				},
				"timespent": {
					"$push": {
						"$cond":[
							{"$gt":["$elapsedTime", 0]},
							"$elapsedTime",
							None
						]
					}
				},
				"games": {"$addToSet": "$game"},
				# "tags": {"$addToSet": "$value"},
				"score": {"$sum": "$score"},
				"nb_records": {"$sum": 1},
			}
		},
		{
			"$project": {
				"_id": 0,
				"games": "$games",
				"score": "$score",
				"nb_records": "$nb_records",
				"student": "$_id.student",
				"subject": "$_id.subject",
				"dataset": "$_id.dataset",
				"classroom": "$_id.classroom",
				"timespent": {"$sum": "$timespent"},
				"%CA": {"$round":[{"$multiply": [{"$divide": ["$score", "$nb_records"]}, 100]}, 2]}
			}
		},
		{
			"$out": "student_counting"
		}
	]
	db = connect()
	if student is None:
		db.student_counting.drop()
	else:
		pipeline[0] = {
			"$match": {
				"student":int(student),
				"subject": "numbers",
				"game": {"$in": ["caterpillar"]},
				# "group": {"$ne": "guest"},
			}
		}
		pipeline[-1] = {
			"$merge": "student_counting"
		}
	db.records.aggregate(pipeline, allowDiskUse=True)
	if student is None:
		for n in db.student_counting.find({}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_counting.update({"_id": n["_id"]}, {"$set": {"color": color}})
	else:
		for n in db.student_counting.find({"student":int(student)}, {"_id":1, "%CA":1}):
			color = get_color(n["%CA"])
			db.student_counting.update({"_id": n["_id"]}, {"$set": {"color": color}})

def create_digits_tables(student=None):
	'''tables for number dashboard'''
	create_student_identification_table(student)
	create_student_counting_table(student)
	create_student_association_table(student)
	return True, ""
	
def delete_digits_tables(student=None):
	db = connect()
	if student is None:
		db.student_counting.drop()
		db.student_association.drop()
		db.student_identification.drop()
		return True, ""
	else:
		student_q = {"student": student}
		db.student_counting.delete_many(student_q)
		db.student_association.delete_many(student_q)
		db.student_identification.delete_many(student_q)
		return True, ""

if __name__=="__main__":
	create_digits_tables()
	# create_digital_decision_tables()
	quit()