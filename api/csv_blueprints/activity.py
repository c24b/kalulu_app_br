from flask import Blueprint, render_template

from flask_restx import abort
from bson import json_util

import json
import time
import itertools
from utils.db import connect
from utils import convert_datetime_to_str, convert_raw_data, get_lesson_nb

csv_activity = Blueprint('activity', __name__, url_prefix='/activity', template_folder='../templates')
db = connect()

@csv_activity.route("/datasets/<dataset>/csv")
def get_dataset_activity(dataset):    
    if dataset not in db.datasets.distinct("dataset"):
        status = False
        code = 406
        msg = "Le nom du dataset {} est incorrect.".format(dataset)
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    if db.student_dataset.count_documents({}) == 0:
        status = False
        code = 500
        msg = "Table student_dataset is empty. Please contact your adminstrator"
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    else:
        student_datasets = list(db.student_dataset.find({"dataset": dataset}, {"_id": 0, "records": 0}))
        if len(student_datasets) == 0:
            status = False
            code = 404
            msg = "Aucune donnée disponible pour le dataset {}.".format( dataset)
            #return render_template('error.html', code=code, msg=msg)
            return abort(code, msg)
        activity = []
        for student_dataset in student_datasets: 
            
            #formatting time from Mongo ISO to python str
            timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
            # student_dataset["start"] = start
            # student_dataset["end"] = end
            # student_dataset["timespent_sec"] = student_dataset["timespent"]
            del student_dataset["days"]
            del student_dataset["start"]
            del student_dataset["end"]
            del student_dataset["sequences"]
            # del student_dataset["records"]
            student_dataset["timespent"] = timespent
            if student_dataset["subject"] == "letters":
                subject = "letters"
                subject_name = "Français"
            else:
                subject = "numbers"
                subject_name = "Maths"
            student_dataset["subject_name"] = subject_name        
            activity.append(student_dataset)
        status = True
        code = 200
        msg = convert_raw_data({"data":activity})
        return msg

@csv_activity.route("/subjects/<subject>/csv")
def get_subject_activity(subject):    
    if subject not in db.datasets.distinct("subject"):
        status = False
        code = 406
        msg = "Le nom du sujet {} est incorrect.".format(subject)
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    if db.student_subject.count_documents({}) == 0:
        status = False
        code = 500
        msg = "Table student_subject is empty. Please contact your adminstrator"
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    else:
        student_datasets = list(db.student_subject.find({"subject": subject}, {"_id": 0, "records": 0}))
        if len(student_datasets) == 0:
            status = False
            code = 404
            msg = "Aucune donnée disponible pour le dataset {}.".format( dataset)
            #return render_template('error.html', code=code, msg=msg)
            return abort(code, msg)
        activity = []
        for student_dataset in student_datasets: 
            #formatting time from Mongo ISO to python str
            timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
            student_dataset["timespent_sec"] = student_dataset["timespent"]
            student_dataset["timespent"] = timespent
            del student_dataset["days"]
            del student_dataset["start"]
            del student_dataset["end"]
            # del student_dataset["sequences"]
            if student_dataset["subject"] == "letters":
                subject = "letters"
                subject_name = "Français"
            else:
                subject = "numbers"
                subject_name = "Maths"
            student_dataset["subject_name"] = subject_name
            student_dataset["datasets"] = "|".join(student_dataset["datasets"])
            student_dataset["timespent_by_dataset"] = "|".join([str(n) for n in student_dataset["timespent_by_dataset"]])        
            activity.append(student_dataset)
        status = True
        code = 200
        msg = convert_raw_data({"data":activity})
        return msg

@csv_activity.route("/students/<student>/datasets/<dataset>/csv")
def get_student_dataset_activity( student, dataset):    
    db = connect()
    try:
        student = int(student)
    except ValueError:
        status = False
        code = 406
        msg = "L'identifiant de l'élève {} est incorrect.".format(student)
        # return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
        # return abort(406, )
    if int(student) not in range(111, 60821):
        status = False
        code = 406
        msg = "L'identifiant de l'élève {} est incorrect.".format(student)
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    if int(student) not in db.students.distinct("student"):
        status = False
        code = 404
        msg = "L'élève {} n'a pas été trouvé.".format(student)
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    if dataset not in db.datasets.distinct("dataset"):
        status = False
        code = 406
        msg = "Le nom du dataset {} est incorrect.".format(dataset)
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    if db.student_dataset.count_documents({}) == 0:
        status = False
        code = 500
        msg = "Table student_dataset is empty. Please contact your adminstrator"
        #return render_template('error.html', code=code, msg=msg)
        return abort(code, msg)
    else:
        student_dataset = db.student_dataset.find_one(
                {"student": student, "dataset": dataset}, {"_id": 0, "records": 0})
        if student_dataset is None:
            status = False
            code = 404
            msg = "Aucune donnée disponible pour l'élève {} et le dataset {}.".format(student, dataset)
            #return render_template('error.html', code=code, msg=msg)
            return abort(code, msg)
        #formatting time from Mongo ISO to python str
        if student_dataset["start"] is not None:
            start = convert_datetime_to_str(student_dataset["start"])
        else:
            start == None
        if student_dataset["end"] is not None:
            end = convert_datetime_to_str(student_dataset["end"])
        else:
            end == None
        timespent = time.strftime('%H:%M:%S', time.gmtime(student_dataset["timespent"]))
        student_dataset["start"] = start
        student_dataset["end"] = end
        student_dataset["timespent_sec"] = student_dataset["timespent"]
        student_dataset["timespent"] = timespent
        if student_dataset["subject"] == "letters":
            subject = "letters"
            subject_name = "Français"
        else:
            subject = "numbers"
            subject_name = "Maths"
        student_dataset["subject_name"] = subject_name        
        status = True
        code = 200
        msg = convert_raw_data({"data":student_dataset})
        return msg
        
            
            
@csv_activity.route("/students/<student>/subjects/<subject>/csv")
def get_student_subject_activity( student, subject):
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
                {"student": student, "subject": subject}, {"_id": 0, "records": 0, "days":0}
                )
        if student_subject is None:
            return abort(404, "Aucune donnée disponible pour l'élève {} en {}.".format(student, subject_name))
        timespent = time.strftime('%H:%M:%S', time.gmtime(student_subject["timespent"]))
        student_subject['timespent'] = timespent
        del student_subject["start"]
        del student_subject["end"]
        print(student_subject)
        student_subject["datasets"] = "|".join(student_subject["datasets"])
        student_subject["timespent_by_dataset"] = "|".join([str(n) for n in student_subject["timespent_by_dataset"]])
        if student_subject["subject"] == "letters":
            student_subject['subject_name'] = "Français"
        else:
            student_subject['subject_name'] = "Maths"
        status = True
        code = 200
        msg = convert_raw_data({"data":student_subject})
        return msg
        
@csv_activity.route("/students/<student>/subjects/<subject>/info/csv")
def get_student_subject_info( student, subject):
    
    db = connect()
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
    if db.student_dataset.count_documents({}) == 0:
        return abort(500, "Table student_subject is empty.")
    else:
        student_dataset = db.student_subject.find_one(
                {"student": student, "subject": subject}, {"_id": 0, "records": 0})
        if student_dataset is None:
            return abort(404, "Aucune donnée disponible pour l'élève {} et le sujet {}.".format(student, subject))
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
    print(student_dataset["datasets"])
    student_dataset["datasets"] = "|".join([str(n) for n in student_dataset["datasets"]])
    student_dataset["timespent_by_dataset"] = "|".join([str(n) for n in student_dataset["timespent_by_dataset"]])
    # del student_dataset["sequences"]
    del student_dataset["days"]
    status = True
    code = 200
    msg = convert_raw_data({"data":student_dataset})
    return msg
        
@csv_activity.route("/students/<student>/subjects/<subject>/last/csv")
def get_student_subject_last( student, subject):
    '''Here for readability needs we export the raw view of last chapter of student'''
    # @ns_activity.expect(student_subject_model)
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
    if len(student_chapters) == 0:
        return abort(404, "No data for student {}".format(student))
    
    student_last_chapter_id = sorted(student_chapters["chapter_ids"])[-1]
    student_confusion = list(db.student_confusion.find({"subject": dataset, "student": int(student), "chapter": student_last_chapter_id}, {"_id":0}))
    confusion = [(n["target"], n["stimulus"], n["WA_rate"]) for n in student_confusion]
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
            z.append(tag_confused[:2])
            x.append(id)
    y = [student for _ in x]
    infos = {
        "data":{
            "x":x,
            "y":y,
            "z": z,
            "markers": markers,
            "colors": colors
        }
    }

    return convert_raw_data(infos)

    

@csv_activity.route("/classrooms/<classroom>/datasets/<dataset>/csv")
def get_classroom_dataset_activity( classroom, dataset):
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
        convert_datetime_to_str(n["start"]), 
        convert_datetime_to_str(n["end"]), 
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
        "activity": activity
    }
    return convert_raw_data({"data":activity})
        
@csv_activity.route("/classrooms/<classroom>/subjects/<subject>/csv")
def get_classroom_subject_activity( classroom, subject):
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
    headers = ["classroom", "group","student", "datasets","subject","start_date", "end_date", "timespent","timespent_sec", "nb_sequences", "nb_days", "nb_records"]
    activity = [
        dict(zip(headers, [
        n["classroom"],
        n["group"],
        n["student"],
        "|".join(n["datasets"]),
        n["subject"],
        n["start_date"], 
        n["end_date"], 
        
        time.strftime('%H:%M:%S', time.gmtime(n["timespent"])),
        n["timespent_sec"],
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
        "activity": activity
    }
    if len(student_datasets) > 0:
        return convert_raw_data({"data":activity})
    else:
        return abort(404, "Pas de données disponibles pour la  classe {} et le sujet {}.".format(classroom,subject))
