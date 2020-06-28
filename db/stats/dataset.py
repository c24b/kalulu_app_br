#!/usr/bin/python3
# encoding: utf-8
__doc__ = "Compute records by student by dataset to get timespent and nb_records"

from utils import connect, SON
from utils import timeit, convert_iso_to_dhms
# from .day import create_day_tables

@timeit
def create_student_dataset(student=None):
	'''
	FROM student_day
	SORT by student, dataset, start
    Group by student and by dataset: 
		- days, sequences, first(start), last(end)
		- calculate nb_records, nb_days, nb_sequences, timespent(in sec.) 
	    - push records
	OUT into student_dataset 
	
	## Output
	{
		
		"student" : 111,
		"classroom" : 1,
		"group" : "r/m",
		"dataset" : "assessments_language",
		"subject" : "letters",
		"nb_records" : 536,
		"start" : ISODate("2018-11-13T09:41:27Z"),
		"end" : ISODate("2019-02-04T09:02:55Z"),
		"timespent" : 1291,
		"days": [],
		"nb_days" : 8,
		"nb_sequences" : 20
		"records": [ ...,]
	}

	'''
	db = connect()
	if student is None:
		db.student_dataset.drop_indexes()
	# print("Create student_dataset")
		db.student_dataset.drop()
	else:
		db.student_dataset.drop_indexes()
		db.student_dataset.delete_many({"student":student})
	# db.student_dataset.create_index([('student', pymongo.ASCENDING), ('dataset', pymongo.ASCENDING)], unique=True)
	# print("\t\t - Create table student_dataset")
	pipeline = [
		# {
		# 	"$in": "student_day"	
		# },
		# {
		# 	"$match": {
		# 		"group": {"$ne": "guest"},
		# 	},
		{
			#important to sort by start before to get start and end correct
			"$sort": SON([("student", 1), ("dataset", 1),("start", 1), ("end",1)])
		},
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"dataset": "$dataset",
					"subject": "$subject",
				},
				
				"days": {"$addToSet":"$day"},
				"sequences": {"$push": "$sequences"},
				"nb_sequences": {"$sum": "$nb_sequences"},
    			"start": {"$first": "$start"},
				"end": {"$last": "$end"},
				"nb_records": {"$sum": "$nb_records"},
				#timespent consists of the sum of timespent over days
				"timespent": {"$sum": "$timespent"},
				"records": {"$push": "$records"},
   			}
		},
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"group": "$_id.group",
				"dataset": "$_id.dataset",
				"subject": "$_id.subject",
				"nb_records": "$nb_records",
				"start": "$start",
				"end": "$end",
				"timespent": "$timespent",
				"days": "$days",
				"end_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$end",  "timezone": "Europe/Paris"} },
				"start_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$start",  "timezone": "Europe/Paris"} },
				"timespent_sec": "$timespent",
				"timespent_min": {"$divide": ["$timespent", 60]},
				"nb_days": {"$size":"$days"},
				"nb_sequences": "$nb_sequences",
				"sequences": {"$reduce": {
						"input": "$sequences",
						"initialValue": [],
					  		"in": {"$concatArrays": ["$$this", "$$value"]}
					}},
				"records": {"$reduce": {
						"input": "$records",
						"initialValue": [],
					  		"in": {"$concatArrays": ["$$this", "$$value"]}
					}},
			}
		},
		{
			"$out": "student_dataset"
		},
	]
	
	# if "student_dataset_day" not in db.list_collection_names():
	# 	create_day_tables(student)
	if student is not None:
		pipeline.insert(0,{"$match": {"student": int(student)}})
		pipeline[-1] = {"$merge": "student_dataset"}
		
	db.student_day.aggregate(pipeline, allowDiskUse=True)
	# print("\t\t> Table student_dataset is ready!")


def delete_dataset_tables(student=None):
	db = connect()
	db.student_dataset.drop_indexes()
	if student is None:
		db.student_dataset.drop()
	else:
		db.student_dataset.delete_many({"student":student})
	return True, ""

def create_dataset_tables(student=None):
	create_student_dataset(student)
	return True, ""

if __name__=="__main__":
	create_dataset_tables()
	quit()