#!/usr/bin/python3
# encoding: utf-8

__doc__ = ''' 
Generate words statistics
'''
import itertools
import statistics
from operator import itemgetter

from utils import connect, get_color
from utils import timeit
from .tag import create_student_tag

def get_words():
	'''
	filter out words from db.path if type is 'word'
	'''
	db = connect()
	for tag in db.records.distinct("tag", {"dataset": "assessments_language"}):
		try:
			is_word = db.path.find_one({"stimuli": tag})
			if is_word is not None:
				if is_word["type"] == "word":
					yield tag
		except:
			pass
		


@timeit
def create_student_words(student=None):
	'''
	FROM student_tag 
	filter out dataset (gapfill_lang and assessments_language)
	filter out tag that has type="word" in db.path table
	filter out only words that have been clicked and have then an elapsedTime set (not -1)
	insert the scores into student_words table
	OUT student_words
	'''
	db = connect()
	words = [n for n in get_words() if n is not None]
	if student is None:
		db.student_words.drop()
	h = ["classroom", "student", "word","type", "%CA", "CA", "nb_records", "nb_letters","median_time_reaction", "records", "color"]
	if "student_tag" not in db.list_collection_names():
		create_student_tag(student)
	if student is None:
		for l in db.student_tag.find({"dataset": {"$in": ["gapfill_lang", "assessments_language"]}, "tag":{"$in":words}}):
			#take all the tag.type'word' as only dataset gapfill have isClicked=1 
			# Take elapsedTime > -1 that is common
			records = [r for r in l["records"] if r["elapsedTime"] > -1]
			scores = [r["score"] for r in records]
			nb_records = len(scores)
			CA = None
			CA100 = None
			color = None
			if nb_records > 0:
				last_CA = scores[-1]
				CA = sum(scores)
				CA100 = round((CA/nb_records)*100, 2)
				if last_CA == 1:
					color = 'green'
				else:
					color = 'orange'
    			# color = get_color(CA*100)
			
			nb_letters = len(l["tag"])
			#compute median time reaction
			median_time_reaction = statistics.median([r["elapsedTime"] for r in l["records"]])
			word_rec = [l["classroom"], l["student"], l["tag"],"word", CA100, CA, nb_records, nb_letters, median_time_reaction,records, color]
			word_s = dict(zip(h, word_rec))
			db.student_words.insert(word_s)
	else:
		for l in db.student_tag.find({"student":student, "dataset": {"$in": ["gapfill_lang", "assessments_language"]}, "tag":{"$in":words}}):
			records = [r for r in l["records"] if r["elapsedTime"] > -1]
			scores = [r["score"] for r in records]
			nb_records = len(scores)
			CA = None
			CA100 = None
			color = None
			if nb_records > 0:
				last_CA = scores[-1]
				CA = sum(scores)
				CA100 = round((CA/nb_records)*100, 2)
				if last_CA == 1:
					color = "green"
				else:
					color = "orange"
    			# color = get_color(CA100)
			
			nb_letters = len(l["tag"])
			#compute median time reaction
			median_time_reaction = statistics.median([r["elapsedTime"] for r in l["records"]])
			word_rec = [l["classroom"], l["student"], l["tag"],"word", CA100, CA, nb_records, nb_letters, median_time_reaction,records, color]
			word_s = dict(zip(h, word_rec))
			db.student_words.insert(word_s)

@timeit
def create_words():
	'''
	### Methods
	Table words is created with script db/stats/words.py
	
	```sql
	FROM student_words
	group words, along with their nb_letters
	sum nb_records
	calculate AVG(median_time_reaction, %CA, nb_records
	insert unique [student, student, ...] 
	insert unique [classroom, classroom, ...]       
	OUT words
	```
	### Output example
	```
	{
		"_id" : ObjectId("5df40a4598f28e7c4f67291d"),
		"word" : "demi",
		"nb_letters" : 4,
		"avg_%CA" : 56.69098870056497,
		"nb_records" : 982,
		"avg_nb_records" : 2.774011299435028,
		"avg_time_reaction" : 2.3198094717514124,
		"nb_students" : 354,
		"nb_classrooms" : 38
	}
	```
	'''
	db = connect()
	if "student_words" not in db.list_collection_names():
		create_student_words()
	db = connect()
	db.words.drop()
	pipeline = [
		{"$group": 
			{
				"_id": {
					"word": "$word",
					# "chapter": "$chapter",
					# "type": "$type",
					"nb_letters": "$nb_letters"
				},
				"avg_time_reaction": {"$avg": "$median_time_reaction"},
				# "CA": {"$push": "$CA"},
				# "%CA": {"$push": "$%CA"},
				"avg_%CA": {"$avg":"$%CA"},
				"avg_nb_records": {"$avg": "$nb_records"},
				"nb_records": {"$sum": "$nb_records"},
				"students": {"$addToSet": "$student"},
				"classrooms": {"$addToSet": "$classroom"}
			}
		},
		{
			"$project": {
				"_id": 0,
				"word": "$_id.word",
				# "chapter": "$_id.chapter",
				# "type": "$_id.type",
				"nb_letters": "$_id.nb_letters",
				"CA": "$CA",
				"%CA": "$%CA",
				"avg_%CA": "$avg_%CA",
				"nb_records": "$nb_records",
				"avg_nb_records":"$avg_nb_records",
				"avg_time_reaction": "$avg_time_reaction",
				# "students": "$students",
				# "classrooms": "$classrooms",
				"nb_students": {"$size": "$students"},
				"nb_classrooms": {"$size": "$classrooms"}
			},
		},
		{
			"$out": "words"
		}
	]
	db.student_words.aggregate(pipeline, allowDiskUse=True)
	

def delete_words_tables(student=None):
	db = connect()
	if student is None:
		db.student_words.drop()
		db.words.drop()
		return True, ""
	else:
		db.student_words.remove({"student":student})
		create_words()
		return True, ""

def create_words_tables(student=None):
	create_student_words(student)
	create_words()
	return True, ""

if __name__=="__main__":
	create_words_tables()
	quit()	
