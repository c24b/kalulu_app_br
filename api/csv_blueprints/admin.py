from flask import Blueprint, render_template

from flask_restx import abort
from utils.db import connect
from utils.files import convert_raw_data

csv_admin = Blueprint('admin', __name__, url_prefix="/admin", template_folder='../templates')

# @csv_admin.route("/datasets/csv")
# def getDatasets():
#     db = connect()

#     classroom = list(db.datasets.find({}, {"_id":0}))
#     return convert_raw_data({"data": classroom}) 
        

@csv_admin.route("/classrooms/csv")
def getClassrooms():
    db = connect()
    # for n in db.students.distinct("classroom"):
    
    #     classroom = list(db.students.find("classroom"))
    return convert_raw_data({"data": sorted(db.students.find({}, {"_id":0}), key=lambda x :x["classroom"])}) 
        

@csv_admin.route("/classrooms/<classroom>/csv")
def getClassroom(classroom):
    db = connect()
    # for n in db.students.distinct("classroom"):
    
    #     classroom = list(db.students.find("classroom"))
    return convert_raw_data({"data": sorted(db.students.find({"classroom":int(classroom)}, {"_id":0}), key=lambda x :x["classroom"])}) 
        

@csv_admin.route("/students/csv")
def getStudents():
    ''' Consult the students '''
    db = connect()
    if db.students.count() > 0:
        return convert_raw_data({"data":list(db.students.find())})
    else:
        return abort(404, "No students found")

@csv_admin.route("/students/status/<status>/csv")
def getStudentsStatus(status):
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
    elif status in ["False", "false", "bug", "error", "wrong", "incorrect"]:
        status = False
        students = list(db.students.find({"status": status}))
    else:
        return abort(406, "Status {} is not supported".format(status))
    
    if len(students) > 0:
        return convert_raw_data({"data":students})
    else:
        return abort(404, "No student with status {} has been found.".format(status))

@csv_admin.route("/students/groups/<group>/csv")
def getStudentsGroup(group):
    '''
    VIEW all students belonging to a specific group 
    '''
    db = connect()
    if group == "None" or group == "null":
        group = None
    if group not in db.students.distinct("group"):
        abort(406, "Group `{}` doesn't exists and is not accepted")
    else:
        students = list(db.students.find({"group":group}))
    if len(students) > 0:
        return convert_raw_data({"data":students})
    else:
        return abort(404, "No student with status {} has been found.".format(status))

@csv_admin.route("/students/<student>/csv")
def getStudent(student):
    db = connect()
    if int(student) not in range(110, 60820):
        return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
    if int(student) not in db.students.distinct("student"):
        return abort(404, "L'élève n'a pas été trouvé")
    student_line = db.students.find_one({"_id": int(student)})
    if student_line is  not None:
        return convert_raw_data({"data":student_line})
    else:
        return abort(404, "Aucune donnée disponible pour cet élève pour ce dataset")

@csv_admin.route("/files/csv")
def getFiles():
    db = connect()
    # for n in db.students.distinct("classroom"):
    
    #     classroom = list(db.students.find("classroom"))
    return convert_raw_data({"data": sorted(list(db.files.find({}, {"_id":0})), key=lambda x:x["filename"])}) 


@csv_admin.route("/lessons/csv")
def getLessons():
    db = connect()
    if db.path.count() == 0:
        raise abort(500, "Table path is empty: initialize the database")
    lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}}, {"_id":0}))
    if len(lessons) == 0:
        raise abort(404, "Pas de leçons")
    return convert_raw_data({"data": lessons})

@csv_admin.route("/chapters/csv")
def getChapters():
    db = connect()
    if db.path.count() == 0:
        raise abort(500, "Table path is empty: initialize the database")
    lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}}, {"_id":0}))
    if len(lessons) == 0:
        raise abort(404, "Pas de leçons")
    return convert_raw_data({"data": lessons})

@csv_admin.route("/path/csv")
def getPath():
    db = connect()
    
    if db.path.count() == 0:
        raise abort(500, "Table path is empty: initialize the database")
    path = list(db.path.find({}, {"_id":0}))
    if len(path) == 0:
        raise abort(404, "Pas de path")
    return convert_raw_data({"data": path})


# @csv_admin.route("/lessons/datasets/<string:dataset>/csv")
# def getLessonsDatasetList(datasey):
    
#     dataset_ref = db.path.find_one({"dataset": dataset})
#     if dataset_ref is None:
#         raise abort(406, "Le dataset `{}` n'existe pas".format(dataset))
#     else:
#         if dataset_ref["subject"] == "letters":
#             subject_name = "Français"
#         else:
#             subject_name = "Maths"
#         lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de leçons pour le dataset {}".format(dataset))
#         return convert_raw_data({
#                     "data": lessons, 
#         })
# @csv_admin.route("/lessons/subject/<string:subject>/csv")
# def getLessonsSubjectList(dataset):    
#     dataset_ref = db.path.find_one({"subject": subject})
#     if dataset_ref is None:
#         raise abort(406, "Le sujet `{}` n'existe pas".format(subject))
#     else:
#         if dataset_ref["subject"] == "letters":
#             subject_name = "Français"
#         else:
#             subject_name = "Maths"
#         lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de leçons pour le dataset {}".format(dataset))
#         return convert_raw_data({
#                     "data": lessons 
#                     })

# @csv_admin.route("/chapters/csv")
# def getChaptersList():
#     lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}}, {"_id":0}))
#     if len(lessons) == 0:
#         raise abort(404, "Pas de chapitres")
#     return convert_raw_data({"data": lessons})

# @csv_admin.route("/chapters/subjects/<subject>/csv")
# def getChaptersSubjectList(subject):
#     if subject not in ["letters", "numbers"]:
#         raise abort(406, "Le sujet `{}` n'existe pas".format(subject))
#     else:
#         if subject == "letters":
#             subject_name = "Français"
#         else:
#             subject_name = "Maths"
#     lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#     if len(lessons) == 0:
#         raise abort(404, "Pas de chapitre pour le sujet `{}`".format(subject))
#     return convert_raw_data({"data": lessons})


# @csv_admin.route("/chapters/datasets/<string:dataset>/csv")
# def getChaptersDatasetList(dataset):
#     dataset_ref = db.datasets.find_one({"dataset": dataset})
#     if dataset_ref is None:
#         raise abort(406, "Le dataset `{}` n'existe pas".format(dataset))
#     else:
#         if dataset_ref["subject"] == "letters":
#             subject_name = "Français"
#         else:
#             subject_name = "Maths"
#         lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, "Pas de chapitre pour le dataset {}".format(dataset))
#         return convert_raw_data({"data": lessons})


# @csv_admin.route("/datasets/csv")
# def getDatasets():
#     db = connect()
#     return convert_raw_data({"data":db.datasets.find({}, {"_id": 0})}) 

# @csv_admin.route("/subjects/csv")
# def getSubjects():
#     db = connect()
#     return convert_raw_data({"data": db.datasets.distinct("subject")})
 
#  @csv_progression.route("/lessons/csv", methods=["GET"])
# def get_LessonsList():
#     lessons = list(db.path.find({"lesson":{"$exists": True, "$ne":None}}, {"_id":0}))
#     return convert_raw_data({"data": lessons})

# @csv_progression.route("/chapters/csv", methods=["GET"])
# def get_ChaptersList():
#     chapters = list(db.path.find({"chapter":{"$exists": True, "$ne":None}}, {"_id":0}))
#     return convert_raw_data({"data": chapters})

# @csv_progression.route("/lessons/subjects/<subject>/csv")
# def get_LessonsSubjectList(subject):
#     lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#     if len(lessons) == 0:
#         raise abort(404, u"Pas de leçons pour le sujet {}".format(subject))
#     return convert_raw_data({"data": lessons})

# @csv_progression.route("/lessons/datasets/<string:dataset>/csv")
# def get_LessonsDatasetList(dataset):
#     lessons = list(db.path.find({"lesson":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#     if len(lessons) == 0:
#         raise abort(404, u"Pas de leçons pour le sujet {}".format(subject))
#     return convert_raw_data({"data": lessons})

# @csv_progression.route("/chapters/subjects/<subject>/csv")
# def get_ChaptersSubjectList(subject):
#     if subject not in ["letters", "numbers"]:
#         raise abort(406, "Le sujet `{}` n'existe pas".format(subject))
#     lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "subject": subject}, {"_id":0}))
#     if len(lessons) == 0:
#         raise abort(404, "Pas de chapitre pour le sujet `{}`".format(subject))
#     return {"data": lessons, "subject":subject, "subject_name": subject_name}

# @csv_progression.route("/chapters/datasets/<string:dataset>/csv")
# def get_ChaptersDatasetList(dataset):
#     dataset_ref = db.datasets.find_one({"dataset": dataset})
#     if dataset_ref is None:
#         raise abort(406, u"Le dataset `{}` n'existe pas".format(dataset))
#     else:
#         lessons = list(db.path.find({"chapter":{"$exists": True, "$ne": None}, "dataset": dataset}, {"_id":0}))
#         if len(lessons) == 0:
#             raise abort(404, u"Pas de chapitre pour le dataset {}".format(dataset))
#         return convert_raw_data({"data": lessons})

# @csv_progression.route("/students/<int:student>/datasets/<string:dataset>/csv")
# def get_StudentChaptersDatasetList(student, dataset):
#     if int(student) not in range(111, 60821):
#         raise abort(406, u"L'identifiant de l'élève  `{}` est incorrect. Vérifier son identifiant".format(student))
#     if student not in db.students.distinct("student"):
#         raise abort(404, u"L'élève `{}` n'a pas été trouvé".format(student))
#     dataset_ref = db.datasets.find_one({"dataset": dataset})
#     if dataset_ref is None:
#         raise abort(406, "Le nom du dataset `{}` est incorrect.".format(dataset))
#     else:
#         lessons = list(db.student_chapter.find({"student":student, "dataset": dataset}, {"_id":0, 'records':0}))
#         if len(lessons) == 0:
#             raise abort(404, u"Pas de données pour l'élève {} sur le dataset {}".format(student, dataset))
#         return convert_raw_data({"data": lessons})
    
# @csv_progression.route("/students/<int:student>/subject/<string:subject>/csv")
# def get_StudentChaptersSubjectList(student, subject):
#     if int(student) not in range(111, 60821):
#         raise abort(406, u"L'identifiant de l'élève  `{}` est incorrect. Vérifier son identifiant".format(student))
#     if student not in db.students.distinct("student"):
#         raise abort(404, u"L'élève `{}` n'a pas été trouvé".format(student))
#     chapters = list(db.student_chapter.find({"student": student, "dataset": dataset}, {"_id":0,'records':0})) 
#     if len(chapters) == 0:
#         raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
#     return convert_raw_data({"data": chapters})

# @csv_progression.route("/students/<int:student>/subject/<string:subject>/last/csv")
# def get_StudentLastChaptersSubjectItem(student, subject):
#     if int(student) not in range(111, 60821):
#         raise abort(406, u"L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
#     if student not in db.students.distinct("student"):
#         raise abort(404, u"L'élève `{}` n'a pas été trouvé".format(student))
#     if subject == "letters":
#         subject_name = "Français"
#         dataset = "gp"
#     else:
#         subject_name = "Maths"
#         dataset = "numbers"
#     chapters = db.student_chapters.find_one({"student": student, "dataset": dataset}, {"_id":0}) 
#     last_chapter_id = chapters["chapters_ids"][-1]
#     if len(chapters) == 0:
#         raise abort(404, u"Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
#     last_chapter = db.student_chapter.find_one({"student": student, "dataset": dataset, "chapter":last_chapter_id}, {"_id":0, "chapters":0})
#     return convert_raw_data({"data": last_chapter})

# @csv_progression.route("/classrooms/<int:classroom>/subjects/<string:subject>/csv")
# def get_ClassroomSubjectProgressionList(classroom, subject):
#     if int(classroom) not in range(1, 60):
#         raise abort(406, u"L'identifiant de la classe  `{}` est incorrect. Vérifiez votre identifiant".format(classroom))
#     if subject not in ["letters", "numbers"]:
#         raise abort(406, u"Le nom du sujet `{}` est incorrect.".format(subject))
#     if subject == "letters":
#         dataset = "gp"
#     else:
#         dataset="numbers"
#     if int(classroom) not in db.students.distinct("classroom"):
#         raise abort(404, u"La classe `{}` n'a pas été trouvée".format(classroom))
#     class_lessons = list(db.student_lessons.find({"classroom": classroom, "dataset": dataset}, {"_id":0, "lessons":0}))
#     return convert_raw_data({"data": class_lessons}) 
                
# @csv_progression.route("/classrooms/<int:classroom>/datasets/<string:dataset>/csv")
# def get_ClassroomDatasetProgressionList(classroom, dataset):
#     if int(classroom) not in range(1, 60):
#         raise abort(406, u"L'identifiant de la classe  `{}` est incorrect. Vérifiez votre identifiant".format(classroom))
#     if int(classroom) not in db.students.distinct("classroom"):
#         raise abort(404, u"La classe `{}` n'a pas été trouvée".format(classroom))
#     dataset_ref = db.datasets.find_one({"dataset": dataset})
#     if dataset_ref is None:
#         raise abort(406, u"Le nom du dataset `{}` est incorrect.".format(dataset))
#     else:
#         class_lessons = list(db.student_lessons.find({"classroom": classroom, "dataset": dataset}, {"_id":0, "lessons":0}))
#         if len(class_lessons) == 0:
#             raise abort(404, u"Pas de données pour la classe {} sur le sujet {}".format(classroom, subject))
#         return convert_raw_data({"data": class_lessons}) 