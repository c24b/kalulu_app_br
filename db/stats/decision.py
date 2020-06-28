#!/usr/bin/python3
# encoding: utf-8

__doc__ = ''' 
Generate decision statistics and graphs
'''
import json
import itertools
import statistics
from operator import itemgetter

from utils  import pymongo
from utils  import connect
from utils  import timeit
from .tag import create_tag_tables
from .words import create_words_tables
from .syllabs import create_syllabs_tables

@timeit
def digital_decision(student=None):
	"""
	1. Detect pairs from chapters
	FROM records
	WHERE dataset ="assessements_maths'
	select DISTINCT student, chapter, (unixTime, elapsedTime)
	push tags [lower,upper]
	SUM scores/2 
	SUM nb_records/2
	push elapsedTime.0 as time_reaction
	COMPUTE difference (upper-lower)

	2. group by (chapter, student, subject, difference)
	push score as CA []
	push nb_records as nb_records []
	push time_reaction as time_reactions []
	
	3. Compute median_time reaction and %CA
	(no median available in mongodb using statistics python)
	OUT student_decision
	"""
	pipeline = [
		{
			"$match": {
				"dataset": "assessments_maths",
				"game": "fish",
				"group": {"$ne": "guest"}
			},
		},
		{
			#group by elapsedTime & Unixtime
			#to get the pair of values proposed
			#at the same time 
			"$group": {
				"_id": {
					"classroom": "$classroom",
					"student": "$student",
					"chapter": "$chapter",
					"elapsedTime": "$elapsedTime",
					"unixTime": "$unixTime"
					},
				"tags": {"$push":"$tag"},
				"scores": {"$sum": "$score"},
				"nb_records": {"$sum": 1}
			}
		},
		
		{
    		"$project": {
				"_id": 0,
				"classroom": "$_id.classroom",
				"student": "$_id.student",
				"chapter": "$_id.chapter",
				"subject": "numbers",
				"time_reaction": "$_id.elapsedTime",
				"lower": {"$toInt": { "$arrayElemAt": ["$tags",0]}},
				"upper": {"$toInt": { "$arrayElemAt": ["$tags",1]}},
				"CA": { "$divide": ["$scores", 2 ]},
				"nb_records": {"$divide": ["$nb_records",2]},
				"tags": "$tags"
			},	
    	},
		{
			"$addFields":
				{ 
					"difference": {"$subtract": ["$upper", "$lower"] },
				}
		},
		{
			"$group":{
				"_id":{
					"classroom": "$classroom",
					"student": "$student",
					"chapter": "$chapter",
					"subject": "$subject",
					"difference": "$difference"
				},
				"tags": {"$addToSet":"$tags"},
				"time_reactions": {"$push": "$time_reaction"},
				"CA": {"$sum": "$CA"},
				"nb_records": {"$sum": "$nb_records"},		
			}
		},
		{
			"$project":{
				"_id": 0,
				"classroom": "$_id.classroom",
				"student": "$_id.student",
				"chapter": "$_id.chapter",
				"subject": "numbers",
				"difference": "$_id.difference",
				"tags": "$tags",
				"time_reactions": "$time_reactions",
				"CA": "$CA",
				"nb_records": "$nb_records",
			}
		},	
		{
			"$merge": "student_decision"
		}
	]
	db = connect()
	db.student_decision.remove({"subject":"numbers"})
	db.records.aggregate(pipeline, allowDiskUse=True)
	for record in db.student_decision.find({"subject": "numbers"}):
		#compute median time reaction by difference
		CA_pct = round((record["CA"] / record["nb_records"]) *100, 2)
		time_reactions = record["time_reactions"]
		if len(time_reactions) == 0:
			median_time_reaction = None
		elif len(time_reactions) == 1:
			median_time_reaction = round(time_reactions[0],2)
		else:
			median_time_reaction = round(statistics.median(record["time_reactions"]), 2)
		db.student_decision.update({"_id":record["_id"]}, {"$set":{
			"CA%": CA_pct,
			"median_time_reaction":median_time_reaction
			}
		})
	
@timeit
def avg_digital_decision(student=None):
	'''Get the average median time reaction by difference over the chapters'''
	pipeline = [
		{
			"$match": {
				"subject":"numbers",
				"difference": {"$ne": None},
				}
		},
		{
			"$group": {
				"_id": {
					"student": "$student",
					"classroom" : "$classroom",
					"difference" : "$difference",
				},
				"avg_median_time_reaction": {"$avg": "$median_time_reaction"},
				"avg_CA%": {"$avg": "$CA%"}
			}
		},
		{
			"$project": {
				"_id": 0,
				"subject": "numbers",
				"chapter": "average",
				"student": "$_id.student",
				"classroom" : "$_id.classroom",
				"difference" : "$_id.difference",
				"median_time_reaction": {"$round":["$avg_median_time_reaction",2]},
				"CA%": {"$round":["$avg_CA%",2]}
			}
		},
		{
			#not possible to merge on same table than aggregation
			"$out": "avg_decision"
		}
	]
	db = connect()
	db.avg_decision.remove({"subject": "numbers"})	
	if student is not None:
		pipeline[0] = {
			"$match": {"subject":"numbers", "student": student}
		}
		db.student_decision.aggregate(pipeline, allowDiskUse=True)
		records = db.avg_decision.find({"subject":"numbers","student":int(student)}, {"_id":0})
		for r in db.avg_decision.find({"subject":"numbers", "student": int(student)},{"_id":0}):
			db.student_decision.insert(r)
	else:
		db.student_decision.aggregate(pipeline, allowDiskUse=True)
		for r in db.avg_decision.find({"subject":"numbers"}, {"_id":0}):
			db.student_decision.insert(r)
	db.avg_decision.remove({"subject": "numbers"})


@timeit
def digital_decision_matrix(student=None):
	'''
	FROM student_digital_decision
	GROUP INTO MATRIX for a (student, subject, chapter)
	[diff, median_time_reaction, %CA]
	'''
	pipeline = [
		{
			"$match": {
				"subject": "numbers",
				"difference": {"$ne":None},
			}
		},
		{
			"$sort": { "student": 1,  "chapter":1, "difference":1} 
		},
		{
			"$group": {
				"_id": {
					"student": "$student",
					"classroom" : "$classroom",
					"subject": "$subject",
					"chapter": "$chapter"
				},
				"differences": {"$push": "$difference"},
				"median_time_reactions": {"$push": "$median_time_reaction"},
				"CA%s": {"$push": "$CA%"}
			}
		},
		{
			"$addFields":{
				"array": {"$zip": {"inputs":["$differences", "$median_time_reactions", "$CA%s"]}}
			}
		},
		{
			"$group": {
				"_id": {
					"student": "$_id.student",
					"classroom" : "$_id.classroom",
					"subject": "$_id.subject"
					
				},
				"arrays": {"$push": "$array"},
				"chapters": {"$push": "$_id.chapter"}
				
			}
		},
		{
			"$addFields": {
				"matrix": {
					"$zip": {"inputs": ["$chapters", "$arrays"]}
				}
			}
		},
		{
			"$project":{
				"_id":0,
				"student": "$_id.student",
				"classroom" : "$_id.classroom",
				"subject": "$_id.subject",
				"chapters": "$chapters",
				"matrix":"$matrix",
			}
		},
		{
			"$merge": "student_decision_matrix"
		}
	]
	db = connect()
	db.student_decision_matrix.remove({"subject":"numbers"})
	db.student_decision.aggregate(pipeline, allowDiskUse=True)


@timeit
def format_digital_matrix(student):
	"""
	Transform matrix [[[],[],[] ],[[],[],[] ]]
	into a graph
	"""
	db = connect()
	if student is None:
		records = list(db.student_decision_matrix.find({"subject": "numbers"}))
	else:
		records = list(db.student_decision_matrix.find({"student":int(student), "subject": "numbers"}))
	for record in records:
		graph = {}
		matrix = record["matrix"]
		xaxis = []
		yaxis = []
		chapters = {
			str(line[0]):
			{
				"series":[], 
				"xaxis": [],
				"yaxis": []
			}
				for line in matrix
			
		}
		for line in matrix:
			xaxis.extend([row[0] for row in line[1]])
			# yaxis.extend([row[1] for row in line[1]])
			chapters[str(line[0])]["series"] = [
				{
					"label": "Distance",
					"name": "Temps de réaction",
					"color": "blue",
					"x":[row[0] for row in line[1]],
					"y":[row[1] for row in line[1]],
					"z":[(row[0],row[1]) for row in line[1]] 
				}
			]

			chapters[str(line[0])]["xaxis"] = [row[0] for row in line[1]]
			chapters[str(line[0])]["yaxis"] = [row[1] for row in line[1]] 
						
		graph = {
			"subject": "numbers",
			"data": dict(sorted(chapters.items())), 
			"xaxis_label":"Distance entre les nombres", 
			"yaxis_label": "Temps médian de réaction(en sec.)",
			"title": "Reconnaissance des nombres et des quantités",
			"xaxis": sorted(list(set(xaxis))),
			# "yaxis": sorted(list(set(yaxis)))
			}
		db.student_decision_matrix.update({"_id": record["_id"]}, {"$set":{"graph": graph}})
			

def get_word_elapsedtime(student=None):
	'''
	FROM student_tag
	WHERE dataset = assessments_language AND GROUP != "guest"
	yield word info
	'''
	db = connect()
	# tags is need to determine the word type
	if "student_tag" not in db.list_collection_names():
		create_tag_tables(student)
	if student is None:
		records = db.student_tag.find({"dataset": "assessments_language", "group": {"$ne": "guest"}}, {"student": 1, "chapter": 1, "classroom": 1, "tag": 1, "records": 1}) 
	else:
		records = db.student_tag.find({"dataset": "assessments_language", "student": int(student), "group": {"$ne": "guest"}}, {"student": 1, "chapter": 1, "classroom": 1, "tag": 1, "records": 1})
	for l in records:
		is_word = db.path.find_one({"stimuli": l["tag"]}, {"type": 1, "chapter": 1})
		info = {
			"word": l["tag"],
			"nb_letters": len(l["tag"]),
			"type": is_word["type"],
			"chapter": is_word["chapter"],
			"student": l["student"],
			"classroom": l["classroom"],
			"elapsedTimes": [r["elapsedTime"] for r in l["records"] if r["score"] == 1],
		}
		yield info

@timeit
def lexical_decision(student=None):
	'''
	FROM student_tag
	WHERE dataset=Gapfill lang and group!="guest"
	GROUP by "student", "classroom", "chapter", "nb_letters", "type"
	compute mediantime
	MERGE INTO student_decision
	'''
	db = connect()
	# tags is need to determine the word type
	if "student_tag" not in db.list_collection_names(): 
		create_tag_tables()
	if "student_words" not in db.list_collection_names(): 
		create_words_tables()
	if	"student_syllabs" not in db.list_collection_names():
		create_syllabs_tables()
	# group by chapter and nb_letter and type
	keys = ["student", "classroom", "chapter", "nb_letters", "type"]
	grouper = itemgetter(*keys)
	keys.extend(["elapsedTimes", "median_time_reaction", "words", "subject"])
	for key, grp in itertools.groupby(sorted([n for n in get_word_elapsedtime(student)], key=grouper), grouper):
		elapsedTimes = []
		words = set()
		for n in grp:
			words.add(n["word"])
			elapsedTimes.extend(n["elapsedTimes"])

		if len(elapsedTimes) == 0:
			median_time_reaction = None
		elif len(elapsedTimes) == 1:
			median_time_reaction = elapsedTimes[0]
		else:
			median_time_reaction = statistics.median(elapsedTimes)
		values = list(key)+[elapsedTimes, median_time_reaction, list(words), "letters"]
		db.student_decision.insert(dict(zip(keys, values)))

@timeit
def avg_lexical_decision(student=None):
	'''
	FROM student_decision subject 'letters'
	COMPUTE AVERAGE chapter
	'''
	
	# FROM student_decision subject letters
	pipeline_letters = [
		{
			"$match": {"subject": "letters"}
		},
		{
			"$group": {
				"_id": {
					"student": "$student",
					"classroom" : "$classroom",
					"nb_letters" : "$nb_letters",
					"type" : "$type",
				},
				"time_reaction": {"$push": "$median_time_reaction"},
			}
		},
		
		{
			"$project": {
				"_id": 0,
				"subject": "letters",
				"chapter": "average",
				"student": "$_id.student",
				"classroom" : "$_id.classroom",
				"nb_letters" : "$_id.nb_letters",
				"type" : "$_id.type",
				"median_time_reaction": {"$avg":"$time_reaction"}
			}
		},
		{
			#not possible to merge on same table than aggregation
			"$out": "avg_decision"
		}
	]
	db = connect()
	if student is None:
		db.avg_decision.remove({"subject": "letters"})	
	else:
		pipeline_letters[0] = {
			"$match": {"subject": "letters","student":int(student)}
		} 
	db = connect()
	db.avg_decision.drop()	
	db.student_decision.aggregate(pipeline_letters, allowDiskUse=True)
	if student is not None:
		records = list(db.avg_decision.find({"student":int(student), "subject":"letters"}, {"_id":0}))
	else:
		records = list(db.avg_decision.find({"subject":"letters"}, {"_id":0}))
	if len(records) > 0:
		db.student_decision.insert_many(records)
	db.avg_decision.remove({"subject":"letters"})


@timeit
def lexical_decision_matrix(student=None):
	'''
	FROM student_lexical_decision
	GROUP INTO A MATRIX
	1.  ["$nb_letters", "$time_reactions"]
	2. ["$type"]
	3. ["chapter"]
	OUT student_decision_matrix
	'''
	pipeline_letters = [
		{
			"$match": {"subject": "letters"}
		},
		{
			"$sort": { "student": 1, "type":1, "chapter":1, "nb_letters":1} 

		},
		{
			"$group": {
				"_id": {
					"student": "$student",
					"classroom" : "$classroom",
					"type": "$type",
					"chapter" : "$chapter",
					"subject": "$subject"
				},			
				"nb_letters" : {"$push":"$nb_letters"},
				"time_reactions": {"$push": {"$round":["$median_time_reaction", 2]}},
			}
		},
		{
			"$addFields": {
				"array1": {"$zip": {"inputs": ["$nb_letters", "$time_reactions"]}}
			}
		},
		{
			"$group": {
				"_id": {
					"student": "$_id.student",
					"classroom" : "$_id.classroom",
					"chapter" : "$_id.chapter",
					"subject": "$_id.subject"
				},
				"nb_letters": {"$push": "$nb_letters"},
				"types": {"$push": "$_id.type"},
				"array1": {"$push":"$array1"},
				"median_time_reactions": {"$push": "$time_reactions"},
			}
		},
		{
			"$addFields": {
				"array2": {"$zip": {"inputs": ["$types", "$array1"]}}
			}
		},
		{
			"$group": {
				"_id": {
					"student": "$_id.student",
					"classroom" : "$_id.classroom",
					"subject": "$_id.subject"
				},
				"chapters": {"$push": "$_id.chapter"}, 
				"array2": {"$push": "$array2"},
				"types": {"$push": "$types"},
				"median_time_reactions": {"$push": "$median_time_reactions"},

			}
		},
		{
			"$addFields": {
				"matrix": {"$zip": {"inputs": ["$chapters", "$array2"]}},
			}
		},
		{
			"$project":{
				"_id":0,
				"student": "$_id.student",
				"classroom" : "$_id.classroom",
				"subject": "$_id.subject",
				# "nb_letters":  "$nb_letters",
				"matrix":"$matrix",
			}
		},
		{
			"$merge": "student_decision_matrix"
		}
	]
	if student is not None:
		pipeline_letters[0] = {
			"$match": {"subject": "letters", "student": int(student)}
		}
		db.student_decision_matrix.remove({"subject":"letters", "student":student})
		db.student_decision.aggregate(pipeline_letters, allowDiskUse=True)
		return
	else:
		db = connect()
		db.student_decision_matrix.remove({"subject":"letters"})
		db.student_decision.aggregate(pipeline_letters, allowDiskUse=True)
		return

@timeit
def format_lexical_matrix(student=None):
	'''
	transform RAW matrix into a graph ready
	'''
	db = connect()
	if student is None:
		records = list(db.student_decision_matrix.find({"subject": "letters"}))
	else:
		records = list(db.student_decision_matrix.find({"student":int(student), "subject": "letters"}))
	for record in records:
		graph = {}
		chapters = {str(line[0]): {"series":[], "xaxis":[]} for line in record["matrix"]}
		
		for line in record["matrix"]:
			chapter = str(line[0])
			chapter_xaxis = []
			for n in line[1]:
				
				if n[0] == "word":
					chapters[chapter]["series"].append(
						{
							"name":"Mot","label":"Mot", "color":"green",
							"y": [x[1] for x in n[1]],
							"x": [x[0] for x in n[1]],
							"z": [tuple(x) for x in n[1]], 
						# "series":[dict(zip(["x", "y"],x)) for x in n[1]]
						})
					chapter_xaxis.extend([x[0]for x in n[1]])
				elif n[0] == "pseudoword":
					chapters[chapter]["series"].append(
						{
							"name":"Pseudo-mot","label":"Pseudo Mot", "color":"red", 
							"y": [x[1] for x in n[1]],
							"x": [x[0] for x in n[1]],
							"z": [tuple(x) for x in n[1]], 
							# "series":[dict(zip(["x", "y"],x)) for x in n[1]]
						})
					chapter_xaxis.extend([x[0]for x in n[1]])
				else:
					chapters[chapter]["series"].append(
						{
							"name":n[0],
							"label":"Distance entre les deux nombres", "color":"blue", 
							"y": [x[1] for x in n[1]],
							"x": [x[0] for x in n[1]],
							"z": [list(x) for x in n[1]], 
							# "series":[dict(zip(["x", "y"],x)) for x in n[1]]
						})
					chapter_xaxis.extend([x[0]for x in n[1]])
			chapters[chapter]["xaxis"] = sorted(list(set(chapter_xaxis)))
			graph = {
					"subject": "letters",
					"data": dict(sorted(chapters.items())), 
					"xaxis_label":"Nombre de lettres", 
					"yaxis_label": "Vitesse de la lecture",
					"title": "Lecture des mots et des pseudomots"
					}
		db.student_decision_matrix.update({"_id": record["_id"]}, {"$set":{"graph": graph}})
	

	
@timeit
def create_lexical_decision(student=None):
	lexical_decision(student)
	avg_lexical_decision(student)
	lexical_decision_matrix(student)
	format_lexical_matrix(student)
	return

@timeit
def create_digital_decision(student=None):
	digital_decision(student)
	avg_digital_decision(student)
	digital_decision_matrix(student)
	format_digital_matrix(student)
	return

@timeit
def create_decision_tables(student=None):
	create_digital_decision(student)
	create_lexical_decision(student)	
	return True, ""
	
@timeit
def delete_decision_tables(student=None):
	db = connect()
	tables = ["student_decision", "student_decision_matrix"]
	if student is None:
		for t in tables:
			db.drop(t)
		return True, ""
	else:
		for t in tables:
			db[t].remove({"student": student})
		return True, ""
if __name__=="__main__":
	create_decision_tables()
	quit()