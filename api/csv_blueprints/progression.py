from flask import Blueprint, render_template
from flask_restx import abort
from bson import json_util
from utils.db import connect
import json
import time
from utils.files import convert_raw_data

csv_progression = Blueprint('progression', __name__, url_prefix='/progression')
db = connect()
@csv_progression.route("/chapters/students/<int:student>/subjects/<string:subject>/csv")
def get_student_chapters( subject, student):
        
    if int(student) not in range(111, 60821):
        raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
    if student not in db.students.distinct("student"):
        raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    chapters = db.student_chapters.find_one({"student": student, "dataset": dataset}, {"_id":0}) 
    progression = []
    for n in chapters["chapters_ids"]:
        progression.extend(list(db.student_chapter.find({"chapter":n},{"records":0, "_id":0})))
            
    if len(chapters) == 0:
        raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
    return convert_raw_data({"data": sorted(progression, key=lambda x: x["chapter"])})

@csv_progression.route("/chapters/students/<int:student>/subjects/<string:subject>/last/csv")
def get_student_chapters_last( subject, student):
    if int(student) not in range(111, 60821):
        raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
    if student not in db.students.distinct("student"):
        raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    chapters = db.student_chapters.find_one({"student": student, "dataset": dataset}, {"_id":0}) 
    last_chapter_id = chapters["chapters_ids"][-1]
    if len(chapters) == 0:
        raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
    last_chapter = db.student_chapter.find_one({"student": student, "dataset": dataset, "chapter":last_chapter_id}, {"_id":0, "chapters":0})
    return convert_raw_data({"data": last_chapter})

@csv_progression.route("/chapters/classrooms/<int:classroom>/subjects/<string:subject>/csv")
def get_classroom_chapters( classroom, subject):
    ''' For readibility purpose we do not expose the matrix graph but the raw data'''    
    if int(classroom) not in range(1, 60):
        raise abort(406, "L'identifiant de la classe `{}` est incorrect, vérifiez votre identifiant.".format(classroom))
    if int(classroom) not in db.students.distinct("classroom"):
        raise abort(404, "La classe `{}` n'a pas été trouvée".format(classroom))
    if subject not in ["letters", "numbers"]:
        raise abort(406, "Le sujet `{}` n'existe pas encore.".format(subject))
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    dataset_ref = db.datasets.find_one({"dataset": dataset})
    if dataset_ref is None:
        raise abort(406, "Le nom du dataset `{}` est incorrect.".format(dataset))
    else:
        if dataset_ref["subject"] == "letters":
            subject_name = "Français"
        else:
            subject_name = "Maths"
    lessons_refs = list(db.path.find({"dataset": dataset}, {"_id":0}))
    lessons = db.path.distinct("lesson",{"dataset": dataset})
    u_tags = sorted([(t,db.path.find_one({"tag":t}, {"lesson":1})["lesson"]) for t in db.path.distinct("tag", {"dataset": dataset})], key=lambda x: x[1])
    tags = [n[0] for n in u_tags]
    
    class_lessons = list(db.student_lessons.find({"classroom": classroom, "dataset": dataset}, {"_id":0, "lessons":0}))
    students = [db.students.find_one({"student": n["student"]}, {"kid":1, "tablet":1}) for n in class_lessons]
    if len(class_lessons) == 0:
        raise abort(404, "Pas de données pour la classe {} sur le sujet {}.".format(classroom, subject))
    return convert_raw_data({"data":sorted(class_lessons, key= lambda x:x["student"])})
        


@csv_progression.route("/lessons/students/<int:student>/subjects/<string:subject>/csv")
def get_student_lessons_subject(subject, student):
    if int(student) not in range(111, 60821):
        raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
    if student not in db.students.distinct("student"):
        raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    lessons = db.student_lessons.find_one({"student": student, "dataset": dataset}, {"_id":0, "lessons":0}) 
    progression = []
    for n in lessons["lesson_ids"]:
        progression.extend(list(db.student_lesson.find({"lesson":n},{"records":0, "_id":0})))
    if len(lessons) == 0:
        raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
    return convert_raw_data({"data":sorted(progression, key=lambda x:x["lesson"])})

@csv_progression.route("/lessons/students/<int:student>/subjects/<string:subject>/last/csv")
def get_student_last_lesson( subject, student):
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    lessons = db.student_lessons.find_one({"student": student, "dataset": dataset}, {"_id":0, "lessons":0}) 
    last_lesson_id = lessons["lesson_ids"][-1]
    if len(chapters) == 0:
        raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
    last_lesson = db.student_lesson.find_one({"student": student, "dataset": dataset, "lesson":last_lesson_id}, {"_id":0, "records":0})
    last_lesson["start"] = convert_datetime_to_str(last_chapter["start"]) 
    last_lesson["end"] = convert_datetime_to_str(last_chapter["end"])
    return convert_raw_data({"data": last_lesson})

@csv_progression.route("/lessons/classrooms/<int:classroom>/subjects/<string:subject>/csv")
def get_classroom_subject_chapter( classroom, subject):
    if int(classroom) not in range(1, 60):
        raise abort(406, "L'identifiant de la classe `{}` est incorrect, vérifiez votre identifiant.".format(classroom))
    if int(classroom) not in db.students.distinct("classroom"):
        raise abort(404, "La classe `{}` n'a pas été trouvée".format(classroom))
    if subject not in ["letters", "numbers"]:
        raise abort(406, "Le sujet `{}` n'existe pas encore.".format(subject))
    if subject == "letters":
        subject_name = "Français"
        dataset = "gp"
    else:
        subject_name = "Maths"
        dataset = "numbers"
    dataset_ref = db.datasets.find_one({"dataset": dataset})
    if dataset_ref is None:
        raise abort(406, "Le nom du dataset `{}` est incorrect.".format(dataset))
    else:
        if dataset_ref["subject"] == "letters":
            subject_name = "Français"
        else:
            subject_name = "Maths"
    lessons_refs = list(db.path.find({"dataset": dataset}, {"_id":0}))
    class_lessons = list(db.student_lessons.find({"classroom": classroom, "dataset": dataset}, {"_id":0, "lessons":0}))
    if len(class_lessons) == 0:
        raise abort(404, "Pas de données pour la classe {} sur le sujet {}.".format(classroom, subject))
    return convert_raw_data({"data": sorted(class_lessons, key=lambda x:x["student"])})
        
