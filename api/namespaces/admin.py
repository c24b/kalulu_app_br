from __future__ import absolute_import

import os
import subprocess
from flask import jsonify
from flask import current_app
from flask import stream_with_context
from flask import g

from flask import request, Response
from flask_restx import Namespace, Resource, abort,fields

from functools import wraps
from flask import request

from settings.api import SUDO_TOKEN
from settings.api import TOKEN
from settings.files import REFERENCES_FILES

from utils.db import connect
from utils.db import dbtable_to_csvfile

# from celery.task.control import inspect
# from itertools import chain


ns_admin = Namespace('admin', description='Administrative tasks and operations')

student_model = ns_admin.model('Student', {
	'student': fields.Integer(required=True, example=212, description="An integer between 111 and 60820"),
	'group': fields.String(required=True, example="r/m", description="A string in ['guest','r/m','m/r']"),
	'classroom': fields.Integer(required=True, example=2, description="An integer between 1 and 60"),
	'tablet': fields.Integer(required=False, example=1, description="An integer between 1 and 8"),
	'kid': fields.Integer(required=False, example=2, description="An integer between 1 and 8"),
	'status': fields.Boolean(required=False, example= True, description="A boolean that describe status of the student  if True has group has file if False group is missing or files are missing"),
	'files_nb': fields.Integer(required=False, example=2, description="An integer that gives the number of files found for the student")
})

students_model = ns_admin.model("Students", {
	"group": fields.String(required=True, example="r/m", description="A string in ['guest','r/m','m/r', None]"),
	"students": fields.String(required=True, example="3931,3926,3976,745", decription="A string listing the student ids with a coma as separator")
})

classroom_model = ns_admin.model('Classroom', {
	'students': fields.List(fields.Integer, description='List of students', required=False, example=[211, 212, 213, 222, 223]),
	'group': fields.String(required=True, description="A string in ['guest','r/m','m/r', None]", example="r/m"),
	'classroom': fields.Integer(required=True, example=2,description="An integer between 1 and 60")
})

dataset_model = ns_admin.model('Dataset', {
	'dataset': fields.String(required=True, description="[gp, assessments_langage, assessments_maths, gapfill_lang, numbers]"),
	"subject" : fields.String(required=True, description="[numbers, letters]"),
	"type" : fields.String(required=False, description=["chapter", "lesson", "item"]),
})

subject_model = ns_admin.model('Subject', {
	'datasets': fields.List(fields.String, description='List of dataset', required=True, example="[gp, assessments_language, gapfill_lang]"),
	"subject" : fields.String(required=True, description = "A string included in [numbers, letters]", example="letters"),
})

group_model = ns_admin.model('Group', {
'group': fields.String(required=True, description="A string in ['guest','r/m','m-r', None]", example="r/m")
})


status_model = ns_admin.model('Status', {
'status': fields.Boolean(required=True, description="A boolean status: True/False ", example=False)
})

### FUNCTIONS
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'X-API-KEY' in request.headers:
			token =request.headers["X-API-KEY"]
		if not token:
			return {"message": "Token is missing."}, 401
		if token != TOKEN:
			return {"message": "Token is invalid"}, 401
		return f(*args, **kwargs)
	return decorated

### FUNCTIONS
def admin_token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'X-API-KEY' in request.headers:
			token =request.headers["X-API-KEY"]
		if not token:
			return {"message": "Token is missing."}, 401
		if token != SUDO_TOKEN:
			return {"message": "Token is invalid."}, 401
		return f(*args, **kwargs)
	return decorated

  
def update_student_group(student, old_group, new_group):
	'''
	UPDATE student group
	- update students TABLE with group
	- background job of updating stats for one student
	- prepare response
	'''
	
	msg = "Group for student '{}' has been successfully updated to `{}`".format(student, new_group)
	if new_group == old_group:
		
		msg = "Group for student {} is already set to `{}`".format(student, old_group)
		# logging.info(msg)
		return True, 201, msg
		
	elif old_group is not None and new_group == "guest":
		'''
		if group is now guest and was r/m or m/r 
		=> delete corresponding stats
		stats(delete, student)
		'''
		print("Calling update_stats")
		current_app.celery.send_task('celery_tasks.update_stats',args=["delete",student])
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
		current_app.celery.send_task('celery_tasks.update_stats',args=["create",student])
		print("Sent to celery")
	return True, 200, msg


@ns_admin.route("/students")
class StudentList(Resource):
	
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No students found')
	def get(self):
		''' 
		VIEW students list
		
		## Method
		
		SELECT * from table students
		        
        ### Documentation
  
		Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
  
		## Output
		```
		{
			"students":[
				{
				"_id": 565,
				"student": 565,
				"classroom": 5,
				"tablet": 6,
				"kid": 5,
				"group": "guest",
				"files_nb": 8,
				"status": true
				},
				...
			],
			"count":1160, 
			"csv": "API_URL/admin/students/csv"
		}	
		'''
		db = connect()
		if db.students.count() == 0:
			return abort(404, "No students found")
		else:
			return {
				"students":list(db.students.find()),
				"count": db.students.count(),
				"csv": "{}/csv".format(request.base_url)
				}
	
	@token_required
	@ns_admin.doc(security='apikey')
	@ns_admin.response(200, 'Success')
	@ns_admin.response(201, 'No modification')
	@ns_admin.response(200, 'Updated')
	@ns_admin.response(404, 'No student found')
	@ns_admin.response(406, 'Incorrect student/group parameter')
	@ns_admin.expect(students_model, validate=True)
	def put(self):
		'''
		UPDATE students list with group
		
		## Method

		FOR _<student_id>_ IN _<data["students"]>_
		SELECT * as student FROM table students WHERE student._id==__<student_id>__;
		UPDATE student.group==__<data["group"]>__;
		
		## How to
		Press the `try it` button
		
		edit `"group"` value 
		edit `"students"` values
		respecting format
		inside payload:
		```
		{
			"group": "guest",
			"students: "2323,745,878,2322,1867"
		}
		```
		'''
		
		db = connect()
		group = request.json["group"]
		group = group.replace("-","/")
		students = request.json["students"]
		try:
			student_ids = [int(n.strip()) for n in students.split(",")]
		except Exception as e:
			return abort(406, "Invalid parameter 'students': students is not a list of integer")
		student_count = len(student_ids)
		counter = 0
		codes = []
		msgs = [] 
		if student_count == 0:
			return abort(406, "Invalid parameter 'students': students is empty")
		elif group not in db.students.distinct("group") and group not in ["", "None", None]:
			return abort(406, "Invalid parameter 'group': group {} not accepted".format(group))
		else:
			for student in student_ids:
				existing_student = db.students.find_one({"_id": student}, {"group":1})
				if existing_student is None:
					status = False
					msg = "student {} doesn't exist.".format(student)
					return abort(404, "Student {} not found".format(student))
			else:
				status, code, response = update_student_group(student, existing_student["group"], group)
				if status is True:
					counter += 1		
		if counter > 0:
			msg = "Group successfully updated to `{}` for {}/{} students: {}".format(group, counter, student_count, student_ids)
			return {"message":msg}, 200
		else:
			return {"message": "No modification made"}, 201


	
@ns_admin.route("/students/<student>")
class Student(Resource):
	@ns_admin.response(200, 'Success')
	@ns_admin.response(404, 'No student found')
	@ns_admin.response(406, 'Incorrect student ID')
	def get(self, student):
		"""
		VIEW student item
		
		## Method
		
		SELECT * from table students WHERE student=_<student_id>_

		## Output
		```
		{
			"_id": 565,
			"student": 565,
			"classroom": 5,
			"tablet": 6,
			"kid": 5,
			"group": "guest",
			"files_nb": 8,
			"status": true
		}
		## Documentation
  		Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		"""
		db = connect()
		if int(student) not in range(110, 60820):
			return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
		if int(student) not in db.students.distinct("student"):
			return abort(404, "L'élève n'a pas été trouvé")
		else:
			return {
				"student":db.students.find_one({"_id": int(student)}), 
				"count":1, 
				"csv": "{}/csv".format(request.base_url)
			}
	
	@ns_admin.response(200, 'Sucessfully Updated')
	@ns_admin.response(404, 'No student found')
	@ns_admin.response(406, 'Incorrect student/group parameter')
	@ns_admin.expect(group_model, validate=True)
	@token_required
	@ns_admin.doc(security='apikey')
	def put(self, student):
		'''
		UPDATE student item with `group`

		## Method

		SELECT * as student FROM table students WHERE student=_<student_id>_;
		UPDATE student.group=_<data["group"]>_;
		
		## How to

		add student in parameters
		and edit "group" value inside 
		```
		{
			"group": ""
		}
		```
		'''
		
		db = connect()
		try:
			student = int(student)
		except KeyError:
			return abort(406, "Student ID {} is incorrect".format(student))
		group = request.json["group"]
		group = group.replace("-", "/")
		if group not in db.students.distinct("group") and group not in ["", "None", None]:
			return abort(406, "Group {} is not accepted".format(group))
		existing_student = db.students.find_one({"student": student})
		if existing_student is None:
			return abort(404, "Student {} not found".format(student))
		
		status, code, response = update_student_group(student, existing_student["group"], group)
		print(code, response)
		if status is False:
			return abort(code, response)
		else:
			db.students.update({"student":student},{"$set":{"group": group}})
			#update status for all students
			db.students.update({"group":{"$ne":None}, "files_nb":{"$gt":0}}, {"$set": {"status": True}})
			dbtable_to_csvfile(REFERENCES_FILES["students"][0], table_name="students")
			return {"message": response}, code
	@token_required
	@ns_admin.response(200, 'Deleted')
	@ns_admin.response(404, 'No student found')
	@ns_admin.doc(security='apikey')
	def delete(self, student):
		'''
		DELETE student

		## Method
		
		DELETE student FROM students table
		WHERE student._id = _<student>_ 
		
		Remove stats of students
		Compute global stats again
		Remove student from reference files
		
  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		'''
		db = connect()
		if  db.students.find_one({"student":int(student)}) is None:
			return abort(404, "Student {} not found".format(student))

		result = current_app.celery.send_task('celery_tasks.update_stats',args=["delete",int(student)])
		db.students.delete({"student":int(student)})
		
		dbtable_to_csvfile(REFERENCES_FILES["students"][0], table_name="students")
		return {"message": "Sucessfully deleted student {}".format(student)}

@ns_admin.doc({
	"status":"A string expressing status in list [True, true, False, false, missing, empty]"})
@ns_admin.route("/students/status/<status>")
class StudentListStatus(Resource):
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No student with status found')
	@ns_admin.response(406, 'Incorrect student/status parameter')
	def get(self, status):
		'''
		VIEW students list having a specific status 
		
		## Description
		
		`status` parameters can be:
			- True true
			- False false
			- 'missing' status is False group is missing
			- 'empty' status is False no file for this student
		
		status is `False`: 
		- when student has group and no file corresponds to `empty`: 
		
		student has been declared but no corresponding files have been found
		
		- when student has files and no group corresponds to `missing`: 
		
		student has not been declared 
		

		## Method
		
		SELECT student FROM students table
		WHERE status=_<status>_ 
		
  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
     
		'''
		db = connect()
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
			return {"students":students, "count": len(students), "csv": "{}/csv".format(request.base_url)}
		else:
			return abort(404, "No student with status {} has been found.".format(status))

@ns_admin.doc({"group":"A string expressing status in list ['rm', 'mr', 'guest', None]"})
# @ns_admin.expect(status_model, validate=True)
@ns_admin.route("/students/groups/<group>")
class StudentListGroup(Resource):
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No student found with this group')
	@ns_admin.response(406, 'Incorrect parameter group')
	def get(self, group):
		'''
		VIEW students belonging to a specific group 
		
## NB:
`{group}` **parameter** is expressed with `-` instead of `/` in this endpoint 
as '/' is a reserved caracter

## Description

`group` parameters can be:	
- r-m
- m-r
- guest
- None

Group:			
- group is `None` when student has no group declared: he is missing  
- group is `guest` when student has been removed from statistics
- group is `rm`(r/m into database) when student has begun by reading and then maths 
- group is `mr`(m/r into database) when student has begun by maths and then reading

## Method

SELECT student from table students
WHERE student.group == __<group>__

## Documentation

Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		'''
		db = connect()
		group = group.replace("-", "/")
		# print(db.students.distinct("group")) 
		if group == "None" or group == "null":
			group = None
		if group not in db.students.distinct("group"):
			abort(406, "Group `{}` doesn't exists and is not accepted".format(group))
		else:
			students = list(db.students.find({"group":group}))
		
		if len(students) > 0:
			return {"students":students, "count": len(students), "csv": "{}/csv".format(request.base_url)}
		else:
			return abort(404, "No student with status {} has been found.".format(status))


@ns_admin.route("/classrooms")
class ClassroomList(Resource):
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No classroom found')
	def get(self):
		"""
		VIEW classrooms list
		
		## Method
		
		SELECT student FROM table student
		SORT by student.classroom
  

  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
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
		return {"classrooms": classroom_records, "count": len(classroom_records), "csv": "{}/csv".format(request.base_url)}

@ns_admin.doc(params={'classroom': 'An integer between 1 and 60'})
@ns_admin.route("/classrooms/<classroom>")
class Classroom(Resource):
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No classroom found')
	def get(self, classroom):
		"""
		VIEW classroom item
		
		## Method
		
		SELECT student FROM table students
		WHERE student.classroom == _<classroom>_
		
  
  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		"""
		db = connect()
		students = [n for n in db.students.find({"classroom": int(classroom)})]
		if len(students) == 0:
			return abort(404, "no classroom `{}` found".format(classroom))
		return {"classroom": students, "count": len(students), "csv": "{}/csv".format(request.base_url)} 
	@ns_admin.doc(security='apikey')    
	@token_required
	@ns_admin.response(200, 'OK')
	@ns_admin.response(201, 'No modification')
	@ns_admin.response(200, 'Modified')
	@ns_admin.response(404, 'No classroom found')
	@ns_admin.response(406, 'Invalid group')
	@ns_admin.expect(group_model, validate=True)
	def put(self, classroom):
		"""
		UPDATE classroom item with `group`
		
		## Method
		SELECT student FROM students table
		WHERE student.classroom = _<classroom>_
		UPDATE student.group SET _<group>_
  

  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		"""
		db = connect()
		classroom = int(classroom)
		group = request.json["group"]
		group = group.replace("-", "/")
		counter = 0 
		student_count = db.students.count({"classroom": classroom})
		print(student_count)
		if student_count == 0:
			return abort(404, "Classroom {} not found".format(classroom))
		if group not in db.students.distinct("group"):
			return abort(406, "Invalid group {}".format(group))
		status = True
		for student in db.students.find({"classroom": classroom}, {"student":1, "group":1}):
			print(student)
			existing_group = student["group"]
			status, code, response = update_student_group(student["student"], existing_group, group)
			if status is True:
				counter += 1
				
		print(counter)
		if counter == 0:
			return abort(201, "No modifications")
		else:
			msg = "Group successfully updated to `{}` for classroom {}: {}/{} students updated".format(group, classroom, counter, student_count)
			return {"msg":msg}, 200
 
	@token_required
	@ns_admin.response(200, 'Successfully deleted')
	@ns_admin.response(404, 'No classroom found')
	@ns_admin.doc(security='apikey')
	
	def delete(self, classroom):
		'''
		DELETE classroom

		## Method
		
		DELETE student FROM students table
		WHERE student.classroom = _<classroom>_ 
		
		Remove stats of classroom
		Compute global stats again
		Remove classroom from reference files
		
  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
  		'''
		db = connect()
		students = list(db.students.find({"classroom":int(classroom)}))
		if students is None:
			return abort(404, "Classroom {} not found".format(student))
		for student in students:
			result = current_app.celery.send_task('celery_tasks.update_stats',args=["delete",student["student"]])
			db.students.delete({"student":student["student"]})
		dbtable_to_csvfile(REFERENCES_FILES["students"][0], table_name="students")
		return {"msg":"Sucessfully deleted student {}".format(student)}, 200

# @ns_admin.doc(params={'files': 'An integer between 1 and 60'})
@ns_admin.route("/files")
class Files(Resource):
	@ns_admin.response(200, 'OK')
	@ns_admin.response(404, 'No files found')
	def get(self):
		"""
		VIEW downloaded files
		
		## Method
		
		SELECT * from files

  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		"""
		db = connect()
		files = list(db.files.find({}, {"_id":0}))
		
		if len(files) == 0:
			return abort(404, "no files found")
		return {"files": sorted(files, key =lambda x: x["filename"]), "count": len(files), "csv": "{}/csv".format(request.base_url)} 
	@ns_admin.doc(security='apikey')    
	@admin_token_required
	@ns_admin.response(200, 'OK')
	@ns_admin.response(200, 'Modified')
	def put(self):
		"""
		UPDATE files by downloading, cleaning, initializing the datbase and insert records
		## Methods

		Use back.main fonction 'run_steps()'
		
  		## Documentation
  		
    	Consult [admin documentation](http://doc.ludoeducation.fr/researcher-guide/admin/)
		"""
		print("Regenerating the database")
		current_app.celery.send_task('celery_tasks.run', args=[{"download": True, "student":None}])
		msg = "regenerating the database completly. "
		return msg, 200 

@ns_admin.route("/path")
class Path(Resource):
	def get(self):
		"""
		VIEW pedagogical path
		
		## Method
		
		SELECT * from path

  		## Documentation
  		
    	Consult http://doc.ludoeducation.fr/researcher-guide/admin/
		"""
		db = connect()
		if db.path.count() == 0:
			raise abort(500, "Table path is empty: initialize the database")
		path = list(db.path.find({}, {"_id":0}))
		if len(path) == 0:
			raise abort(404, "Pas de path")
		return {"path": path}