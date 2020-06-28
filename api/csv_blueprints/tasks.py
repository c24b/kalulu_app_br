from flask import Blueprint, render_template, abort
from utils.db import connect
from utils.files import convert_raw_data

csv_tasks = Blueprint('tasks', __name__, url_prefix='/tasks')
db = connect()
@csv_tasks.route("/confusion/students/<int:student>/subjects/<string:subject>/csv", methods=["GET"])
def get_StudentDatasetConfusion(student, subject):
    if subject =="letters":
        dataset = "gp"
    else:
        dataset = "numbers"
    print(subject)
    chapter_confusion = list(db.student_confusion.find(
        {"student": student, "subject": subject}, {"_id":0,"title":0, "lessons":0}))
    # print(chapter_confusion)
    headers = list(chapter_confusion[0].keys())
    confusion = []
    for n in sorted(chapter_confusion, key = lambda x: x["chapter"]):
        n["timespent"] = round(n["timespent"], 2)
        if n["stimulus"] == n["target"]:
            n["miss_rate"] = n["WA_rate"]
            n["hit_rate"] = n["CA_rate"]
            n["fa_rate"] = None
            n["cr_rate"] = None
        else:
            n["miss_rate"] = None
            n["hit_rate"] = None
            n["fa_rate"] = n["WA_rate"]
            n["cr_rate"] = n["CA_rate"]
        n["dataset"] = dataset
        confusion.append(n)
    return convert_raw_data({"data": confusion})


@csv_tasks.route("/confusion/subjects/<string:subject>/csv", methods=["GET"])
def get_DatasetConfusionMatrix(subject):
    if subject =="letters":
        dataset = "gp"
    else:
        dataset = "numbers"
    chapter_confusion = list(db.confusion.find(
        {"subject": subject}, {"_id":0}))
    # headers = list(students[0].keys())
    confusion = []
    for n in chapter_confusion:
        # n["timespent"] = round(n["timespent"], 2)
        if n["stimulus"] == n["target"]:
            n["miss_rate"] = n["avg_WA_rate"]
            n["hit_rate"] = n["avg_CA_rate"]
            n["fa_rate"] = None
            n["cr_rate"] = None
        else:
            n["miss_rate"] = None
            n["hit_rate"] = None
            n["fa_rate"] = n["avg_WA_rate"]
            n["cr_rate"] = n["avg_CA_rate"]
        n["dataset"] = dataset
        confusion.append(n)
    return convert_raw_data({"data": confusion})

@csv_tasks.route("/decision/students/<int:student>/subjects/<subject>/csv")
def get_student_decision(student, subject):    
    decision = list(db.student_decision.find({"student": int(student), "subject": subject},{"_id": 0}))
    return convert_raw_data({"data": decision})