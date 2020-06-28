#!/usr/bin/python3
# encoding: utf-8

import itertools
import pymongo

from utils  import connect, close
from utils  import timeit, get_lesson_nb, get_CV
# from .chapter import create_chapter_tables


def build_item(student, chapter, subject, couple, CV="N"):
	title = ""
	if CV == "V":
		title = "Voyelles"
	elif CV == "C":
		title = "Consonnes"
	else:
		# elif CV is "N":
		title = "Nombres"
	return {
			"student": student,
			"chapter": chapter,
			"subject": subject,
			"CV": CV,
			"title": title,
			"target": couple[0],
			"stimulus": couple[1],
			"timespent": 0,
			"WA_rate": None,
			"CA_rate": None,
			"CA": None,
			"WA": None,
			"nb_records": 0
	}

@timeit
def filter_tags(student_tags, CV):
	if CV != "N":
		return [tag for tag in student_tags if get_CV(tag) == CV ]	
	else:
		return student_tags

# @timeit
def build_records(student):
	db = connect()
	#get the chapters and tags by subject for one student 
	subject_items = []
	for subject_dataset in [("letters","gp"),("numbers","numbers")]:
		subject, dataset = subject_dataset
		# how many chapters?
		chapters = db.student_chapters.find_one({"student":student, "subject": subject})
		if chapters is None:
			continue
		else:
			chapters = chapters["chapter_ids"]
			# how many tags? 
			tags = db.student_tag.distinct("tag", {"student": student, "dataset":dataset})
			# print(chapters, tags)
			if len(tags) != 0:
				# print(tags, chapters)
				if subject == "letters":
					C_tags = [tag for tag in tags if get_CV(tag) == "C" ]
					V_tags = [tag for tag in tags if get_CV(tag) == "V" ]
					# print(C_tags, V_tags)
					if len(V_tags) != 0 and len(C_tags) == 0:
						couples = [
							("V", list(itertools.product(V_tags, repeat=2)))
						]
					elif len(C_tags) != 0 and len(V_tags) == 0:
						couples = [
							("C", list(itertools.product(V_tags, repeat=2)))
						]
					else:
						couples = [
							("V", list(itertools.product(V_tags, repeat=2))), 
							("C", list(itertools.product(C_tags, repeat=2)))
						]
				else:		
					if len(tags) > 0:
						couples = [
							("N", list(itertools.product(tags, repeat=2)))
						]
			for block in couples:
				CV, combos = block
				db.student_confusion.insert_many([
					build_item(student, chapter, subject, couple, CV) 
						for chapter in chapters for couple in combos
				])
				

@timeit
def fill_student_confusion(student=None):
	db = connect()
	db.student_confusion.drop()
	if student is None:
		for student in db.students.distinct("student", {"group":{"$nin":["guest", "None"]}}):
			build_records(student)	
		return	
	else:
		db.student_confusion.remove({"student":student})
		build_records(student)
			
@timeit
def insert_student_confusion(student=None):
	'''
	FROM student_chapter
	INSERT into student_confusion TABLE
	where all the possibilities previously generated manually
	UNWIND all records 
	IF stimulus is not None
	WHEN document.target matches the  target, stimulus, student, chapter, subject, CV
	UDPATE arrays (push) score, elapsedTime 
	SUM nb_records, score (to CA)
	UDPATE set lesson to lessons set (unique)
	CALCULATE WA
	'''
	### IF STIMULUS is set to '' and target = 'a'
	### we assumed that if score is set to 1 he correctly avoided it
	### And 0 that he didn't recognize it
	### DO WE HAVE TO INCLUDE IT INTO confusion replacing '' by the target
	### To get a more realistic state of recognition (a better CA) for the tag?
	# OR DO WE CONSIDER AS an touch error?
	# print("Insert confusion")
	pipeline = [
		{
			"$unwind": "$records"
		},
		{
			"$match": {
				"records.CV": {"$in": ["C", "V", "N"]},
				"records.stimulus_tag": {"$ne": None},		
			}
		},
		{
			"$group": {
				"_id": {
					"student": "$student",
					"dataset": "$dataset",
					"chapter": "$chapter",
					"subject": "$subject",
					"target": "$records.target_tag",
					"stimulus": "$records.stimulus_tag",
					"CV": "$records.CV", 
				},
				"timespent": {"$push":
							  {"$cond": [
								  {"$ne": ["$records.elapsedTime", -1]},
								  "$records.elapsedTime",
								  0
							  ]}},
				"nb_records": {"$sum": 1},
				"CA": {"$sum": "$records.score"},
			}
		},
		{
			"$addFields": {
				"WA": {"$subtract": [{"$sum": 1},{"$sum": "$records.score"}]}},
			
		},
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"dataset": "$_id.dataset",
				"chapter": "$_id.chapter",
				"CV": "$_id.CV",
				"subject": "$_id.subject",
				"target": "$_id.target",
				"stimulus": "$_id.stimulus",
				"timespent": {"$sum": "$timespent"},
				"nb_records": "$nb_records",
				"CA": "$CA",
				"WA": "$WA",
				"WA_rate": {"$round":[{"$divide": ["$WA", "$nb_records"]}, 2]},
				"CA_rate": {"$round":[{"$divide": ["$CA", "$nb_records"]}, 2] },
			}
		},
		{
			"$merge": {
				"into": "student_confusion",
				"on": ["student", "chapter", "subject", "target", "stimulus", "CV"],
				"whenMatched": "replace",
				"whenNotMatched": "insert" 
				}
		}
	]
	db = connect()
		
	if student is not None:
		pipeline.insert(0, {"$match":{"student":int(student)}})
	try:
		db.student_chapter.aggregate(pipeline, allowDiskUse=True)
	except pymongo.errors.DuplicateKeyError:
		pass
	except pymongo.errors.OperationFailure:
		db.student_chapter.aggregate(pipeline, allowDiskUse=True)
	#FIX  small correction for records from 
	# student 351 and student 1461
	# WHERE target and stimulus have not the same type
	db.student_confusion.remove({"target":"q", "stimulus":"a"})
	db.student_confusion.remove({"target":"l", "stimulus":"a"})
	
@timeit
def create_student_confusion_matrix(student=None):
	'''
	Create the matrix needed for the heatmap
	where matrix will be: 
	
	[y, [(x, WA), (x, WA), (x, WA)]]
	[y, [(x, WA), (x, WA), (x, WA)]]
	[y, [(x, WA), (x, WA), (x, WA)]]
	
	such as:

	[target, [(stimulus, WA), (stimulus, WA), (stimulus, WA)]]
	[target, [(stimulus, WA), (stimulus, WA), (stimulus, WA)]]
	[target, [(stimulus, CA), (stimulus, WA), (stimulus, WA)]]
	
	FROM student_confusion
	GROUP by student, dataset, classroom, CV, stimulus,
	SET targets  as [target, target, target, ...]
	SET WA_rate  as [WA, WA, WA, ...]
	ZIP (target, WA_rate) into `arrays` such as 
		[(target, WA), (target, WA),(target, WA),(target, WA),...] 
	GROUP by student, dataset, classroom, CV
	SET stimuli as [stimulus, stimulus, stimulus, ...]
	ZIP (stimuli, arrays) into `matrix` such as 
	[
		[stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]],
		[stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]]
		[stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]]
	]

	'''
	# LETTERS
	pipeline = [
		{
			"$match":{
				"stimulus": {"$ne":None},
				"CV": {"$ne": "NA"}
				}
		},
		{
			# first group by stimulus and chapter
			"$group": {
				"_id": {
					"student": "$student",
					"classroom": "$classroom",
					"subject": "$subject",
					"chapter": "$chapter",
					"stimulus": "$stimulus",
					"CV": "$CV"
				},
				# push targets (yaxis)
				"targets": {"$push": "$target"},
				# "timespent": {"$push": "$timespent"},
				"WA_rate": {"$push": "$WA_rate"},
				# "CA_rate": {"$push": "$CA_rate"},
				# "nb_records": {"$push": "$nb_records"}
			}
		},
		{
			# concatenate the arrays with targets and corresponding $WA_rate
			# to build y_axis
			# (target, WA, target_WA)
			"$addFields": {
				"arrays": {
					"$zip": {
						"inputs": ["$targets", "$WA_rate"] 
						#"$CA_rate", "$nb_records", "$timespent"]
					}
				}
			}
		},
		{
			# then push stimuli 
			# to build y_axis
			"$group": {
				"_id": {
					"student": "$_id.student",
					"classroom": "$_id.classroom",
					"subject": "$_id.subject",
					"chapter": "$_id.chapter",
					"CV": "$_id.CV"
				},
				"stimuli": {"$push": "$_id.stimulus"},
				"arrays": {"$push": "$arrays"},
				# "targets": {"$push": "$targets"},
				# "timespent": {"$push": "$timespent"},
				# "CA_rate": {"$push": "$CA_rate"},
				# "nb_records": {"$push": "$nb_records"},
				# "WA_rate": {"$push": "$WA_rate"},
				# "CA_rate": {"$push": "$CA_rate"},
				# "nb_records": {"$push": "$nb_records"}
			}
		},
		{
			# concatenate stimuli with arrays(target, WA, CA, nb_records, timespent) into matrix
			# [a, [[a,WA,CA,nb,timespent],[...]]
			"$addFields": {
				"matrix": {
					"$zip": {
						"inputs": ["$stimuli", "$arrays"]
					}
				}
			}
		},
		{
			"$project": {
				"_id": 0,
				"student": "$_id.student",
				"classroom": "$_id.classroom",
				"subject": "$_id.subject",
				"chapter": "$_id.chapter",
				"CV": "$_id.CV",
				"matrix": "$matrix",
				"y_axis": "$stimuli",
				"x_axis": "$stimuli"
				# "WA_rates": "$WA_rate",
				# "CA_rates": "$CA_rate",
				# "nb_records": "$nb_records",
				# "timespent": "$timespent"
			}
		},
		{
			"$out": "student_confusion_matrix"
		}
	]
	db = connect()
	if student is None:
		db.student_confusion_matrix.drop()
	else:
		db.student_confusion_matrix.remove({"student": student})
		pipeline.insert(0,{
			"$match": {
				"student": int(student)
				}
		})
	try:
		db.student_confusion.aggregate(pipeline, allowDiskUse=True)
	except pymongo.errors.DuplicateKeyError:
		pass
	# Format: sort axis and round value
	# print("Sort matrix axis and round values")
	if student is None:
		records = db.student_confusion_matrix.find()
	else:
		 records = db.student_confusion_matrix.find({"student":int(student)})
	for n in records:
		new_matrix = []
		for line in sorted(n["matrix"], key=lambda l: get_lesson_nb(l[0])):
			#line = [x, [(y, WA),(y, WA), ]]
			target = line[0]
			lesson_t = get_lesson_nb(target)
			new_cells = []
			# print(target, line[1])
			cells =  sorted(line[1], key=lambda c: get_lesson_nb(c[0]))
			new_cells = []
			for c in cells:
				if c[1] is not None:
					new_cells.append([c[0], round(c[1],2)])
				else:
					new_cells.append([c[0], c[1]])
			new_matrix.append([target, new_cells])
		x_axis = [n[0] for n in new_matrix]
		y_axis = [x[0] for x in [n[1] for n in new_matrix][0]]
		# print(y_axis)
		db.student_confusion_matrix.update_one(
			{"_id": n["_id"]}, 
			{
				"$set": {
					"matrix": new_matrix, 
					"xaxis_label":"distracteur", 
					"yaxis_label": "cible", 
					"xaxis": x_axis, 
					"yaxis": x_axis
					}
			}
		)

@timeit
def create_confusion():
	db = connect()
	db.confusion.drop()
	#insert
	# for couple in itertools.product(db.path.distinct("tag", {"dataset": "numbers"}, repeat=2):
	
	# V_tags = list(itertools.product([tag["tag"] for tag in db.path.find({"dataset": "gp"}) if tag["CV"] == "V"], repeat=2)
	# C_tags = itertools.product([tag["tag"] for tag in db.path.find({"dataset": "gp"}) if tag["CV"] == "C"], repeat=2)
	
	# get the students
	students = db.student_confusion.distinct("student")
	# get the last_chapter by student and by subject
	for student in students:
		for subject in ["letters", "numbers"]:
			  
			chapters = db.student_chapters.find_one({"student":student, "subject":subject})
			if chapters is not None:
			# student_subject_chapters = sorted(db.student_chapter.distinct("chapter", {"student":student, "subject":subject}))
			# # insert if exists
			# if len(student_subject_chapters) > 0:
				student_last_chapter = chapters["chapter_ids"][-1]
				last_confusion = list(db.student_confusion.find({"student": student,"subject": subject, "chapter": student_last_chapter}, {"_id":0}))
				db.confusion.insert_many(last_confusion)
	# group records (stimulus, target, score) over the students
	
	pipeline = [

		{
			# first group by subject and (stimulus, target) + CV (not a filter) 
			"$group": {
				"_id": {
					"subject": "$subject",
					"stimulus": "$stimulus",
					"target": "$target",
					"CV": "$CV",
				},
				"avg_WA_rate": {"$avg": "$WA_rate"},
				"avg_CA_rate": {"$avg": "$CA_rate"},
				"avg_timespent": {"$avg": "$timespent"},
				"avg_nb_records": {"$avg": "$nb_records"}
			}
		},
		{
			"$project": {
				"_id":0,
				"subject": "$_id.subject",
				"stimulus": "$_id.stimulus",
				"CV": "$_id.CV",
				"target": "$_id.target",
				"avg_WA_rate": "$avg_WA_rate",
				"avg_CA_rate": "$avg_CA_rate",
				"avg_timespent": "$avg_timespent",
				"avg_nb_records": "$avg_nb_records",
			}
		},
		{"$out": "confusion"}
	]
	db.confusion.aggregate(pipeline, allowDiskUse=True)
	
def create_confusion_matrix():
	pipeline = [
		{
			# first group by subject, stimulus (and CV not a filter) 
			"$group": {
				"_id": {
					"subject": "$subject",
					"stimulus": "$stimulus",
					"CV": "$CV"
				},
				"targets": {"$push":"$target"},
				"avg_WA_rate": {"$push": "$avg_WA_rate"},
				
			}
		},
		{
			# concatenate the arrays with targets and corresponding $WA_rate
			# to build y_axis
			# (target, WA, target_WA)
			"$addFields": {
				"arrays": {
					"$zip": {
						"inputs": ["$targets", "$avg_WA_rate"] 
						#"$CA_rate", "$nb_records", "$timespent"]
					}
				}
			}
		},
		{
			# then push stimuli 
			# to build y_axis
			"$group": {
				"_id": {
					"subject": "$_id.subject",
					"CV": "$_id.CV"
				},
				"stimuli": {"$push": "$_id.stimulus"},
				"arrays": {"$push": "$arrays"},
				# "targets": {"$push": "$targets"},
				# "timespent": {"$push": "$timespent"},
				# "CA_rate": {"$push": "$CA_rate"},
				# "nb_records": {"$push": "$nb_records"},
				# "WA_rate": {"$push": "$WA_rate"},
				# "CA_rate": {"$push": "$CA_rate"},
				# "nb_records": {"$push": "$nb_records"}
			}
		},
		{
			# concatenate stimuli with arrays(target, WA, CA, nb_records, timespent) into matrix
			# [a, [[a,WA,CA,nb,timespent],[...]]
			"$addFields": {
				"matrix": {
					"$zip": {
						"inputs": ["$stimuli", "$arrays"]
					}
				}
			}
		},
		{
			"$project": {
				"_id": 0,
				"subject": "$_id.subject",
				"dataset": "$_id.dataset",
				"CV": "$_id.CV",
				"matrix": "$matrix",
				"y_axis": "$stimuli",
				"x_axis": "$stimuli"
				# "WA_rates": "$WA_rate",
				# "CA_rates": "$CA_rate",
				# "nb_records": "$nb_records",
				# "timespent": "$timespent"
			}
		},
		
		{
			"$out": "confusion_matrix"
		}
	]
	db = connect()
	db.confusion_matrix.drop()
	db.confusion.aggregate(pipeline, allowDiskUse=True)
	# Format: sort axis and round value
	# print("Sort matrix axis and round values")
	for n in db.confusion_matrix.find():
		new_matrix = []
		for line in sorted(n["matrix"], key=lambda l: get_lesson_nb(l[0])):
			# print(line)
			#line = [x, [(y, WA),(y, WA), ]]
			target = line[0]
			lesson_t = get_lesson_nb(target)
			new_cells = []
			cells =  sorted(line[1], key=lambda c: get_lesson_nb(c[0]))
			new_cells = []
			# print(cells)
			for c in cells:
				
				if c[1] is not None:
					new_cells.append([c[0], round(c[1],2)])
				else:
					new_cells.append([c[0], c[1]])
			new_matrix.append([target, new_cells])
		x_axis = [n[0] for n in new_matrix]
		y_axis = [x[0] for x in [n[1] for n in new_matrix][0]]
		
		db.confusion_matrix.update_one(
			{"_id": n["_id"]}, 
			{
				"$set": {
					"matrix": new_matrix, 
					"xaxis_label":"Valeur proposée", 
					"yaxis_label": "Cible", 
					"xaxis": x_axis, 
					"yaxis": x_axis
					}
			}
		)
    
@timeit		
def create_student_confusion(student=None):
	db = connect()
	if student is None:
		db.student_confusion.drop()
		db.student_confusion.drop_indexes()
		fill_student_confusion(student)
		db.student_confusion.create_index(
			[("student", 1), ("chapter", 1),("subject",1), ("target", 1), ("stimulus", 1), ("CV", 1)],  unique=True)
		# create index to get next merge aggregation functionnal
		# db.student_confusion.create_index(
		# 	[("student", 1), ("chapter", 1),("subject",1), ("target", 1), ("stimulus", 1)],  unique=True)
	
		insert_student_confusion(student)
		return
	else:
		fill_student_confusion(student)
		db.student_confusion.drop_indexes()
		db.student_confusion.create_index(
			[("student", 1), ("chapter", 1),("subject",1), ("target", 1),("stimulus", 1), ("CV", 1)],  unique=True)
		insert_student_confusion(student)
		return

def delete_student_confusion(student=None):
	db = connect()
	if student is None:
		return db.student_confusion.drop()
	else:
		return db.student_confusion.delete_many({"student":student})

def delete_student_confusion_matrix(student=None):
	db = connect()
	if student is None:
		return db.student_confusion_matrix.drop()
	else:
		return db.student_confusion_matrix.delete_many({"student":student})

@timeit
def create_confusion_tables(student=None):
	create_student_confusion(student)
	create_student_confusion_matrix(student)
	create_confusion()
	create_confusion_matrix()
	return True, ""
@timeit
def delete_confusion_tables(student=None):
	db = connect()
	delete_student_confusion(student)
	delete_student_confusion_matrix(student)
	if student is None:
		db.confusion.drop()
		db.confusion_matrix.drop()
		return
	else:
		create_confusion()
		create_confusion_matrix()
	return True, ""	

if __name__ == "__main__":
	create_confusion_tables()
	quit()
	
