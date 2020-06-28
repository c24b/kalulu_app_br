#!/usr/bin/env python3
# encoding: utf-8
import itertools

from utils import connect
from utils import timeit


@timeit
def create_student_chapter(student=None):
	''' 
	FROM table student_lesson
	group by chapter student and dataset
	Available only for dataset="gp" and dataset="numbers"
	OUT student_chapter
	'''
	pipeline = [
		{
			"$sort": {"student":1, "subject":1,"chapter":1, "lesson":1}
		},
		{
			"$group": {
				"_id":{
					"classroom": "$classroom",
					"group": "$group",
					"student": "$student",
					# "dataset": "$dataset",
					"chapter": "$chapter",
					"subject": "$subject"
				},
				"tags":{"$addToSet": "$tag"},
				"records": {"$push": "$records"},
				"lesson_ids": {"$addToSet":"$lesson"},
				"nb_records": {"$sum": "$nb_records"},
				"timespent": {"$sum": "$timespent"},
				# "CA": {"$sum": "$CA"},
				# "WA": {"$sum": "$WA"}
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
				"chapter": "$_id.chapter",
				"tags": "$tags",
				"lesson_ids": "$lesson_ids",
				# "CA": "$CA",
				# "WA": "$WA",
				"nb_records": "$nb_records",
				"timespent": "$timespent",
				"records": {"$reduce": {
						"input": "$records",
						"initialValue": [],
					  		"in": {"$concatArrays": ["$$this", "$$value"]}
					}},
				}
		},
		{"$out": "student_chapter"}
	]
	db = connect()
	if student is None:
		db.student_chapter.drop_indexes()
		db.student_chapter.drop()
		return db.student_lesson.aggregate(pipeline, allowDiskUse=True)
	else:
		db.student_chapter.drop_indexes()
		db.student_chapter.create_index([("student",1), ("subject",1), ("chapter",1)], unique=True)
		pipeline.insert(0,{"$match":{"student":student}})
		pipeline[-1] = {"$merge": "student_chapter"}
		return db.student_lesson.aggregate(pipeline, allowDiskUse=True)
	

@timeit
def create_student_chapters(student=None):
	''' 
	FROM table student_chapter
	group by student 
	OUT student_chapters
	'''
	pipeline = [
		{
			"$sort": {"student":1, "subject":1,"chapter":1}
		},
		{
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"group": "$group",
					# "dataset": "$dataset",
					"subject": "$subject",
				},
				"chapter_ids": {"$push":"$chapter"},
				"lesson_ids": {"$addToSet": "$lesson_ids"},
				"tags": {"$addToSet":"$tags"},
				"chapter_count": {"$sum": 1},
				"records": {"$push": "$records"},
				# "CAs": {"$push": "$CA"},
				# "nb_records": {"$push": "$nb_records"},
				# "timespents": {"$push": "$timespent"},
				
			}
		},
		# {
		# 	"$addFields":{"cumul": "False"}
		# },
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"group": "$_id.group",
				# "dataset": "$_id.dataset",
				"subject": "$_id.subject",
				"chapter_ids": "$chapter_ids",
				"chapter_nb": "$chapter_count",
				"cumul": "$cumul",
				"lessons": {"$reduce": {
						"input": "$lesson_ids",
						"initialValue": [],
							"in": {"$setUnion": ["$$this", "$$value"]}
					}},
				"tags": {"$reduce": {
						"input": "$tags",
						"initialValue": [],
							"in": {"$setUnion": ["$$this", "$$value"]}
					}},
				"records": "$records",
				}
		},
		{
			"$out": "student_chapters"
		},
	]
	db = connect()
	if student is None:
		db.student_chapters.drop_indexes()
		db.student_chapters.drop()
		return db.student_chapter.aggregate(pipeline, allowDiskUse=True)
	else:
		db.student_chapters.remove({"student": student})
		db.student_chapters.drop_indexes()
		db.student_chapters.create_index([("student",1), ("subject",1) ], unique=True)
		pipeline.insert(0,{"$match":{"student":student}})
		pipeline[-1] = {"$merge": "student_chapters"}
		return db.student_chapter.aggregate(pipeline, allowDiskUse=True)	
	

@timeit
def update_student_chapter(student=None):
	'''
	Update db.student_chapters with cumulated chapters exceed storage capacity limit for a record
	"BSONObjectTooLarge" BSONObj size: 16908846 (0x102022E) is invalid. Size must be between 0 and 16793600(16MB)

	USING student_chapters
	we add cumul of chapter records inside each chapter of student_chapter
	
	CAREFUL NUMBERS HAS NO CHAPTER 13
	
	'''	
	db = connect()
	if student is None:
		chapters_refs = db.student_chapters.find()
	else:
		chapters_refs =  db.student_chapters.find({"student": student})
	#chapter ref is organized by (student,subject) "records": (chap1, chap2, chap3, ...)
	for c in chapters_refs:
		chapter_ids = c["chapter_ids"]
		for i, c_id in enumerate(chapter_ids):
			# print(i, len(c["records"]))		
			#No chapter 13 so using index to get corresponding records array
			# record_index =  chapter_ids.index(c_id)
			if i == 0:
				db.student_chapter.update(
							{
								"student":c["student"],
								"subject": c["subject"],
								# "dataset": c["dataset"],
								"chapter": c_id 
							},
							{"$set":
								{
									"cumulated_nb_records": len(c["records"]),
									"chapters": [c_id],
									# "cumul": True
								}
							}
						)
				continue
			else:
				new_records = []
				if len(chapter_ids) == i:
					for records in c["records"]:
						new_records.extend(records)
				else: 
					for records in c["records"][0: i+1]:
						new_records.extend(records)	
				db.student_chapter.update(
							{
								"student":c["student"],
								"subject": c["subject"],
								# "dataset": c["dataset"],
								"chapter": c_id 
							},
							{"$set":
								{
									"records": new_records, 
									"cumulated_nb_records": len(new_records),
									"chapters": chapter_ids[0:i+1],
									# "cumul": True
								}
							}
						)
				continue
			db.student_chapters.update({"_id": c["_id"]}, {"$set":{"cumul":"True"}})
	# DROP matrix chapter NO
	# db.student_chapters.drop()
	return

# @timeit
# def create_chapters():
# 	'''
# 	FROM student_dataset_chapter
# 	aggregate chapter metrics
# 	INTO chapters
# 	'''
# 	db = connect()
# 	db.chapters.drop()

# 	# print("\t- create `chapter` table")
# 	db.student_chapter.aggregate([
# 		{
# 			"$group": {
# 				"_id": {
# 					"dataset": "$dataset",git
# 					"subject": "$subject",
# 					"chapter": "$chapter",
# 				},
# 				"%CA": {"$push": "$%CA"},
# 				"nb_records": {"$push": "$nb_records"},
# 				"timespent": {"$push": "$timespent"},
# 				"classrooms": {"$addToSet": "$classroom"},
# 				"students": {"$addToSet": "$student"},
# 				"tags": {"$addToSet": "$tag"},
# 				"lessons": {"$addToSet": "$lessons"},
# 			}
# 		},
# 		{
# 			"$project": {
# 				"_id": 0,
# 				"dataset": "$_id.dataset",
# 				"chapter": "$_id.chapter",
# 				"tag": "$_id.tag",
# 				"avg_nb_records": {"$avg":"$nb_records"},
# 				"std_nb_records": {"$stdDevPop": "$nb_records"},
# 				"avg_%CA": {"$avg": "$%CA"},
# 				"avg_timespent": {"$avg": "$timespent"},
# 				"std_%CA": {"$stdDevPop": "$%CA"},
# 				"std_timespent": {"$stdDevPop": "$timespent"},
# 				"students": "$students",
# 				"nb_students": {"$size": "$students"},
# 				"classrooms": "$classrooms",
# 				"nb_classrooms": {"$size": "$classrooms"},
# 				"lessons": "$lessons",
# 				"tags": "$tags"
# 			}
# 		},
# 		{
# 			"$out": "chapters"
# 		}
# 	], allowDiskUse=True)
# 	# print("\t> created chapters tables")
# 	# rounding maths because much simpler than in mongo
# 	for n in db.chapters.find():
# 		try:
# 			avg_CA = round(n["avg_%CA"], 2)
# 			avg_timespent = round(n["avg_timespent"], 2)
# 			std_CA = round(n["std_%CA"], 2)
# 			std_timespent = round(n["std_timespent"], 2)
# 			modif = {
# 				"$set": {
# 							"avg_%CA": avg_CA,
# 							"avg_timespent": avg_timespent,
# 							"std_%CA": std_CA,
# 							"std_timespent": std_timespent,
# 							"color": CHAPTER_COLORS[n["chapter"]]
# 							}
# 			}
# 			db.chapters.update({"_id": n["_id"]}, modif)
# 		except TypeError:
# 			#somewhere element is None
# 			pass
def delete_student_chapter(student=None):
	db = connect()
	if student is None:
		db.student_chapter.drop()
	else:
		db.student_chapter.remove({"student": student})
	
def delete_student_chapters(student=None):
	db = connect()
	if student is None:
		db.student_chapters.drop()
	else:
		db.student_chapters.delete_many({"student": student})

@timeit
def create_chapter_tables(student=None):
	create_student_chapter(student)
	create_student_chapters(student)
	#cumulate chapter records in records
	update_student_chapter(student)
	#NOT USEFULL
	# create_chapters()
	return True, ""
@timeit
def delete_chapter_tables(student=None):
	# NEW
	delete_student_chapter(student)
	delete_student_chapters(student)
	return True, ""
	# update_student_chapter(student)
	#NOT USEFULL
	# create_chapters()

if __name__ == "__main__":
	create_chapter_tables()
	quit()
	# create_student_chapter(None)
