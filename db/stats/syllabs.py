#!/usr/bin/python3
# encoding: utf-8
__doc__ = '''
Create syllabs Tables

'''
import statistics

from utils  import connect, get_color
from utils  import timeit


def build_word_from_syllabs(target):
	return "".join([c.split("-")[0] for c in target.split(".")])

@timeit
def create_student_syllabs(student=None):
	'''
	### Methods
	FROM records
	SELECT records WHERE dataset='gp' AND WHERE '.' in record[target] or '.' in record[stimulus] AND WHERE group != "guest" 
	GROUP BY classroom, student, target
	SUM nb_records, CA
	
	ADD [stimulus, stimulus,...]
	CALCULATE word
	CALCULATE %CA
	ADD color based on %CA
	OUT student_syllabs

	### OUTPUT
	```
	{
	"_id" : ObjectId("5df1031a00dcec78e5588297"),
	"classroom" : 9,
	"student" : 924,
	"group" : "r/m",
	"dataset" : "gp",
	"syllab" : "m-m.ou-u",
	"stimuli" : [
		"l-l.a-a",
		"s-s.ou-u",
		"m-m.ou-u",
		""
	],
	"CA" : 40,
	"nb_records" : 54,
	"%CA" : 74.07,
	"color" : "green",
	"word" : "mou"
	}
	```

	'''
	pipeline = [
		# {
		# 	"$in": "records"
		# },
		{
			"$match":{
				"dataset": "gp",
				"$or": [{"stimulus": {"$regex": "\\."}}, {"target": {"$regex": "\\."}}],
				"group": {"$ne":"guest"}
			}
		},
		{
			"$group": {
					"_id": {
						"classroom": "$classroom",
						"student": "$student",
						"group": "$group",
						"dataset": "$dataset",
						"target": "$target",			
					},
					"nb_records": {"$sum": 1},
					"CA": {"$sum": "$score"},
					"scores": {"$push": "$score"},
     				# "targets": {"$addToSet": "$target"},
					"stimuli": {"$addToSet": "$stimulus"}
			}
		},
		{
			"$project": {
				"_id":0,
				"classroom": "$_id.classroom",
				"student": "$_id.student",
				"group": "$_id.group",
				"dataset": "$_id.dataset",
				"syllab": "$_id.target",
				"stimuli": "$stimuli",
				"CA": "$CA",
				"scores": "$scores",
				"nb_records": "$nb_records",
				"%CA": {"$round": [{"$multiply":[{"$divide":["$CA", "$nb_records"]}, 100]}, 2]}

				# "syllabs": {"$setUnion": [ "$targets", "$stimuli"]},
				}
		},
		{
			"$out":"student_syllabs"}
	]
	db = connect()
	if student is None:
		db.student_syllabs.drop()
	if student is not None:
		
		pipeline[0] = {
			"$match":{
				"student": str(student),
				"dataset": "gp",
				"$or": [{"stimulus": {"$regex": "\\."}}, {"target": {"$regex": "\\."}}],
				# "group": {"$ne":"guest"}
			}
		}
		pipeline[-1] = {"$merge": "student_syllabs"}
	try:
		db.records.aggregate(pipeline, allowDiskUse=True)
	except pymongo.errors.DuplicateKeyError as e:
		pass
	if student is None:
		for s in db.student_syllabs.find():
			word = build_word_from_syllabs(s["syllab"])
			last_score = s["scores"][-1]
			if last_score == 1:
				color = "green"
			else:
				color = "orange"
   			# color = get_color(s["%CA"])
			db.student_syllabs.update({"_id": s["_id"]}, {"$set": {"word":word, "color": color}})
	else:
		for s in db.student_syllabs.find({"student":student}):
			word = build_word_from_syllabs(s["syllab"])
			last_score = s["scores"][-1]
			if last_score == 1:
				color = "green"
			else:
				color = "orange"
   			# color = get_color(s["%CA"])
			db.student_syllabs.update({"_id": s["_id"]}, {"$set": {"word":word, "color": color}})

def create_syllabs_tables(student=None):
	create_student_syllabs(student)
	return True, ""
def delete_syllabs_tables(student=None):
	db = connect()
	if student is None:
		db.student_syllabs.drop()
	else:
		db.student_syllabs.delete_many({"student":student})
	return True, ""

if __name__=="__main__":
	create_syllabs_tables()
	quit()