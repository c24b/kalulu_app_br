from flask import Blueprint, render_template, abort
from utils.db import connect
from utils.files import convert_raw_data

csv_letters = Blueprint('letters', __name__, url_prefix='/letters')
csv_numbers = Blueprint('numbers', __name__, url_prefix='/numbers')

db = connect()

@csv_letters.route("/words/csv")
def get_words():
    """
    Consult the words 
    """
    words = list(db.words.find({}, {"_id":0}))
    if len(words) == 0:
        return abort(404, u"404 - No Data")
    return convert_raw_data({
        "data": sorted(words, key= lambda x:x["nb_letters"])
    })
@csv_letters.route("/words/students/<int:student_id>/csv")
def get_student_words(student_id):
    """
    Consult the words of a student specifying the student id
    student: an integer between 111 and 60820
    """
    if int(student_id) not in range(111, 60820):
        return (406, "406 - Incorrect Student ID")
    if int(student_id) not in db.students.distinct("student"):
        return abort(406, "406 - Incorrect Student ID")
    student_words = list(db.student_words.find({"student": int(student_id)}, {"records": 0, u"_id": 0}))
    if len(student_words) == 0:
        return abort(404)
    return convert_raw_data({
        "data": sorted(student_words, key= lambda x:x["nb_letters"])
    })

@csv_letters.route("/syllabs/students/<int:student_id>/csv")
def get_student_syllabs(student_id):
    """
    Consult the words of a student specifying the student id
    student: an integer between 111 and 60820
    """
    
        
    if int(student_id) not in range(111, 60820):
        return (406, "406 - Incorrect Student ID")
    if int(student_id) not in db.students.distinct("student"):
        return abort(406, u"406 - Incorrect Student Not Found")
    student_syllabs = list(db.student_syllabs.find({"student": int(student_id)}, {"_id" :0, u"stimuli":0}))
    if len(student_syllabs) == 0:
        
        return abort(404, u"404 - No Data")
    return convert_raw_data({
        "data": sorted(student_syllabs, key= lambda x:len(x["word"]))
        })
@csv_numbers.route("/association/students/<int:student_id>/csv")
def get_student_association( student_id):
    """
    Consult the result on association digits game specifying student id
    """
    if int(student_id) not in range(111, 60820):
        return (406, "406 - Incorrect Student ID")
    if int(student_id) not in db.students.distinct("student"):
        return abort(406, "406 - Incorrect Student ID")
    student_id_digits = list(db.student_association.find({"student": int(student_id)}, {"_id": 0, "games":0}))
    if len(student_id_digits) == 0:
        return abort(404, u"404 - No Data")
    return convert_raw_data({
        "data": student_id_digits
    })
@csv_numbers.route("/identification/students/<int:student_id>/csv")
def get_student_id( student_id):
    """
    Consult the result on identification digits game specifying student id
    """
    if int(student_id) not in range(111, 60820):
        return (406, "406 - Incorrect Student ID")
    if int(student_id) not in db.students.distinct("student"):
        return abort(406, "406 - Incorrect Student ID")
    student_id_digits = list(db.student_identification.find({"student": int(student_id)}, {"_id": 0, "games":0}))
    if len(student_id_digits) == 0:
        return abort(404, u"404 - No Data")
    return convert_raw_data({
        "data": student_id_digits
    })
@csv_numbers.route("/counting/students/<int:student_id>/csv")
def get_student_counting( student_id):
    """
    Consult the result on counting digits game specifying student id
    """
    if int(student_id) not in range(111, 60820):
        return (406, "406 - Incorrect Student ID")
    if int(student_id) not in db.students.distinct("student"):
        return (406, "406 - Incorrect Student ID")
    student_counting_digits = list(db.student_counting.find({"student": int(student_id)}, {"_id": 0, "games":0}))
    if len(student_counting_digits) == 0:
        return abort(404, u"404 - No Data")
    return convert_raw_data({
        "data": student_counting_digits
    })
