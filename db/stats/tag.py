#!/usr/bin/python3
# encoding: utf-8

__doc__ = ''' 
Generate tags statistics
'''

from utils  import connect, SON
from utils  import timeit

@timeit
def create_student_tag(student=None):
	'''
	FROM records
	create table student_tag from records
	that group unique tag by student along with the full records for this tag
	OUT student_tag
	---
	> db.student_tag.findOne()
	{
		"_id" : ObjectId("5ddffedb11d14dadde957ba3"),
		"subject" : "letters",
		"dataset" : "assessments_language",
		"tag" : "aller",
		"student" : 153,
		"classroom" : 1,
		"nb_records" : 2,
		"CA" : 2,
		"records" : [...]
	}
	'''
	db = connect()
	if student is None:
		db.student_tag.drop()
	pipeline = [
			
			{
				"$group": {
					"_id": {
						"subject": "$subject",
                        "dataset": "$dataset",
						"group": "$group",
						"tag": "$tag",
						"student": "$student",
						"classroom": "$classroom"
					},
					"records": {"$push": "$$ROOT"},
					"nb_records": {"$sum": 1},
					"CA": {"$sum": "$score"}
				}
			},
			# {
			# 	"$sort": SON([("student", 1), ("dataset", 1), ("unixTime", 1)])
			# },
			{
				"$project": {
					"_id": 0,
                    "subject": "$_id.subject",
					"dataset": "$_id.dataset",
					"group": "$_id.group",
					"tag": "$_id.tag",
					"student": "$_id.student",
					"classroom": "$_id.classroom",
					"nb_records": "$nb_records",
					"CA": "$CA",
					"records": "$records",
					
				}
			},
			{
				"$out": "student_tag"
			}
		]
	if student is not None:
		pipeline.insert(0,{"$match": {"student": student}})
		pipeline[-1] = {"$merge": "student_tag"}
	return db.records.aggregate(pipeline, allowDiskUse=True)

@timeit
def create_student_tags(student=None):
	'''
	AGGREGATE for one student all his tags
	---
	db.student_tags.findOne()
	{
		"_id" : ObjectId("5ddffedb11d14dadde957ba3"),
		"subject" : "letters",
		"student" : 153,
		"classroom" : 1,
		
	}
	'''
	db = connect()
	if student is None:
		db.student_tags.drop()
	pipeline = [
			{
				"$sort": SON([("student", 1), ("dataset", 1), ("unixTime", 1)])
			},
			{
				"$group": {
					"_id": {
						"subject": "$subject",
                        "dataset": "$dataset",
						"group":" $group",
						"student": "$student",
						"classroom": "$classroom"
					},
					"tags": {"$push": "$tags"},
					"nb_tags": {"$sum": 1},
					"nb_records": {"$push":"$nb_records"},
					"records": {"$push": "$records"},
					"CA": {"$push": "$CA"}
				}
			},
			{
				"$sort": SON([("student", 1), ("dataset", 1), ("records.unixTime", 1)])
			},
			{
				"$project": {
					"_id": 0,
                    "subject": "$_id.subject",
					"dataset": "$_id.dataset",
					"group": "$_id.group",
					"tags": "$tags",
					"student": "$_id.student",
					"nb_records": "$nb_records",
					"CA": "$CA",
					"records": "$records",
					
				}
			},
			{
				"$out": "student_tags"
			}
		]
	if student is not None:
		pipeline.insert(0,{"$match": {"student": int(student)}})
		pipeline[-1] = {"$merge": "student_tags"}
		
	return db.student_tag.aggregate(pipeline, allowDiskUse=True)

def create_tag_tables(student=None):
	create_student_tag(student)
	create_student_tags(student)
	return True, ""
def delete_tag_tables(student = None):
	db = connect()
	if student is None:
		db.student_tag.drop()
		db.student_tags.drop()
	else:
		db.student_tag.remove({"student":student})
		db.student_tags.remove({"student":student})
	return True, ""

if __name__ == "__main__":
	create_tag_tables()
	quit()