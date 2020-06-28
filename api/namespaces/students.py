from flask import request
from flask_restx import Namespace, Resource, abort, fields
from settings import connect, errors, db, TOKEN
from functools import wraps
from utils.db import connect

db = connect()
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

ns_student = Namespace('students', description='Consult and update students in the game')
student_definition = ns_student.model('Student', {
    'student': fields.Integer(required=True, example=212, description="An integer between 111 and 60820"),
    'group': fields.String(required=True, example="r/m", description="A string in ['guest','r/m','m/r']"),
    'classroom': fields.Integer(required=True, example=2, description="An integer between 1 and 60")
})

ns_classroom = Namespace('classrooms', description='Consult and update classrooms in the game')
classroom_definition = ns_classroom.model('Classroom', {
    'students': fields.List(fields.Integer, description='List of students', required=False, example=[211, 212, 213, 222, 223]),
    'group': fields.String(required=True, description="A string in ['guest','r/m','m/r']", example="r/m"),
    'classroom': fields.Integer(required=True, example=2,description="An integer between 1 and 60")
})


@ns_student.route("/")
class Students(Resource):
    @ns_student.response(200, 'Success')
    @ns_student.response(404, 'No data')
    @ns_student.response(406, "Incorrect parameter")
    @ns_student.response(500, "Database Error")
    def get(self):
        ''' Consult the students '''
        students = list(db.students.find())
        return {"data":students}
    @ns_classroom.doc(security='apikey')
    @token_required
    @ns_student.expect(student_definition, validate=True)
    def post(self, **kwargs):
        '''Add a new student'''
        pass


# @ns_student.marshal_with(student_definition, as_list=True)
@ns_student.doc(params={
    'student': 'An integer between 111 and 60820',
    
})
@ns_student.expect(student_definition)
@ns_student.route("/<student>/")
class Student(Resource):
    @ns_student.response(200, 'Success')
    @ns_student.response(404, 'No data')
    @ns_student.response(406, "Incorrect parameter")
    @ns_student.response(500, "Database Error")
    def get(self, student):
        """
        Student definition 

        ### Description
        
        Expose the table `students` created at initialization of the database: 
        by the document list 
        and updated throught a CSV referenced file that add group information 
        
        Group define if we include the student into stats 
        
        ### Output example:
        ```json
        ```
        
  		## Documentation
  		
    	Consult [documentation](http://doc.ludoeducation.fr/researcher-guide/stats/students/)
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
    
@ns_classroom.expect(classroom_definition)
@ns_classroom.route("/")
class Classroom(Resource):
    @ns_classroom.response(200, 'Success')
    @ns_classroom.response(404, 'No data')
    @ns_classroom.response(406, "Incorrect parameter")
    @ns_classroom.response(500, "Database Error")
    def get(self):
        """
        Classroom definition 

        ### Description
        
        Expose the table `students` grouped by classroom created at initialization of the database: 
        by the document list 
        and updated throught a CSV referenced file that add group information 
        
        Group define if we include the student into stats 
        
        ### Output example:
        ```json
        ```
        ## Documentation
  		
    	Consult [documentation](http://doc.ludoeducation.fr/researcher-guide/stats/students/)
        """
        
        
        db = connect()

        classroom = list(db.students.find({"classroom": classroom}))
        if len(classroom) == 0:
            return {"message": "Classroom {} Not Found".format(classroom)}, 404
        groups = set([n["group"] for n in classrom])
        if len(groups) != 1:
            return {"message": "Classroom has multiple groups {}. Aborting".format(groups)}, 409
        return {"classroom": classroom, "group": groups[0], "students": [n["student"] for n in classroom]} 
        
    @ns_classroom.doc(security='apikey')
    @token_required
    @ns_classroom.expect(classroom_definition, validate=True)
    def post(self):
        '''Add a new classroom'''
        db = connect()
        classroom = request.json["classroom"]
        students = request.json["students"]
        group = request.json["group"]
        for n in students:
            if not str(n).startswith(classroom):
                return {"message":"Student doesn't belong to classroom: student ID must start with classroom ID"}, 406
            else:
                pass
                # db.students.update({"student":n, "group": group, "classroom": classroom},True)
        return {"message": "Sucessfully added classroom {}".format(classroom)}, 204

    @ns_classroom.doc(security='apikey')    
    @token_required
    @ns_classroom.expect(classroom_definition, validate=True)
    def put(self):
        '''Update a classroom'''
        db = connect()
        classroom = request.json["classroom"]
        # students = request.json["students"])
        group = request.json["group"]
        for n in students:
            if not str(n).startswith(classroom):
                return abort(406, "Student doesn't belong to classroom: student ID must start with classroom ID")
        # for n in db.students.find({"classroom":classroom}):
        #     db.students.update({"_id":n["_id"]} {"$set":{"group": group, "classroom": classroom}})
        return {"message": "Sucessfully udpated classroom {}".format(classroom)}, 204
