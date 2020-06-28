#!/usr/bin/python3
# encoding: utf-8
__doc__ = "Compute records by student by day and by dataset"

from utils import timeit, connect, pymongo, SON

@timeit
def create_student_nb_gapfill_gp_day(student=None):
	'''
	From RECORDS WHERE dataset in ["numbers", "gp", "gapfill_lang"]
	Group (student if student.group != "guest records by dataset and by day
	sort records by student, dataset and unixtime
	get FIRST unixTime LAST unixTime
	create sequence and sequence_nb
	compute timespent (LAST-FIRST) into seconds
	MERGE into student_day
	'''

	db = connect()
	db.student_day.drop_indexes()
	db.student_day.create_index([('student', pymongo.ASCENDING), (
			'day', pymongo.ASCENDING), ('subject', pymongo.ASCENDING), ('dataset', pymongo.ASCENDING)], unique=True)
	if student is None:
		db.student_day.drop()
		
		# print("\t\t - Create table student_dataset_day for gp, nb and gapfill_lang")
	pipeline = [
		# {
		# 	"$in":"records"
		# },
		{
			"$match": {
				"group": {"$ne": "guest"},
				"dataset": {"$in": ["numbers", "gp", "gapfill_lang"]}
			},
		},
		{
			"$sort": SON([("student", 1), ("unixTime", 1)])
		},
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"dataset": "$dataset",
					"day": "$day",
					"subject": "$subject",
				},
				"nb_sequences": {"$sum":1},
				"start": {"$first": "$unixTime"},
				"end": {"$last": "$unixTime"},
				"nb_records": {"$sum": 1},
				"records": {"$push": "$$ROOT"},
				
			}
		},
		{
			"$addFields":{
				"nb_sequences": 1
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
				"day": "$_id.day",
				"nb_records": "$nb_records",
				"start": "$start",
				"end": "$end",
				#sequence of plays within a day
				"sequences" : [["$start", "$end"]],
				"nb_sequences": "$nb_sequences",
				"start": "$start",
				"end": "$end",
				"end_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$end",  "timezone": "Europe/Paris"} },
				"start_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$start",  "timezone": "Europe/Paris"} },
				"timespent": {"$divide": [{"$subtract": ["$end", "$start"]}, 1000]},
				"timespent_sec": {"$divide": [{"$subtract": ["$end", "$start"]}, 1000]},
				"timespent_min": {"$divide": [{"$subtract": ["$end", "$start"]}, 60000]},
				# "timespent_hms": { "$dateToString": { "format": "%H:%M:%S", "date": {"$toDate":{"$divide": [{"$subtract": ["$end", "$start"]}, 1000]}}, "timezone": "Europe/Paris"} },
				# "elapsedTimes": {"$push": {"$records.elapsedTime"}},
				"records": {
					'$map': {
						'input': '$records',
						'as': 'record',
						'in': {
							'tag': '$$record.tag',
							'value': '$$record.value',
							'unixTime': '$$record.unixTime',
							'score': '$$record.score',
							"stimulus_tag": '$$record.stimulus_tag',
							"target_tag": '$$record.target_tag',
							"CV": "$$record.CV",
							'stimulus': "$$record.stimulus",
							'target': "$$record.target",
							"click": "$$record.isClicked",
							"chapter": '$$record.chapter',
							"lesson": '$$record.lesson',
							"elapsedTime": "$$record.elapsedTime"
							
						}
					}
				},

			}
		},
		{
			"$merge": "student_day"
		},
	]
	if student is not None:
		pipeline[0] = {
				"$match": {
					"student": int(student), 
					"group": {"$ne": "guest"},
					"dataset": {"$in": ["numbers", "gp", "gapfill_lang"]}
				},
			}
	try:
		db.records.aggregate(pipeline, allowDiskUse=True)
	except pymongo.errors.DuplicateKeyError:
		pass
	
	# print("\t\t> Table student_dataset_day is ready with nb gp and gapfill!")

# ASSESSMENTS
## ASSSEMENTS CASE: RECORDS> SEQUENCE > DAY 

@timeit
def create_student_assessment_day(student=None):
	'''
	FROM records
	FIRST Group student (not guests) records by dataset by sequence day (day unixtime as start and assessmentEndTime as end)
	GROUP records by SEQUENCES
	AND THEN SEQUENCE BY DAY

	MERGE into student_day	
	'''
	
	db = connect()
	db.student_day.drop_indexes()
	pipeline = [
		{
			"$match": {
				"group": {"$ne": "guest"},
				"dataset": {"$in": ["assessments_maths", "assessments_language"]}
			},
		},
		{
			"$sort": SON([("student", 1), ("unixTime", 1), ("assessmentEndTime", 1)])
		},
		{
			#first group records by student, dataset, day, assessementEndTime 
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"dataset": "$dataset",
					"day": "$day",
					"subject": "$subject",
					"assessmentEndTime": "$assessmentEndTime",
					# "chapter": "$chapter"
				},
				#get the unixTime from the first record
				"start": {"$first": "$unixTime"},
				#get the unixTime from the last record
				# soon replaced by assessementEndTime 
    			"end": {"$last": "$unixTime"},
				#timespent( end-start) should be equal to elapsedTime (when not -1)
				"nb_records": {"$sum": 1},
				
				# assessements DO have chapter but not lessons
				# as assessementEndTime is unique chapter is unique: 
    			# but not usefull as we never see two validated chapter in the same day
				# "chapter": {"$addToSet": "$chapter"},
				# "lesson": None,
    			"records": {"$push": "$$ROOT"},
			}
		},
		# record on sequence day level  with unixtime as start and assessmentEndTime as end
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"group": "$_id.group",
				"dataset": "$_id.dataset",
				"subject": "$_id.subject",
				"day": "$_id.day",
				# "chapter": "$chapter",
				# "lesson": "$lesson",
				"nb_records": "$nb_records",
				"start": "$start",
				# here we use as sequence end time the assessementEndTime
				# instead of last record unixTime
				"end": "$_id.assessmentEndTime",
				"timespent": {"$subtract": ["$_id.assessmentEndTime", "$start"]},		
				"last_record_time": "$end",
				"records": {
					'$map': {
						'input': '$records',
						'as': 'record',
						'in': {
							'tag': '$$record.tag',
							'unixTime': '$$record.unixTime',
							'score': '$$record.score',
							'stimulus': "$$record.stimulus",
							'target': "$$record.target",
							# in assessments there is not value isClicked
							# "click": "$$record.isClicked",
							# so transforming click with score
							'click': '$$record.score',
							# just in case for verification
							"chapter": '$$record.chapter',
							"lesson": None,
       						# in assessments there is an elapsedTime
							# that gives us not the timespent 
							# but the time reaction
							# we could order by elapsedTime to have what he clicked first 
							"elapsedTime": "$$record.elapsedTime"
						}
					}
				},

			}
		},
		{
			"$sort": SON([("student", 1), ("start", 1), ("end", 1)])
		},
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"dataset": "$dataset",
					"day": "$day",
					"subject": "$subject",
					# "chapter": "$chapter",
					#"lesson": "$lesson",
				},
				"nb_sequences": {"$sum": 1},
				# superior boundaries that doesn't show the different sequences
				# means the first item of the day and the last item of the day
				"start": {"$first": "$start"},
				# end corresponds to assessmentEndTime 
				# AND not anymore to last record unixTime
				"end": {"$last": "$end"},
				# sequences unixtimes 
				"starts": {"$push":"$start"},
				"ends": {"$push": "$end"},
				"nb_records": {"$sum": "$nb_records"},
				"records": {"$push": "$records"}
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
				"day": "$_id.day",
				# "lesson": "$_id.lesson",
				# "chapter": "$_id.chapter",
				"nb_records": "$nb_records",
				# beginning of the day
				"start": "$start",
				# end of the day
				"end": "$end",
				#sequence of plays within a day
				"sequences" :{"$zip":
					{
						"inputs": ["$starts", "$ends"],
						"useLongestLength": True,
						"defaults":  [None, None],
					}
				},
				"nb_sequences": "$nb_sequences",
				#timespent within a day converted from milliseconds to seconds
				"timespent": {"$divide":[{"$subtract":["$end", "$start"]}, 1000]},
				"timespent_sec": {"$divide":[{"$subtract":["$end", "$start"]}, 1000]},
				"timespent_min": {"$divide":[{"$subtract":["$end", "$start"]}, 60000]},
				"end_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$end",  "timezone": "Europe/Paris"} },
				"start_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$start",  "timezone": "Europe/Paris"} },
				"records": {
					"$reduce": {
						"input": "$records",
						"initialValue": [],
					  		"in": {"$concatArrays": ["$$this", "$$value"]}
					}},

			}
		},
		{
			"$merge": "student_day"
		}
	]
	if student is not None:
		pipeline[0] = {
			"$match": {
				"student": int(student),
				"group": {"$ne": "guest"},
				"dataset": {"$in": ["assessments_maths", "assessments_language"]}
			},
		}
	
	db = connect()
	try:
		db.records.aggregate(pipeline, allowDiskUse=True)
	except pymongo.errors.DuplicateKeyError:
		pass


	
	

@timeit
def create_day_tables(student=None):
	if student is None:
		delete_day_tables(student=None)	
	#create student dataset day for numbers, gp, gapfill
	create_student_nb_gapfill_gp_day(student)
	# create student dataset day for assessements
	create_student_assessment_day(student)
	return True, ""
	
@timeit
def delete_day_tables(student=None):
	db = connect()
	msg = ""
	if student is not None:
		db.student_day.drop_indexes()
		db.student_day.delete_many({"student":student})
		return True, msg
	else:
		db.student_day.drop()
		db.student_day.drop_indexes()
		return True, msg
if __name__=="__main__":
	create_day_tables()
	quit()