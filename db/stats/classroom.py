#!/usr/bin/python3
# encoding: utf-8

__doc__ = '''
Compute statistics from records to tables

- classroom_info: overview of classrooms (r/m or m/r)
- classroom_days: daily activity by classrooms
'''

from datetime import datetime as dt

from utils  import SON, connect
from utils  import timeit

def create_classroom_progression_matrix():
	print("Classroom")
	
	pipeline = [
		{
			"$sort": {"classroom":1, "student":1, "chapter":1, "lesson":1}
		},
		{
			"$group": {
				"_id":{
					"classroom": "$classroom",
					"student": "$student",
					"subject":"$subject",
					"dataset": "$dataset",
				},
			"chapters": {"$push":"$chapter"},
			"tags": {"$push":"$tag"},
			"lessons": {"$push": "$lesson"},
			"%CA_colors": {"$push":"$%CA_color"},
			"%CAs": {"$push":"$%CA"},
			"timespents": {"$push": "$timespent"},
			}
		},
		{
			"$addFields": {				
				"series":{"$zip": {
					"inputs": 
					["$tags","$chapters", "$lessons", "$%CA_colors", "$%CAs", "$timespents"], 

				}}
			}
		},
		{
			"$out": "student_progression_matrix"
		}
	]
	db = connect()
	print("Student_progression_matrix aggregate")
	db.student_progression_matrix.drop()
	db.student_dataset_lesson.aggregate(pipeline)
	
	print("Student_progression_matrix format")
	for record in db.student_progression_matrix.find():
		
		students_classroom = [(i,student) for i, student in enumerate(db.student_dataset_lesson.distinct("student", {"classroom": record["_id"]["classroom"]}))]
		student_i = [n[0] for n in students_classroom if n[1] == record["_id"]["student"]][0]
		data = {
			"name": record["_id"]["student"], 
			"student_i": student_i, 
			# x = lessons
			"data": record["lessons"], 
			"x_axis": record["lessons"],
			"x_labels": record["tags"],
			"x_hover_text": record["timespents"],
			"x_axis_colors": record["%CA_colors"], 
			# y = student line
			"y_axis": [record["_id"]["student"] for x in record["lessons"]],
			# w = chapters
			"w_axis": record["chapters"],
			"w_colors": [CHAPTER_COLORS[c] for c in record["chapters"]], 
			# "w_label": "Chapters",
		}

		db.student_progression_matrix.update({"_id":record["_id"]}, {"$set":
			data}) 
	pipeline = [
		{
			"$sort": {"classroom":1, "student":1, "chapter":1, "lesson":1}
		},
		{
			"$group": {
				"_id":{
					"classroom": "$_id.classroom",
					"subject":"$_id.subject",
					"dataset": "$_id.dataset",
				},
			"students_i": {"$push": "$i"},
			"students": {"$push": "$_id.student"},
			"lines": {"$push":"$data"},
			"marker_labels": {"$push": "$tags"},
			"marker_hoverinfos": {"$push": "$x_hover_text"},
			"marker_colors": {"$push": "$x_axis_colors"},
			"tags": {"$addToSet":"$tags"},
			"lessons": {"$addToSet": "$lessons"},
			"chapters": {"$push": "$chapters"},
			"w_colors": {"$push": "$w_colors"}
			}
		},
		{
			"$project": {
				"_id": 0,
				"classroom": "$_id.classroom",
				"subject": "$_id.subject",
				"dataset": "$_id.dataset",
				"y": "$students",
				"y_axis": {"$zip": {
					"inputs": ["$students_i", "$students"]
					}
				},
				"lines": "$lines",
				"marker_labels": "$marker_labels",
				"marker_hoverinfos": "$marker_hoverinfos",
				"marker_colors": "$marker_colors",
				"x_label": "Lessons",
				"x_axis": {
							"$reduce": {
								"input": "$lessons",
								"initialValue": [],
								"in": {"$setUnion": ["$$this", "$$value"]}
							}},
				"x_axis_labels": {
							"$reduce": {
								"input": "$tags",
								"initialValue": [],
								"in": {"$setUnion": ["$$this", "$$value"]}
							}},
				"y_label": "Elèves",
				"w_labels": "Chapitres",
				"w_axis": {
							"$reduce": {
								"input": "$chapters",
								"initialValue": [],
								"in": {"$setUnion": ["$$this", "$$value"]}
							}},
				"w_axis_colors":{
							"$reduce": {
								"input": "$w_colors",
								"initialValue": [],
								"in": {"$setUnion": ["$$this", "$$value"]}
							}},
				
			}
		},
		{
			"$out": "classroom_progression_matrix"
		}
	]
	db.classroom_progression_matrix.drop()
	db.student_progression_matrix.aggregate(pipeline, allowDiskUse=True)
	db.student_progression_matrix.drop()
	print("Classroom progression matrix ready!")
	return

def create_classrooms_table():
    pipeline = [{
        "$group": {
            "_id":{
                "classroom": "$classroom"
            },
            "students": {"$push": "$student"},
            "group": {"$addToSet": "$group"},
            "subjects": {"$addToSet": "$subject"},
            "datasets": {"$addToSet": "$dataset"},
            "lessons": {"$addToSet": "$lessons"},
            "chapters": {"$addToSet": "$chapters"}
        }
    }, 
    {
        "$project": {
            "_id": 0, 
            "classroom": "$_id.classroom",
            "students": "$students",
            "group": "$group",
            "datasets": "$datasets",
            "subjects": "$subjects",
            "lessons": {
                "$reduce":{
                "input": "$lessons",
								"initialValue": [],
								"in": {"$setUnion": ["$$this", "$$value"]}
							}},
            
                
            # "chapters": {
            #     "$reduce":{
            #     "input": "$chapters",
			# 					"initialValue": [],
			# 					"in": {"$setUnion": ["$$this", "$$value"]}
			# 				}},
            # }
        }
    },
    {
        "$out": "classrooms"
    }
    ]
    db = connect()
    db.classrooms.drop()
    db.student_dataset_lesson.aggregate(pipeline)
	return True, ""
	
def create_classroom_tables():
    create_classroom_table()
    create_classroom_progression_matrix()
	return True, ""