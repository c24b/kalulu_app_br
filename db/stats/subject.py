
#!/usr/bin/python3
# encoding: utf-8
__doc__ = "Compute records by student and by subject"

from utils import connect, SON, pymongo
from utils import timeit
#from .dataset import create_dataset_tables

@timeit
def create_student_subject(student=None):
	"""
	FROM student_dataset
	GROUP BY classroom, student, subject
	INSERT first(start), last(end), datasets(list)
	SUM nb_sequences, nb_days, nb_records, timespent (in sec)
	INSERT records(list) datasets(list)
	OUT student_subject

	### OUTPUT
	{

		"student" : 111,
		"classroom" : 1,
		"group" : "r/m",
		"datasets" : [
			"assessments_language",
			"gapfill_lang",
			"gp"
		],
		"subject" : "letters",
		"nb_records" : 6118,
		"start" : ISODate("2018-11-13T09:41:27Z"),
		"end" : ISODate("2019-02-08T11:05:48Z"),
		"timespent" : 46878,
		"nb_days" : 0,
		"nb_sequences" : 65
		"records": [...]
	}

	"""
	pipeline = [
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"subject": "$subject",
				},
				"start": {"$first": "$start"},
				"end": {"$last": "$end"},
				"datasets": {"$push":"$dataset"},
				"nb_sequences": {"$sum": "$nb_sequences"},
				"days": {"$addToSet": "$days"},
				"nb_records": {"$sum": "$nb_records"},
				"timespent_by_dataset": {"$push": "$timespent"},
				"timespent": {"$sum":"$timespent"},
				"records": {"$push": "$records"},
			}
		},
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"group": "$_id.group",
				"datasets": "$datasets",
				"subject": "$_id.subject",
				"nb_records": "$nb_records",
				# "CA": "$CA",
				"start": "$start",
				"end": "$end",
				"end_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$end",  "timezone": "Europe/Paris"} },
				"start_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$start",  "timezone": "Europe/Paris"} },
				"timespent": "$timespent",
				"timespent_by_dataset": "$timespent_by_dataset",
				"timespent_sec": "$timespent",
				"timespent_min": {"$divide": ["$timespent", 60]},
				"datasets": "$datasets",
				"days": {"$reduce": {
						"input": "$days",
						"initialValue": [],
					  		"in": {"$setUnion": ["$$this", "$$value"]}
					}},
				
				"nb_sequences": "$nb_sequences",
				"records": {"$reduce": {
						"input": "$records",
						"initialValue": [],
							"in": {"$concatArrays": ["$$this", "$$value"]}
					}},
				
			}
		},
		{
			"$addFields": {"nb_days": {"$size": "$days"}}
		},
		{
			"$out": "student_subject"
		},
	]
	db = connect()
	if student is None:
		db.student_subject.drop_indexes()
		db.student_subject.drop()
		# if "student_dataset" not in db.list_collection_names():
		# 	create_dataset_tables(student)
		try:
			db.student_dataset.aggregate(pipeline, allowDiskUse=True)
		except pymongo.errors.DuplicateKeyError:
			pass
		
	else:
		# if student_dataset.find_one({"student":student}) is None:
		# 	create_dataset_tables(student)
		# if student_dataset.find_one({"student":student}) is not None:
		# 	db.student_subject.remove({"student": student})
		pipeline.insert(0,{"$match": {"student": str(student)}})
		pipeline[-1] = {"$merge": "student_subject"}
		# print(pipeline)
		try:
			db.student_dataset.aggregate(pipeline, allowDiskUse=True)
		except pymongo.errors.DuplicateKeyError:
			print("Duplicate")
			pass
	
@timeit
def delete_subject_tables(student=None):
	db = connect()
	if student is None:
		db.student_subject.drop_indexes()
		db.student_subject.drop()
	else:
		db.student_subject.delete_many({"student":str(student)})
	return True, ""	
@timeit
def create_subject_tables(student=None):
	create_student_subject(student=None)
	return True, ""

if __name__=="__main__":
	create_subject_tables()
	quit()