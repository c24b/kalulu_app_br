# from flask_restplus import Namespace, Resource, abort, fields
from flask_restx import Api, Resource, fields, abort, Namespace
from flask import request
import time
import itertools
from utils.db import connect
from utils import convert_datetime_to_str, convert_raw_data, get_lesson_nb



ns_activity = Namespace('activity', description='Consult activity on the game')
dataset_model = ns_activity.model('Dataset', {
	'dataset': fields.String(required=True, description="[gp, assessments_langage, assessments_maths, gapfill_lang, numbers]"),
	"subject" : fields.String(required=True, description="[numbers, letters]"),
	"type" : fields.String(required=False, description=["chapter", "lesson", "item"]),

})

subject_model = ns_activity.model('Subject', {
	'datasets': fields.List(fields.String, description='List of dataset', required=True, example="[gp, assessments_language, gapfill_lang]"),
	"subject" : fields.String(required=True, description = "A string included in [numbers, letters]", example="letters"),
	
})

student_dataset_model = ns_activity.model('StudentDataset', {
	'student': fields.Integer(required=True),
	'dataset': fields.String(required=True),
	
})

student_subject_model = ns_activity.model('StudentSubject', {
	'student': fields.Integer(required=True),
	'subject': fields.String(required=True),
	
})
classroom_dataset_model = ns_activity.model('ClassroomDataset', {
	'classroom': fields.Integer(required=True),
	'dataset': fields.String(required=True),
	
})

classroom_subject_model = ns_activity.model('ClassroomSubject', {
	'classroom': fields.Integer(required=True),
	'subject': fields.String(required=True),
	
})

@ns_activity.route("/datasets/<dataset>/")
class Dataset(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, dataset):
		"""
		Activity of all students on a dataset

		### Description
		
		Expose the table `student_dataset` 
		giving an activity overview 
		with nb_records, nb_days, nb_sequences(nb_tries), timespent (in sec)
		for all student that are not guest and selected dataset

		### Methods

		FROM student_dataset_day
		SORT by student, dataset, start
		Group by student and by dataset: 
			- days, sequences, first(start), last(end)
			- calculate nb_records, nb_days, nb_sequences, timespent(in sec.) 
		
		OUT into student_dataset 
  
		### Documentation
  
		Consult [activity documentation](http://doc.ludoeducation.fr/researcher-guide/activity/)
		"""
		db = connect()
		if dataset not in db.datasets.distinct("dataset"):
			return abort(406, "Le nom du dataset {} est incorrect.".format(dataset))
		if db.student_dataset.count_documents({}) == 0:
			return abort(500, "Table student_dataset is empty.")
		else:
			student_datasets = [n for n in db.student_dataset.find(
					{"dataset": dataset}, {"_id": 0, "records": 0})]
			if len(student_datasets) == 0:
				return abort(404, "Aucune donnée disponible pour le dataset {}.".format(dataset))
			activity = []
			for student_dataset in student_datasets:
				timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
				if student_dataset["subject"] == "letters":
					subject_name = "Français"
					student_dataset["subject_name"] = "Français"
				else:
					subject_name = "Maths"
					student_dataset["subject_name"] = "Maths"
				del student_dataset["start"]
				del student_dataset["end"]
				del student_dataset["sequences"]
				activity.append(student_dataset)
				
			return {
					"dataset": dataset,
					"type": "activity",
					"activity": activity,
					"doc": '''
					Aperçu de l'activité de l'ensemble des élève  sur le type de jeu (dataset) {} en {}: 
					nombre de jours,
					nombre d'essai, temps de jeu en secondes'''.format( dataset, subject_name)
				}

@ns_activity.route("/subjects/<subject>/")
class Subject(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, subject):
		"""
		Activity of all students on a dataset

		### Description
		
		Expose the table `student_subject` 
		giving an activity overview 
		with nb_records, nb_days, nb_sequences(nb_tries), timespent (in sec)
		for all student that are not guest and selected dataset

		### Methods

		FROM student_day
		SORT by student, subject, start
		Group by student and by subject: 
			- days, sequences, first(start), last(end)
			- calculate nb_records, nb_days, nb_sequences, timespent(in sec.) 
		
		OUT into student_subject

		"""
		db = connect()
		if subject not in db.datasets.distinct("subject"):
			return abort(406, "Le nom du sujet {} est incorrect.".format(subject))
		if db.student_subject.count_documents({}) == 0:
			return abort(500, "Table student_subject is empty.")
		else:
			student_subject = [n for n in db.student_subject.find(
					{"subject": subject}, {"_id": 0, "records": 0})]
			if len(student_subject) == 0:
				return abort(404, "Aucune donnée disponible pour le dataset {}.".format(subject))
			activity = []
			for student_dataset in student_subject:
				timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
				student_dataset["timespent"] = timespent
				if student_dataset["subject"] == "letters":
					student_dataset["subject_name"] = "Français"
				else:
					student_dataset["subject_name"] = "Name"
				activity.append(student_dataset)
				del student_dataset["start"]
				del student_dataset["end"]
				# del student_dataset["sequences"]
			return {
					"subject": subject,

					"type": "activity",
					"activity": activity,
					"doc": '''
					Aperçu de l'activité de l'ensemble des élève  en {}: 
					nombre de jours,
					nombre d'essai, temps de jeu en secondes'''.format(subject, student_dataset["subject_name"])
				}
# @ns_activity.expect(student_dataset_model)
@ns_activity.doc(params={
	'student': 'An integer between 111 and 60820',
	"dataset": "A dataset as included in the list [gp, numbers,gapfill_lang, assessments_language, assessments_maths]"
})
@ns_activity.route("/students/<student>/datasets/<dataset>/")
class StudentDataset(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, student, dataset):
		"""
		Activity of a student on a dataset

		### Description
		
		Expose the table `student_dataset` 
		giving an activity overview 
		with nb_records, nb_days, nb_sequences(nb_tries), timespent (in sec)
		for the selected student and selected dataset

		### Methods

		FROM student_dataset_day
		SORT by student, dataset, start
		Group by student and by dataset: 
			- days, sequences, first(start), last(end)
			- calculate nb_records, nb_days, nb_sequences, timespent(in sec.) 
		
		OUT into student_dataset 

		### Documentation
  
		Consult [activity documentation](http://doc.ludoeducation.fr/researcher-guide/activity/)
		
        """
		db = connect()
		try:
			student = int(student)
		except ValueError:
			return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
		if int(student) not in range(111, 60821):
			return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
		if int(student) not in db.students.distinct("student"):
			return abort(404, "L'élève {} n'a pas été trouvé.".format(student))
		if dataset not in db.datasets.distinct("dataset"):
			return abort(406, "Le nom du dataset {} est incorrect.".format(dataset))
		if db.student_dataset.count_documents({}) == 0:
			return abort(500, "Table student_dataset is empty.")
		else:
			student_dataset = db.student_dataset.find_one(
					{"student": student, "dataset": dataset}, {"_id": 0, "records": 0})
			if student_dataset is None:
				return abort(404, "Aucune donnée disponible pour l'élève {} et le dataset {}.".format(student, dataset))
			timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
			student_dataset["timespent_sec"] = student_dataset["timespent"]
			student_dataset["timespent"] = timespent
			if student_dataset["subject"] == "letters":
				subject = "letters"
				subject_name = "Français"
			else:
				subject = "numbers"
				subject_name = "Maths"
			del student_dataset["start"]
			del student_dataset["end"]
			del student_dataset["sequences"]
			del student_dataset["days"]
			# headers = ["nb_days", "nb_sequences", "nb_records", "start", "end", "timespent"]
			return {
					"student": int(student),
					"dataset": dataset,
					"classroom": student_dataset["classroom"],
					"subject": student_dataset["subject"],
					"subject_name": subject_name,
					"type": "activity",
					"activity": [student_dataset],
					"data": [student_dataset],
					"doc": '''
					Aperçu de l'activité de l'élève <code>{}</code> sur le type de jeu (dataset) {} en {}: 
					nombre de jours,
					nombre d'essai, temps de jeu en secondes'''.format(student, dataset, subject_name)
				}
			
			
# @ns_activity.expect(student_subject_model)
@ns_activity.doc(params={
	'student': 'An integer between 111 and 60820',
	"subject": "A subject as included in the list [letters, numbers]"
})
@ns_activity.route("/students/<student>/subjects/<subject>/")
class StudentSubject(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, student, subject):
		"""
		Activity of a student on a subject

		
		### Description
		
		Expose the table `student_subject` giving an activity overview of a student on a subject 
		with nb_records, nb_days, nb_sequences(nb_tries), timespent (in sec)
		
		### Methods

		Student_subject table is built upon student_dataset_day table         
		to compute records by student, dataset and day to get : 
			- the nb of sequences 
			- the timespent
			- the records
		aggregated by student and subject
		
        ### Documentation
  
		Consult [activity documentation](http://doc.ludoeducation.fr/researcher-guide/activity/)
		"""
		db = connect()
		if subject == "letters":
			subject_name = "Français"
		elif subject == "numbers":
			subject_name = "Maths"
		else:
			return abort(406, "Le nom du sujet {} est incorrect.".format(subject))
			
		try:
			student = int(student)
		except ValueError:
			return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
		if int(student) not in range(111, 60821):
			return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
		if int(student) not in db.students.distinct("student"):
			return abort(404, "L'élève {} n'a pas été trouvé.".format(student))
		if subject not in db.datasets.distinct("subject"):
			return abort(406, "Le nom du sujet {} est incorrect.".format(subject))
		if db.student_subject.count_documents({}) == 0:
			return abort(500, "Table student_subject is empty.")
		else:
			student_subject = db.student_subject.find_one(
					{"student": student, "subject": subject}, {"_id": 0, "records": 0})
			if student_subject is None:
				return abort(404, "Aucune donnée disponible pour l'élève {} en {}.".format(student, subject_name))
			
			timespent = time.strftime('%H:%M:%S', time.gmtime(student_subject["timespent"]))
			student_subject["timespent_sec"] = student_subject["timespent"]
			student_subject["timespent"] = timespent
			headers = ["nb_days", "nb_sequences", "nb_records", "start_date", "end_date", "timespent", "timespent_sec", "timespent_min", "timespent_by_dataset"]
			activity = {
				k: student_subject[k] for k in headers
			}
			del student_subject["start"]
			del student_subject["end"]
			# del student_subject["sequences"]
			
			return {
					"title": "Activité de l'élève {} en Français".format(student),
					"student": int(student),
					"classroom": student_subject["classroom"],
					"subject": student_subject["subject"],
					"subject_name": subject_name,
					"type": "activity",
					"activity": [activity],
					"data": [student_subject],
					"csv": "{}/csv".format(request.base_url),
					"doc": '''
					Aperçu de l'activité de l'élève {}  en {}: 
					nombre de jours,
					nombre d'essai, temps de jeu en secondes'''.format(student, subject_name)
				
				}

# @ns_activity.expect(student_subject_model)
@ns_activity.route("/students/<student>/subjects/<subject>/info")
class StudentSubjectInfo(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, student, subject):
		"""
		Global Activity information of a student given a subject 
		
		### Description

		 Expose the table `student_subject` with:
			- student 
			- subject
			- subject_name
			- start (YYYY-MM-DD HH:MM:SS)
			- end (YYYY-MM-DD HH:MM:SS)
			- timespent (in HH:MM:SS)
			- nb_days
			- nb_sequences
		Expose the table student_lessons with:
		- last lesson
		- last chapter
		Expose the table path 
		showing the last notions seen into the last lesson 
		### Documentation
  
		Consult [activity documentation](http://doc.ludoeducation.fr/researcher-guide/activity/)
  		"""
		db = connect()
		try:
			student = int(student)
		except ValueError:
			return abort(406, "L'identifiant de l' élève {} est incorrect.".format(student))

		if student not in range(111, 60821):
			return abort(406, "L'identifiant de l' élève {} est incorrect.".format(student))
			
		if student not in db.students.distinct("student"):
			return abort(404, "L'élève {} n'existe pas.".format(student))
		if subject not in ["letters", "numbers"]:
			return abort(406, "Le sujet {} est incorrect.".format(subject))
		
		if subject == "letters":
			subject_name = "Français"
			dataset = "gp"
		else:
			subject_name = "Maths"
			dataset = "numbers"
		if db.student_lessons.count() == 0:
			return abort(500, "Table student_lessons is empty.")
		
		student_lessons = db.student_lessons.find_one({"dataset": dataset, "student": int(student)}, {"_id":0, "lessons":0})
		if student_lessons is None:
			return abort(404, "Pas de données disponibles pour l'élève {} en {} .".format(student, subject_name))
		# timespent = sum(student_lessons["timespents"])
		# timespent = time.strftime('%H:%M:%S', time.gmtime(timespent))
		last_chapter = student_lessons["chapters"][-1]
		last_lesson = student_lessons["lesson_ids"][-1]
		chapter_color = student_lessons["chapter_colors"][-1]
		notions_path = set([n["tag"] for n in db.path.find({"lesson": last_lesson, "subject":subject})])
		print(notions_path, chapter_color)

		# lessons = list(db.student_lesson.find({"dataset": dataset, "student": int(student)}, {"nb_days":1}))
		# print([n["nb_days"] for n in lessons]) 
		# last_lesson = db.student_lesson.find_one({"dataset": dataset, "student": int(student), "lesson":last_lesson}, {"_id":0, "records":0})
		if db.student_subject.count() == 0:
			return abort(500, "Table student_subject is empty.")
		subject_stats = db.student_subject.find_one({"subject": subject, "student": int(student)}, {"records":0})
		if subject_stats is None:
			print("Warning: l.173 in namespaces/activity.py no data found in student_subject.find_one({'subject':{}, 'student':{}})".format(subject, int(student)))
			subject_stats = {"nb_days": None, "nb_sequences": None, "timespent": None}
		else:
			timespent = time.strftime('%H:%M:%S', time.gmtime(subject_stats["timespent"]))
			student_ids = db.students.find_one({"student": student})
		infos = {
			"title": "Activité de l'élève {} en {}".format(student, subject_name),
			"doc":'''
			Aperçu  général de l'activité en {} de l'élève n°{} sur la tablette n°{}, de la classe n°{}.

			'''.format(subject_name, student_ids["kid"], student_ids["tablet"], student_ids["classroom"]),
			"type": "activity",
			"subject": subject,
			"student": student, 
			"tablet": student_ids["tablet"],
			"kid": student_ids["kid"],
			"subject_name": subject_name,
			"tags": list(notions_path),
			"timespent": timespent,
			"chapter": last_chapter,
			"chapter_color": chapter_color,
			"lesson": last_lesson,
			"nb_days": subject_stats["nb_days"],
			"started_at": subject_stats["start_date"],
			"ended_at": subject_stats["end_date"],
			"nb_sequences": subject_stats["nb_sequences"],
			"timespent_sec": subject_stats["timespent"],
			# "timespent": timespent,
			"csv": "{}/csv".format(request.base_url),
			
		}
		return infos

# @ns_activity.expect(student_subject_model)
@ns_activity.route("/students/<student>/subjects/<subject>/last")
class StudentSubjectLast(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, student, subject):
		"""
		VIEW activity of a student on last chapter 
		
		### Description

		 Expose the `student_confusion` data on last chapter  with:
			- student 
			- subject
			- subject_name
			- chapter
		As chapter are cumulated : last activity is the result of what the student made during all the game

		### Documentation
  
		Consult activity documentation http://doc.ludoeducation.fr/researcher-guide/activity/
  
  		"""
		db = connect()
		try:
			student = int(student)
		except ValueError:
			return abort(406, "L'identifiant de l' élève {} est incorrect.".format(student))
		try:
			if student not in range(111, 60821):
				return abort(406, "L'identifiant de l' élève {} est incorrect.".format(student))
		except ValueError:
			return abort(406, "L'identifiant de l' élève {} est incorrect.".format(student))
		if student not in db.students.distinct("student"):
			return abort(404, "L'élève {} n'existe pas.".format(student))
		if subject not in ["letters", "numbers"]:
			return abort(406, "Le sujet {} est incorrect.".format(subject))
		
		if subject == "letters":
			subject_name = "Français"
			dataset = "gp"
		else:
			subject_name = "Maths"
			dataset = "numbers"
		student_chapters = db.student_chapters.find_one({"student":student, "subject": subject})
		# print(student_chapters["chapter_ids"])
		# student_chapters = db.student_chapter.distinct("chapter", {"student":student, "subject": subject})
		if student_chapters is None:
		# elif len(student_chapters) == 0:
			return abort(
				404, 
				"L'élève {} n'a pas encore joué en {}".format(student, subject_name), title="Dernière activité en {}".format(subject_name))
		student_last_chapter_id = sorted(student_chapters["chapter_ids"])[-1]
		student_last_lesson_id = sorted(student_chapters["lessons"])[-1]
		student_confusion = list(db.student_confusion.find({"subject": subject, "student": int(student), "chapter": student_last_chapter_id}, {"_id":0}))
		confusion = [(n["target"], n["stimulus"], n["WA_rate"]) for n in student_confusion if n["WA_rate"] is not None]
		if len(confusion) == 0:
			return abort(
				404, 
				"L'élève {} n'a pas encore joué en {}".format(student, subject_name), title="Dernière activité en {}".format(subject_name))
		x = []
		z = []
		markers = []
		colors = []
		for id, group in itertools.groupby(sorted(confusion, key=lambda x:get_lesson_nb(x[0])), key=lambda x: x[0]):
			scores = list(group)
			activity = [n for n in scores if n[2] is not None]
			if len(activity) > 0:
				average_score = sum([n[2] for n in activity]) / len(activity)
				if average_score < 0.75:
					colors.append("yellow")
					markers.append("star")
				else:
					colors.append("red")
					markers.append("cross")
				tag_confused = sorted([(n[1],n[2]) for n in activity], key=lambda x:x[-1], reverse=True)
				# print("tag", id, tag_confused)
				z.append([n[0] for n in tag_confused[:2]])
				x.append(id)
		if subject == "letters":
			title = "graphème-phonème"
			doc = '''
   	Détail de l’ensemble de l’activité “association graphème-phonème” dans le jardin courant (jardin {}).\n 
    \n
    Chaque icône représente une notion abordée:\n
	\t- Une étoile représente un taux de bonnes réponses > à 75%\n
	\t- Une croix représente un taux de bonnes réponses < à 75%\n
	En cliquant sur chaque icône, on voit s’afficher les deux graphèmes avec lesquels le graphème abordé a été le plus souvent confondu.
'''.format(student_last_chapter_id)
		else:
			title = "nombre"
			doc = '''
   	Détail de l’ensemble de l’activité “association nombres” dans le jardin courant (jardin {}).\n 
    \n
    Chaque icône représente une notion abordée:\n
	\t- Une étoile représente un taux de bonnes réponses > à 75%\n
	\t- Une croix représente un taux de bonnes réponses < à 75%\n
	En cliquant sur chaque icône, on voit s’afficher les deux chiffres avec lesquels le chiffre abordé a été le plus souvent confondu.
'''.format(student_last_chapter_id)
		y = [student for _ in x]
		activity = {}
		
		activity["title"] = "Maîtrise des correspondances "+title
		activity["xaxis"] = x
		activity["xaxis_label"] = "Défi"
		activity["yaxis"] = y
		activity["yaxis_label"] = "Elève"
		activity["zaxis"] = z
		activity["zaxis_label"] = "confondu avec"
		activity["legend"] = "Etoile jaune : moyenne de bonnes réponses < 75%, Croix rouge: > 75%"
		infos = {
			"type": "activity",
			"student": student, 
			"subject": subject,
			"subject_name": subject_name,
			"chapter": student_last_chapter_id,
			"title": activity["title"],
			"data": [{
				"x":x,
				"y":y,
				"z": z,
				"markers": markers,
				"colors": colors
			}],
			"activity": [activity],
			"csv": "{}/csv".format(request.base_url),
			"doc": doc
		}
		return infos



# # @ns_activity.expect(student_subject_model)
# @ns_activity.route("/students/<student>/subjects/<subject>/last_lesson")
# class StudentSubjectLastLesson(Resource):
# 	@ns_activity.response(200, 'Success')
# 	@ns_activity.response(404, 'No data')
# 	@ns_activity.response(406, "Incorrect parameter")
# 	@ns_activity.response(500, "Database Error")

# 	def get_last_lesson_confusion(student,dataset):
# 		'''
# 		Method for the API
# 		student 112 last lesson 'est' 
# 		tested over tag [a, e, ]
# 		'''
# 		db = connect()
# 		student_lessons = db.student_lessons.find_one({"student":student, "dataset": dataset})
# 		last_lesson = student_lessons["lessons"][-1]
# 		records = last_lesson["records"]
# 		tags = set([n["tag"] for n in records])
# 		lessons = sorted([(n["lesson"], n["tag"]) for n in [db.path.find_one({"tag":tag}, {"lesson":1, "tag":1}) for tag in tags]])
# 		tag_lesson = {t: l for l,t in lessons}
# 		confusion_records = [
# 					[
# 						n["target_tag"],
# 						n["stimulus_tag"],
# 						n["score"]
# 					]
# 					for n in records
# 					if n["target_tag"] != n["stimulus_tag"]
# 					if n["stimulus_tag"] is not None
# 				]
# 		print(confusion_records)
# 		confusion_list = []
# 		for target_stimulus, score in itertools.groupby(sorted(confusion_records), key=lambda x: (x[0], x[1])):
# 			scores = list(score)
# 			target, stimulus = target_stimulus
# 			score = [n[2] for n in scores]
# 			stimuli = [n[1] for n in scores]
# 			CA = round((len(score) - sum(score))/len(score), 2)
# 			confusion_list.append((target, stimulus, CA))
# 		last_lesson_confusion = []
# 		for target, score in itertools.groupby(confusion_list, key= lambda x: x[0]):
# 			last_lesson_confusion.append([target, sorted([(n[1], n[2]) for n in score])])
# 		sorted_last_lesson_confusion = sorted(last_lesson_confusion, key=lambda x: tag_lesson[x[0]])
# 		print(sorted_last_lesson_confusion)

# @ns_activity.expect(classroom_dataset_model)
@ns_activity.doc(
	params={
		'classroom': 'An integer between 1 and 60', 
		"dataset": "A string included in  the following list: 'numbers, gp, assessments_language, assessments_maths, gapfill_lang'"})
@ns_activity.route("/classrooms/<classroom>/datasets/<dataset>")
class ClassroomDataset(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, classroom, dataset):
		"""
		Global activity of one classroom on a selected dataset
		
		### Description
		
		Expose the table `student_dataset` giving an activity overview of a student, 
		with nb_records, nb_days, nb_sequences(nb_tries), timespent, CA, CA_rate
		
		### Methods

		- see the complete documentation on method
		
		`student_dataset` table         
		FROM student_dataset_day
		Compute records by student, dataset and day to get : 
			- the nb of sequences 
			- the timespent
			- the records
		"""
		db = connect()
		try:
			classroom = int(classroom)
		except ValueError:
			return abort(406, "L'identifiant de la classe {} est incorrect.".format(classroom))
		if classroom not in range(1, 61):
			return abort(406, "L'identifiant de la classe {} est incorrect.".format(classroom))
		if classroom not in db.students.distinct("classroom"):
			return abort(404, "La classe {} n'a pas été trouvée.".format(classroom))
		if dataset not in db.datasets.distinct("dataset"):
			return abort(406, "Le nom du dataset {} est incorrect.".format(dataset))
		if db.student_dataset.count() == 0:
			return abort(500, "La table {} est vide".format("student_dataset"))    
		student_datasets = list(db.student_dataset.find(
			{"classroom": classroom, "dataset": dataset}, 
			{ "records":0, "days":0, "sequences":0, "_id":0}))
		if len(student_datasets) == 0:
			return abort(404, "Pas de données disponible pour la classe {} sur le dataset {}.".format(classroom, dataset))
		
		headers = ["classroom", "subject", "group","student", "dataset", "start_date", "end_date", "timespent", "nb_sequences", "nb_days", "nb_records"]
		activity = [dict(zip(headers, [
			n["classroom"],
			n["subject"],
			n["group"],
			n["student"],
			n["dataset"],
			n["start"].strftime("%Y-%m-%d %H:%M:%S"),
			n["end"].strftime("%Y-%m-%d %H:%M:%S"), 
			time.strftime('%H:%M:%S', time.gmtime(n["timespent"])),
			n["nb_sequences"],
			n["nb_days"],
			n["nb_records"],
		])) for n in student_datasets]
		subject =  student_datasets[0]["subject"]
		if subject == "letters":
			subject_name = "Français"
		else:
			subject_name = "Maths"
		infos = {
			"type": "activity",
			"dataset": dataset,
			"subject": subject,
			"subject_name": subject_name,
			"classroom": classroom, 
			"data": activity,
			"activity": activity,
			"csv": "{}/csv".format(request.base_url),
			"doc": "Aperçu de l'activité de la classe  {} sur le type de jeu (dataset) {} en {}".format(classroom, dataset, subject_name)
		}
		return infos

@ns_activity.doc(
	params={
		'classroom': 'An integer between 1 and 60', 
		"subject": "A string included in  the following list: 'numbers, letters'"})
@ns_activity.route("/classrooms/<classroom>/subjects/<subject>")
class ClassroomSubject(Resource):
	@ns_activity.response(200, 'Success')
	@ns_activity.response(404, 'No data')
	@ns_activity.response(406, "Incorrect parameter")
	@ns_activity.response(500, "Database Error")
	def get(self, classroom, subject):
		"""
		VIEW activity of classsrom students on a subject 
		
		### Description
		
		Expose the table `student_subject` giving an activity overview of a student on a subject  
		with nb_records, nb_days, nb_sequences(nb_tries), timespent (in sec)
		filtered by classroom
		
		### Methods

		- see the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/activity.md#student_subject)
		
		`student_subject` table         

		Compute records by student, dataset  to get : 
			- the nb of sequences 
			- the timespent
			- the records
		
		"""
		
		db = connect()
		try:
			classroom = int(classroom)
		except ValueError:
			return abort(406, "L'identifiant de la classe {} est incorrect.".format(classroom))
		if classroom not in range(1, 61):
			return abort(406, "L'identifiant de la classe {} est incorrect.".format(classroom))
		if classroom not in db.students.distinct("classroom"):
			return abort(404, "La classe {} n'a pas été trouvée.")
		if subject not in ["numbers", "letters"]:
			return abort(406, "Le nom du sujet {} est incorrect.".format(subject))
		if db.student_dataset.count() == 0:
			return abort(500, "La table {} est vide".format("student_subject"))
		student_datasets = list(db.student_subject.find({"classroom": classroom, "subject": subject}, { "days":0, "records":0, "sequences":0, "_id":0,}))
		headers = ["classroom", "group","student", "datasets","subject","start", "end", "timespent", "nb_sequences", "nb_days", "nb_records"]
		activity = [
			dict(zip(headers, [
			n["classroom"],
			n["group"],
			n["student"],
			n["datasets"],
			n["subject"],
			n["start"].strftime("%Y-%m-%d %H:%M:%S"),
			n["end"].strftime("%Y-%m-%d %H:%M:%S"), 
			time.strftime('%H:%M:%S', time.gmtime(n["timespent"])),
			n["nb_sequences"],
			n["nb_days"],
			n["nb_records"]
			])) for n in student_datasets]

		if subject == "letters":
			subject_name= "Français"
		else:
			subject_name = "Maths"
		infos = {
			"type": "activity",
			"subject": subject,
			"subject_name": subject_name,
			"classroom": classroom, 
			"data": activity,
			"activity": activity,
			"csv": "{}/csv".format(request.base_url),
			"doc": '''
			Ce graphique représente la progression de chaque élève de la classe en {}:
			- les élèves sont ordonnés par numéro de tablette puis par identifiant (axe vertical)
			- chaque point correspond à une leçon completée (axe horizontal)
			- chaque leçon est colorée en fonction du score de bonne réponse par comparaison avec l'ensemble des scores de bonne réponses pour cette leçon</li> 
				
			La couleur de la leçon correspond au score de bonne réponse de l'élève par rapport 
			à l'ensemble des élèves (toute classe confonfue) ayant complété cette même leçon.
			
			-	Un point vert: le score de bonne réponse pour cette leçon est supérieur ou égal au score median pour cette leçon
			-	Un point orange: le score de bonne réponse pour cette leçon est inférieur au score median pour cette leçon
			-	Un point rouge: le score de bonne réponse pour cette leçon est deux fois inférieur au score median pour cette leçon
			
			Accédez au détail de l'élève en cliquant sur l'un des points qui lui correspond.
			'''.format(subject_name)
		}
		if len(student_datasets) > 0:
			return infos
		else:
			return abort(404, "Pas de données disponibles pour la  classe {} et le sujet {}.".format(classroom,subject))
