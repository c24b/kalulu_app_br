#!/usr/bin/env python3

from utils import connect
from utils import timeit
import itertools




@timeit
def insert_student_lesson(student=None):
	'''
	FROM student_day
	select dataset gp and numbers records
	INSERT into student_lesson
	with subject
	'''
	# print("insert gp records into student_dataset_lesson")
	db = connect()
	#STUDENT
	# in student_day assessements + lessons games
	#so filtering on dataset 
	for dataset_subject in [("numbers", "numbers"), ("gp", "letters")]:
		dataset, subject = dataset_subject
		if student is None:
			students = db.student_day.distinct("student", {"dataset": dataset})
			if len(students) == 0:
				continue
		else:
			if db.student_day.count( {"dataset": dataset, "student":student}) == 0:
				continue
			else:
				students = [int(student)]
		for student_id in students:
			# being sure of student_day scope for records (student, dataset)
			student_dataset_day = []	
			# DAY SCOPE
			# iterate throught the day scope in student_day for one student one dataset
			for record_day in db.student_day.find({"student": student_id, "dataset": dataset}):
				subject = record_day["subject"]
				classroom = record_day["classroom"]
				group = record_day["group"]
				daily_sequences = []
				# as ordered by day
				day = record_day["day"]
				# group by lessons id not over the day but sequentially
				# that was not possible in mongo that sort by group _id
				# but possible in python specifying the local scope 
				# (groupby is an iterator: so local scope is preserved)
				for lesson_id, records in itertools.groupby(record_day["records"], key=lambda x: x["lesson"]):
					records = list(records)
					nb_records = len(records)
					CA = sum([n["score"] for n in records])
					start = records[0]["unixTime"]
					end = records[-1]["unixTime"]
					timespent = (end - start).seconds
					tag = records[0]["tag"]
					chapter = records[0]["chapter"]
					
					# elapsedTime = [n["elapsedTime"] for n in records]
					# somewhere in record a 'target' is missing
					try:	
						headers = ["tag", "CV", "target", "stimulus","target_tag", "stimulus_tag",
														"click", "score", "elapsedTime"]
						signals = [dict(zip(headers, [r[k] for k in headers]))
														for r in records]
						
					#stimulus is missing
					# so for this peculiar case we copy records
					# in confusion we will have to sort again the keys
					# to get (target,stimulus,click,score)
					except KeyError:
						signals = records
						# db.student_dataset_day.update({"_id": record_day["_id"]}, {
						# 								"$set": {"signals": records}})
					# here is the minimal definition of a lesson
					# in the day scope
					sequence = {
						"classroom": classroom,
						"group": group,
						"student": student_id,
						"dataset": dataset,
						"subject": subject,
						"lesson": lesson_id,
						"chapter": chapter,
						"start": start,
						"end": end,
						"timespent": timespent,
						"sequence": [[start, end]],
						# "elapsedTime": elapsedTime,
						"nb_records": nb_records,
						"CA": CA,
						"records": signals,
						"tag": tag,
						"tags": [tag],
						"lessons": [lesson_id],
						"days": [day]
					}
					try:
						# here we compare with previous sequence
						previous = daily_sequences[-1][1]
						if previous["lesson"] >= lesson_id:
							# as we are in the same day
							# we can postpone end bondary to the current
							previous["end"] = end
							#avoiding the case if record = 1 then start and end are equal
							# and thought timespent is 0
							previous["timespent"] = (
								end - previous["start"]).seconds
							# same `lesson` aggregating scores
							previous["nb_records"] += nb_records
							previous["CA"] += CA
							# previous["elapsedTime"].extend(elapsedTime)
							previous["records"].extend(signals)
							previous["tags"].append(tag)
							previous["lessons"].append(lesson_id)
							previous["sequence"].append([start, end])
							previous["days"].append(day)
							# putting back the modification inside the stack
							daily_sequences[-1][1] = previous
						else:
							# add the daily_sequence inside the stack
							daily_sequences.append([lesson_id, sequence])
					except IndexError:
						# first daily_sequence add inside the stack
						daily_sequences.append([lesson_id, sequence])
				
				try:
					#scope is now over the days
					# we compare each sequence of the current day to the previous day 
					for curr_day in daily_sequences:
						previous_day = student_dataset_day[-1]
						#if previous_day has an upper lesson number or the same
						if previous_day[0] >= curr_day[0]:
							# we aggregate the daily_sequence info
							previous_day[1]["days"].extend(curr_day[1]["days"])
							# as the scope is not same day we simply add curr seq timespent
							previous_day[1]["timespent"] += curr_day[1]["timespent"]
							previous_day[1]["CA"] += curr_day[1]["CA"]
							previous_day[1]["nb_records"] += curr_day[1]["nb_records"]
							# records now belongs to the previous lesson
							# previous_day[1]["elapsedTime"].extend(
							# 	curr_day[1]["elapsedTime"])
							previous_day[1]["records"].extend(
								curr_day[1]["records"])
							previous_day[1]["lessons"].extend(
								curr_day[1]["lessons"])
							previous_day[1]["tags"].extend(
								curr_day[1]["tags"])
							previous_day[1]["sequence"].extend(
								curr_day[1]["sequence"])
							previous_day[1]["end"] = curr_day[1]["end"]
							student_dataset_day[-1][1] = previous_day[1]
							continue
						else:
							#if lesson_id > previous day lesson _id
							# this is a new sequence
							student_dataset_day.append(curr_day)        
				except IndexError:
					#first daily sequences
					#add into into the stack
					student_dataset_day.extend(daily_sequences)
			
			# cleaning a bit the student_dataset_lesson
			# before inserting it
			
			for seq in student_dataset_day:
				sequence = seq[1]
				sequence["subject"] = subject
				sequence["dataset"] = dataset
				sequence["WA"] = sequence["nb_records"]-sequence["CA"]
				sequence["CA_rate"] = round(sequence["CA"]/sequence["nb_records"],2)
				sequence["WA_rate"] = round(sequence["WA"]/sequence["nb_records"],2)
				sequence["%WA"] = round((sequence["WA"]/sequence["nb_records"])*100,2)
				sequence["%CA"] = round((sequence["CA"]/sequence["nb_records"])*100,2)
				# sequence["days"] = list(set(sequence["days"]))
				sequence["tags"] = list(set(sequence["tags"]))
				sequence["lessons"] = list(set(sequence["lessons"]))
				sequence["nb_days"] = len(set(sequence["days"]))
				sequence["nb_sequence"] = len(sequence["sequence"])
				del sequence["sequence"]
				del sequence["days"]
				db.student_lesson.insert(sequence)
	


@timeit
def create_lessons():
	'''
	FROM student_dataset_lessons
	group by lessons process metrics aggregate records
	OUT lessons
	'''
	db = connect()
	db.lessons.drop()
	# the table student_lesson is required for creating lessons
	# student_lesson > lessons > student_lesson 
	if "student_lesson" not in db.list_collection_names():
		create_student_lessons()
	# print("\t- create `lessons` TABLE")
	db.student_lesson.aggregate([
		{
			"$group": {
				"_id": {
					"dataset": "$dataset",
					"subject": "$subject",
					"chapter": "$chapter",
					"lesson": "$lesson",
					"tag": "$tag",
					
				},
				"%CA": {"$push": "$%CA"},
				"nb_records": {"$push": "$nb_records"},
				"timespent": {"$push": "$timespent"},
				"classrooms": {"$addToSet":"$classroom"},
				"students": {"$addToSet": "$student"},
			}
		},
		{
			"$project": {
				"_id": 0,
				"dataset": "$_id.dataset",
				"lesson": "$_id.lesson",
				"chapter": "$_id.chapter",
				"tag": "$_id.tag",
				"avg_nb_records": {"$avg": "$nb_records"},
				"std_nb_records": {"$stdDevPop": "$nb_records"},
				"avg_%CA": {"$avg": "$%CA"},
				"avg_timespent": {"$avg": "$timespent"},
				"std_%CA": {"$stdDevPop": "$%CA"},
				"std_timespent": {"$stdDevPop": "$timespent"},
				"students": "$students",
				"nb_students": {"$size": "$students"},
				"classrooms": "$classrooms",
			}
		},
		{
			"$out": "lessons"
		}
	], allowDiskUse=True)
	# print("\t> created lessons tables")
	# rounding maths
	for n in db.lessons.find():
		chapter_color = db.path.find_one({"chapter":n["chapter"], "dataset": n["dataset"]}).get("chapter_color")
		modif = {
			"$set":{
							"chapter_color": chapter_color,
							"avg_nb_records": round(n["avg_nb_records"], 2),
					 		"std_nb_records": round(n["std_nb_records"], 2),
							"avg_%CA": round(n["avg_%CA"], 2),
							"avg_timespent": round(n["avg_timespent"], 2),
							"std_%CA": round(n["std_%CA"], 2),
							"std_timespent": round(n["std_timespent"], 2)
						}
		}
		db.lessons.update({"_id": n["_id"]},modif)
		
		
@timeit
def update_student_lesson():
	'''
	FROM lessons
	compare performances (%CA, timespent) 
	add color code field to each lesson of a student
	inside student_lesson table
	UPDATE student_lesson
	'''
	db = connect()
	# print("\t- update student_lessons table with stats")
	# to update student lesson lessons is required
	# student_lesson > lessons > student_lesson
	if "lessons" not in db.list_collection_names():
		create_lessons()
	for student_record in db.student_lesson.find({}, no_cursor_timeout=True):
		dataset = student_record["dataset"]
		subject = student_record["subject"]
		tag = student_record["tag"]
		lesson = student_record["lesson"]
		chapter = student_record["chapter"]
		record = db.lessons.find_one(
			{"chapter": chapter, "lesson": lesson, "tag": tag, "dataset": dataset})
		chapter_color = record["chapter_color"]
		avg_ca100 = record["avg_%CA"]
		std_ca100 = record["std_%CA"]
		avg_ts = record["avg_timespent"]
		std_ts = record["std_timespent"]
		if student_record["%CA"] < (avg_ca100 - (2 * std_ca100)):
			score_color = "red"
		elif student_record["%CA"] >= (avg_ca100 - std_ca100):
			score_color = "green"
		else:
			# elif student_record["%CA"] <= (avg_ca100 - std_ca100):
			score_color = "orange"

		if student_record["timespent"] <= avg_ts + std_ts:
			time_color = "green"
		elif student_record["timespent"] >= (avg_ts + std_ts):
			time_color = "orange"
			
		elif student_record["timespent"] > (avg_ts + (2 * std_ts)):
			time_color = "red"
		
		db.student_lesson.update(
			{"_id": student_record["_id"]},
			{
				"$set": {
					"chapter_color": chapter_color,
					"timespent_color": time_color,
					"timespent_avg": avg_ts,
					"%CA_color": score_color,
					"%CA_avg": avg_ca100
				}
			}
		)
	# print("\t> updated lessons table")
@timeit
def create_student_lessons(student=None):
	'''
	Store for one student all the lessons given the dataset and the subject
	Used for classroom progression graph + student_activity widget
	'''
	pipeline = [
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					"dataset": "$dataset",
					"subject": "$subject",
				},
				"lesson_ids": {"$push":"$lesson"},
				"lessons_count": {"$sum": 1},
				"tags": {"$push": "$tag"},
				"chapters": {"$push": "$chapter"},
				"chapter_colors": {"$push": "$chapter_color"},
				# "records": {"$push": "$records"},
				"nb_records": {"$push": "$nb_records"},
				"CA": {"$push": "$CA"},
				"WA": {"$push": "$WA"},
				"CA_rates" : {"$push":"$CA_rate"},
				"WA_rates" : {"$push":"$WA_rate"},
				"%CA_colors" : {"$push": "$%CA_color"},
				"timespents": {"$push": "$timespent"},
				"timespent_colors" : {"$push": "$timespent_color"},
			}
		},
		# {
		# 	"$addFields": {
		# 		"matrix": {
		# 			"$zip": {"inputs": [
		# 				"$lesson_ids", "$tags","$chapters", 
		# 				"$CA","$CA_rates","$WA_rates","$%CA_colors", 
		# 				"$timespent_colors", "$timespents",
		# 				"$nb_records"
		# 				# ,"$records"
		# 				]
		# 			} 
		# 		}
			
		# 	}
		# },
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"group": "$_id.group",
				"dataset": "$_id.dataset",
				"subject": "$_id.subject",
				"lesson_ids": "$lesson_ids",
				"lessons_nb": "$lesson_count",
				"tags": "$tags",
				"timespents": "$timespents",
				"%CA_colors": "$%CA_colors",
				"chapters": "$chapters",
				"chapter_colors": "$chapter_colors",
				# "lessons": "$matrix"
				}
		},
		{
			"$out": "student_lessons"
		},
	]
	db = connect()
	if student is None:
		db.student_lessons.drop_indexes()
		db.student_lessons.drop()
	else:
		db.student_lessons.drop_indexes()
		db.student_lessons.create_index([("student",1), ("subject",1),("lesson",1)], unique=True)
		pipeline.insert(0, {"match":{"student":int(student)}})
		pipeline[-1] = {"$merge":"student_lessons"}
	
	db.student_lesson.aggregate(pipeline, allowDiskUse=True)	
	# if student is None:
	# 	for student_lessons in db.student_lessons.find():
	# 		lessons = student_lessons["lessons"]
	# 		header = ["lesson", "tag", "chapter", "CA", "CA_rate", "WA_rate", "CA_color", "timespent_color", "timespent", "nb_records","records"]
	# 		lessons = [dict(zip(header, n)) for n in lessons] 
	# 		db.student_lessons.update({"_id":student_lessons["_id"]}, {"$set": {"lessons": lessons}})
	# else:
	# 	for student_lessons in db.student_lessons.find({"student":int(student)}):
	# 		lessons = student_lessons["lessons"]
	# 		header = ["lesson", "tag", "chapter", "CA", "CA_rate", "WA_rate", "CA_color", "timespent_color", "timespent", "nb_records","records"]
	# 		lessons = [dict(zip(header, n)) for n in lessons] 
	# 		db.student_lessons.update({"_id":student_lessons["_id"]}, {"$set": {"lessons": lessons}})
	# drop detailled vue? NON used in graph
	# db.student_lesson.drop()


@timeit	
def create_lesson_tables(student=None):
	db = connect()
	if student is None:	
		db.student_lesson.drop()
		db.student_lessons.drop()
		db.lessons.drop()
		
	else:
		db.student_lesson.delete_many({"student":student})
		db.student_lessons.remove_many({"student":student})
	insert_student_lesson(student)
	create_lessons()
	update_student_lesson()
	create_student_lessons()
	return
@timeit
def delete_lesson_tables(student=None):
	db = connect()
	if student is None:
		db.student_lesson.drop()
		db.lessons.drop()
		return True, ""
	else:
		db.student_lesson.delete_many({"student":student})
		# regenerate lessons stats without the student
		create_lessons()
		update_student_lesson()
		return True, ""
		
if __name__ == "__main__":
	create_lesson_tables()
	quit()