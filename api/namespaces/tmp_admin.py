from __future__ import absolute_import

import os
import subprocess
from flask import current_app

from flask import request, Response
from flask_restplus import Namespace, Resource, abort,fields

from functools import wraps
from flask import request


from settings.api import TOKEN
from settings.files import REFERENCES_FILES

from utils.db import connect
from utils.db import dbtable_to_csvfile

# from celery.task.control import inspect
# from itertools import chain


ns_admin = Namespace('admin', description='Administrative tasks and operations')


students_group = ns_admin.model("StudentsGroup", {
	"group": fields.String(required=True, example="r/m", description="A string in ['guest','r/m','m/r', None]"),
	"students": fields.String(required=True, example="3931,3926,3976,745", decription="A string listing the student ids with a coma as separator")
})


group_model = ns_admin.model('Group', {
'group': fields.String(required=True, description="A string in ['guest','r/m','m/r', None]", example="r/m")
})



def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'X-API-KEY' in request.headers:
			token =request.headers["X-API-KEY"]
		if not token:
			return {"message": "Token is missing."}, 401
		if token != TOKEN:
			return {"message": "Invalid Token"}, 401
		return f(*args, **kwargs)
	return decorated



def update_student_group(student, old_group, new_group):
	'''
	UPDATE student group
	- update students TABLE with group
	- background job of updating stats for one student
	- prepare response
	'''
	db = connect()
	code = 204
	msg = "Group for student '{}' has been successfully updated to {}".format(student, new_group)

	if new_group == old_group:
		code = 406
		msg = "Group for student {} is already set to `{}`".format(student, old_group)
		# logging.info(msg)
		return False, {"code":code, "message":msg}
		
	elif old_group is not None and new_group == "guest":
		'''
		if group is now guest and was r/m or m/r 
		=> delete corresponding stats
		stats(delete, student)
		'''
		print("Calling update_stats")
		result = current_app.celery.send_task('celery_tasks.update_stats',args=["delete",int(student)])
		print("Sent to celery")

	elif old_group is None and new_group == "guest":
		'''
		old_group None not in stats and new_group guest not in stats
		=> do nothing
		'''
		pass
	elif old_group in ["r/m", "m/r"] and new_group in ["m/r", "r/m"]:
		'''
		old_group is m/r or m/r in stats and new_group r/m mr in stats
		=> do nothing
		'''
		pass
	else:
		'''
		student create stats
		'''
		print("Calling update_stats")
		result = current_app.celery.send_task('celery_tasks.update_stats',args=["create",int(student)])
		print("Sent to celery")
	db.students.update({"student":student},{"$set":{"group": new_group}})
	#update status for all students
	db.students.update({"group":{"$ne":None}, "files_nb":{"$gt":0}}, {"$set": {"status": True}})
	dbtable_to_csvfile(REFERENCES_FILES["students"][0], table_name="students")
	return True, {"code":code, "message": msg}


@ns_admin.route("/classrooms")
class ClassroomList(Resource):
	def get(self):
		"""
		VIEW classrooms list
		
		## Method
		
		Classroom are stored in `students` table
		
		"""
		db = connect()	
		classrooms = db.students.distinct("classroom")
		
		if len(classrooms) == 0:
			return abort(404, "No classroom found.")
		classroom_records = []
		for classroom in classrooms:
			students = list(db.students.find({"classroom": classroom}, {"student":1, "status":1, "files_nb":1, "group": 1}))
			classroom_status = all(db.students.distinct("status", {"classroom": classroom})) 
			classroom_groups = db.students.distinct("group", {"classroom": classroom})
			files_nb = sum([x["files_nb"] for x in list(db.students.find({"classroom": classroom}, {"files_nb":1}))])
			classroom_records.append(
				{
					"classroom": classroom, 
					"status": classroom_status,
					"files_nb": files_nb,
					"groups": classroom_groups,
					"students":students
				}
			)
		return {"classrooms": classroom_records, "count": len(classroom_records)}, 200 

@ns_admin.doc(params={'classroom': 'An integer between 1 and 60'})
@ns_admin.route("/classrooms/<classroom>")
class Classroom(Resource):
    def get(self, classroom):
		"""
		VIEW classroom  
		
		## Method
		
		Providing argument classroom
		Classroom are stored in `students` table
		
		"""
		
		students = list(db.students.find({"classroom": int(classroom)}))
		# classroms = set([n["classroom"], n["group"] for n in classroom])
		
		# groups = set([n["group"] for n in classrom])
		if len(students) != 0:
			return abort(404, "no classroom `{}` found".format(classroom))
		return {"classrooms": students}, 200 
	
	@ns_admin.doc(security='apikey')    
	@token_required
	@ns_admin.expect(group_model, validate=True)
	def put(self, classroom):
		"""
		UPDATE classroom `group`
		
		## Method

		Classroom is stored in `students` table
		Providing `classroom` as a parameter 
		and data as following 
		{
			"group": "guest"
		} 
		
		will update 'group' for each student belonging to classroom 
		inside students tables 
		and update stats for each student and globally
		"""
		classroom = int(classroom)
		group = request.json["group"]
		counter = 0 
		db = connect()
		student_count = db.students.count({"classroom": classroom})
		status = True
		for student in db.students.find({"classroom": classroom}, {"student":1, "group":1}):
			existing_group = student["group"]
			status, response = update_student_group(student["student"], existing_group, group)
			if status is True:
				counter += 1
				
			else:
				code = response["code"]
				msg = response["msg"]
		if counter == 0:
			return abort(code[-1], msg)
		else:
			msg = "Group successfully updated to `{}` for classroom {}: {}/{} students updated".format(group, classroom, counter, student_count)
			return msg, 204  
@ns_admin.route("/students")
class Students(Resource):
	def get(self):
		''' 
		VIEW students 
		
		## Method
		
		Access to table students

		'''
		if db.students.count() == 0:
			return abort(500, "Table `students` is empty")
		else:
			return {"students":list(db.students.find())}, 200
	
	@ns_admin.doc(security='apikey')
	@token_required
	@ns_admin.expect(students_group, validate=True)
	def put(self):
		''' Update `group` for students
		
		## Methods

		Edit payload as shown in example

		Change the group for a list of students separated by `,`
		data = {"group": "r/m", "students":"2626,745,802,985,3972"}
		
		'''
		db = connect()
		group = request.json["group"]
		students = request.json["students"]
		student_ids = [n.strip() for n in students.split(",")]
		student_count = len(student_ids)
		counter = 0
		codes = []
		msgs = [] 
		for student in student_ids:
			try:
				student = int(student)
			except Exception as e:
				#partial response? No
				status = False
				msg = "Student {} is a incorrect, id must be integer.".format(student)
				codes.append(406)
				msgs.append(msg)
				continue
			existing_student = db.students.find_one({"_id": student}, {"group":1})
			if existing_student is None:
				status = False
				msg = "student {} doesn't exist.".format(student)
				codes.append(406)
				msgs.append(msg)
				continue
			else:
				status, response = update_student_group(student, existing_student["group"], group)
				codes.append(response["code"])
				msgs.append(response["msg"])
				if status is True:
					counter += 1		
		if counter > 0:
			msg = "Group successfully updated to `{}` for {}/{} students: {}".format(group, counter, student_count, student_ids)
			return {"code": 204, "message": msg}, 204
		else:
			return abort(codes[-1], {"code": codes[-1], "message": ", ".join(msgs)})

@ns_admin.route("/students/<student>")
class Student(Resource):
	def get(self, student):
		"""
		VIEW student item
		providing parameters `student`

		## Method

		Expose `student` item from [`students` table](../docs/students.md)
		
		"""
		if int(student) not in range(110, 60820):
			return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
		if int(student) not in db.students.distinct("student"):
			return abort(404, "L'élève n'a pas été trouvé")
		student_line = db.students.find_one({"_id": int(student)})
		if student_line is  not None:
			return {"data":student_line, "student":int(student)}
		else:
			return abort(404, "Aucune donnée disponible pour cet élève pour ce dataset")
	
	@ns_admin.expect(group_model, validate=True)
	@token_required
	@ns_admin.doc(security='apikey')
	def put(self, student):
		'''
		UPDATE student `group`

		## Method

		Student is stored in `students` table
		Providing `student` parameters 
		and editing group value in payload
		{
			group:"r/m"
		}
		will update the group for the student  
		and regenerate the stats using update_student_group()
		'''
		db = connect()
		group = request.json["group"]
		if group not in db.students.distinct("group"):
			return abort(406, "Group {} is not accepted".format(group))
		existing_student = db.students.find_one({"student": int(student)})
		if existing_student is None:
			return abort(404, "Student {} not found".format(student))
		else:
			status, response = update_student_group(student,existing_student["group"], group)
			if status is False:
				return abort(response['code'], response["msg"])
			else:
				return response, 204 
@ns_admin.doc({
	"status":"A string expressing status in list [True, true, False, false, missing, empty]"})
@ns_admin.route("/students/status/<status>")
class StudentStatus(Resource):
	def get(self, status):
		'''
		VIEW students with a specific status 
		
		## Description
		
		`status` parameters can be:
			- True true
			- False false
			- 'missing' status is False group is missing
			- 'empty' status is False no file for this student
		
		
		## Method
		
		expose the table `students` WHERE student.status == status
		
		status is `False`: 
		- when student has group and no file corresponds to `empty`: 
		
		student has been declared but no corresponding files have been found
		
		- when student has files and no group corresponds to `missing`: 
		
		student has not been declared 
		
		raise 404 if no students with corresponding status has been found  
		 
		'''
		
		if status == "missing":
			status = False
			group = None
			students = list(db.students.find({"status": status, "group":None}))
		elif status == "empty":
			status = False
			files_nb = 0
			students = list(db.students.find({"status": status, "files_nb":0}))

		elif status in ["True", "true", "OK", "correct"]:
			status = True
			students = list(db.students.find({"status": status}))
		elif status in ["False", "false", "bug", "error","wrong", "incorrect"]:
			status = False
			students = list(db.students.find({"status": status}))
		else:
			return abort(406, "Status {} is not supported".format(status))
		
		if len(students) > 0:
			return {"students":students, "count": len(students)}, 200
		else:
			return abort(404, "No student with status {} has been found.".format(status))
	
@ns_admin.doc({"group":"A string expressing status in list ['r/m', 'm/r', 'guest', None]"})
# @ns_admin.expect(status_model, validate=True)
@ns_admin.route("/students/groups/<group>")
class StudentGroup(Resource):
	def get(self, group):
		'''
		VIEW students belonging to a specific group 
		
		## Description
		
		`group` parameters can be:
			- r/m
			- m/r
			- guest
			- None
		
		
		## Method
		
		expose the table `students` WHERE student.group == group
		
		- group is `None` when student has no group declared: he is missing  
		- group is `guest` when student has been removed from statistics
		- group is `r/m` when student has begun by reading and then maths
		- group is `m/r` when student has begun by maths and then reading
		
		raise 404 if no students with corresponding status has been found  
		raise 406 if group not in the list
		'''
		# print(db.students.distinct("group")) 
		if group == "None" or group == "null":
			group = None
		if group not in db.students.distinct("group"):
			abort(406, "Group `{}` doesn't exists and is not accepted")
		else:
			students = list(db.students.find({"group":group}))
		
		if len(students) > 0:
			return {"students":students, "count": len(students)}
		else:
			return abort(404, "No student with status {} has been found.".format(status))



# @ns_admin.route("/lessons")
# class LessonsList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the lessons defined in the game

#         ### Description
		
#         Expose the table `path`  
#         giving the list of lessons when declared in path
		
#         ### Methods

#         - see the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#lessons)
		
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
#         ```json
#         {
#             "data" : 
#                 [
#                     { "chapter" : 2, "stimuli" : "il", "type" : "word", "lesson" : null, "subject" : "letters", "dataset" : "gapfill_lang" }
#                     ...
#                 ]
#         }
#         ```
#         """
#         if db.path.count() == 0:
#             raise abort(500, "Table path is empty: initialize the database")
#         lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de leçons")
#         return {"type": "lessons", "lessons": lessons, "data": lessons}


# @ns_admin.route("/lessons/datasets/<string:dataset>")
# class LessonsDatasetList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self, dataset):
#         """
#         Consult the lessons by dataset

#         ### Description
		
#         Expose the table `path`  
#         giving the list of lessons of a specific dataset as declared in path
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#lessons)
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
#         ```json

#         {   "data" :
#             [ 
#                 { "chapter" : 2, "stimuli" : "il", "type" : "word", "lesson" : null, "subject" : "letters", "dataset" : "gapfill_lang" },
#                 ...
#             ],
#             "dataset:" "gapfill_lang",
#             "subject": "letters",
#             "subject_name: "Français",
#         ```
#         """
#         dataset_ref = db.path.find_one({"dataset": dataset})
#         if dataset_ref is None:
#             raise abort(406, "Le dataset `{}` n'existe pas".format(dataset))
#         else:
#             if dataset_ref["subject"] == "letters":
#                 subject_name = "Français"
#             else:
#                 subject_name = "Maths"
#             lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#             if len(lessons) == 0:
#                 raise abort(404, "Pas de leçons pour le dataset {}".format(dataset))
#             return {
#                         "lessons": lessons, 
#                         "dataset": dataset, 
#                         "subject":dataset_ref["subject"], 
#                         "subject_name": subject_name 
#                     }
# @ns_admin.route("/lessons/subject/<string:subject>")
# class LessonsDatasetList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self, dataset):
#         """
#         Consult the lessons by subject

#         ### Description
		
#         Expose the table `path`  
#         giving the list of lessons of a specific dataset as declared in path
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#lessons)
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
#         ```json

#         {   "data" :
#             [ 
#                 { "chapter" : 2, "stimuli" : "il", "type" : "word", "lesson" : null, "subject" : "letters", "dataset" : "gapfill_lang" },
#                 ...
#             ],
#             "dataset:" "gapfill_lang",
#             "subject": "letters",
#             "subject_name: "Français",
#         ```
#         """
#         dataset_ref = db.path.find_one({"subject": subject})
#         if dataset_ref is None:
#             raise abort(406, "Le sujet `{}` n'existe pas".format(subject))
#         else:
#             if dataset_ref["subject"] == "letters":
#                 subject_name = "Français"
#             else:
#                 subject_name = "Maths"
#             lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#             if len(lessons) == 0:
#                 raise abort(404, "Pas de leçons pour le dataset {}".format(dataset))
#             return {
#                         "lessons": lessons, 
#                         "subject":dataset_ref["subject"], 
#                         "subject_name": subject_name 
#                     }

# @ns_admin.route("/chapters")
# class ChaptersList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the chapters defined in the game

#         ### Description
		
#         Expose the table `path`  
#         giving the list of chapters when declared in path
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#chapters)
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
		
#         ```json
#         data = [
#             { "chapter" : 1, "lesson" : 1, "subject" : "letters", "dataset" : "gp", "visualaudio" : "a-a", "visual" : "a", "audio" : "a", "CV" : "V", "tag" : "a", "games" : [ "jellyfish", "jellyfish", "crabs" ] }
#         ]
#         ```
#         """
#         lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de chapitres")
#         return {"type": "chapters", "chapters": lessons, "data": lessons}

# @ns_admin.doc(params={
#     "subject": "A subject as included in the list [letters, numbers]"
# })
# @ns_admin.route("/chapters/subjects/<subject>")
# class ChaptersSubjectList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self, subject):
#         """
#         Consult the chapter by subject

#         ### Description
		
#         Expose the table `path`  
#         giving the list of chapters of a specific subject as declared in path
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#chapters)
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
		
#         ```json
#             {
#                 "data" :
#                     [ 
#                         { "chapter" : 2, "stimuli" : "il", "type" : "word", "lesson" : null, "subject" : "letters", "dataset" : "gapfill_lang" },
#                         ...
#                     ],
#                 "subject": "letters",
#                 "subject_name: "Français"
#             }
#         ```
#         """
#         if subject not in ["letters", "numbers"]:
#             raise abort(406, "Le sujet `{}` n'existe pas".format(subject))
#         else:
#             if subject == "letters":
#                 subject_name = "Français"
#             else:
#                 subject_name = "Maths"
#         lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de chapitre pour le sujet `{}`".format(subject))
#         return {"type": "chapters", "chapters": lessons,"data": lessons, "subject":subject, "subject_name": subject_name}

# @ns_admin.doc(params={
#     "dataset": "A dataset as included in the list [gapfill_lang, asessments_language, assessments_maths, gp, numbers]"
# })
# @ns_admin.route("/chapters/datasets/<string:dataset>")
# class ChaptersDatasetList(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self, dataset):
#         """
#         Consult the chapters by dataset

#         ### Description
		
#         Expose the table `path`  
#         giving the list of lessons of a specific dataset as declared in path
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/stats/progression.md#lessons)
#         Path table is built with the references files given by admin and inserted at initialization          
		
#         ### Output example
		
#         ```json
#             {
#                 "data" :[ 
#                     { "chapter" : 2, "stimuli" : "il", "type" : "word", "lesson" : null, "subject" : "letters", "dataset" : "gapfill_lang" },
#                     ...
#                 ],
#                 "dataset:" "gapfill_lang",
#                 "subject": "letters",
#                 "subject_name: "Français"
#             }
#         ```
#         """
#         dataset_ref = db.datasets.find_one({"dataset": dataset})
#         if dataset_ref is None:
#             raise abort(406, "Le dataset `{}` n'existe pas".format(dataset))
#         else:
#             if dataset_ref["subject"] == "letters":
#                 subject_name = "Français"
#             else:
#                 subject_name = "Maths"
#             lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#             if len(lessons) == 0:
#                 raise abort(404, "Pas de chapitre pour le dataset {}".format(dataset))
#             return {
#                         "data": lessons, 
#                         "dataset": dataset, 
#                         "subject":dataset_ref["subject"], 
#                         "subject_name": subject_name 
#                     }

# @ns_admin.route("/datasets")
# class Datasets(Resource):
#     @ns_admin.expect(dataset_model)
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the datasets available 
		
#         ### Description
		
#         Expose the table `datasets`  
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/datasets.md#)
#         """
#         db = connect
#         return db.datasets.find({}, {"_id": 0}) 

# @ns_admin.route("/subjects")
# class Datasets(Resource):
#     @ns_admin.expect(subject_model)
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the svbjects available 
		
#         ### Description
		
#         Expose the table `datasets`  
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/datasets.md#)
#         """
#         
#         return db.datasets.distinct("subject") 


# @ns_admin.route("/files")
# class LogFiles(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the svbjects available 
		
#         ### Description
		
#         Expose the table `datasets`  
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/datasets.md#)
#         """
#         
#         return list(db.files.find({}, {"_id":0})) 
# @ns_admin.route("/references")
# class LogFiles(Resource):
#     @ns_admin.response(200, 'Success')
#     @ns_admin.response(404, 'No data')
#     @ns_admin.response(406, "Incorrect parameter")
#     @ns_admin.response(500, "Database Error")
#     def get(self):
#         """
#         Consult the svbjects available 
		
#         ### Description
		
#         Expose the table `datasets`  
		
#         ### Methods

#         See the complete documentation on method: (htts://lab.driss.org/kalulu/docs/datasets.md#)
#         """
		
#         init(DIRS)
#         return list(db.references.find({}, {"_id":0})) 
# @ns_admin.route('/tasks/stats/<action>/<student>')
# def task_processing(action, student):
#     task = update.delay(action, student)
#     async_result = AsyncResult(id=task.task_id, app=celery)
#     processing_result = async_result.get()
#     return processing_result


@ns_admin.route("/students/<student>/group/<group>")
class StudentGroup(Resource):
	@ns_admin.response(204, 'Student group updated')
	@ns_admin.response(404, 'No student found')
	@ns_admin.response(406, 'Incorrect parameter (studen or group)')
	def put(self, student, group):
		'''
		UPDATE student `group`

		## Method

		SELECT * as student FROM table students WHERE student=_<student>_;
		UPDATE student.group=_<group>_;
		
		'''
		db = connect()
		# group = request.json["group"]
		if group not in db.students.distinct("group"):
			return abort(406, "Group {} is not accepted".format(group))
		existing_student = db.students.find_one({"student": int(student)})
		if existing_student is None:
			return abort(404, "Student {} not found".format(student))
		else:
			status, response = update_student_group(student,existing_student["group"], group)
			if status is False:
				return abort(response['code'], response["msg"])
			else:
				return Response(204, response["msg"])


###### multiple edit
@ns_admin.doc(security='apikey')
@token_required
@ns_admin.expect(students, validate=True)	
def put(self):
		''' Update `group` for students
		
		## Methods

		Edit payload as shown in example

		Change the group for a list of students separated by `,`
		data = {"group": "r/m", "students":"2626,745,802,985,3972"}
		
		'''
		db = connect()
		group = request.json["group"]
		students = request.json["students"]
		student_ids = [n.strip() for n in students.split(",")]
		student_count = len(student_ids)
		counter = 0
		codes = []
		msgs = [] 
		for student in student_ids:
			try:
				student = int(student)
			except Exception as e:
				#partial response? No
				status = False
				msg = "Student {} is a incorrect, id must be integer.".format(student)
				codes.append(406)
				msgs.append(msg)
				continue
			existing_student = db.students.find_one({"_id": student}, {"group":1})
			if existing_student is None:
				status = False
				msg = "student {} doesn't exist.".format(student)
				codes.append(406)
				msgs.append(msg)
				continue
			else:
				status, response = update_student_group(student, existing_student["group"], group)
				codes.append(response["code"])
				msgs.append(response["msg"])
				if status is True:
					counter += 1		
		if counter > 0:
			msg = "Group successfully updated to `{}` for {}/{} students: {}".format(group, counter, student_count, student_ids)
			return {"code": 204, "message": msg}, 204
		else:
			return abort(codes[-1], {"code": codes[-1], "message": ", ".join(msgs)})