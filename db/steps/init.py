#!/usr/bin/env python3
import os
import pymongo
# import logging
# from logging.handlers import RotatingFileHandler

from collections import Counter

from settings import RAW_DIR, CLEAN_DIR, REFERENCES_DIR, ARCHIVED_DIR, LOG_DIR
from settings.files import REFERENCES_FILES

from utils import timeit, read_csv, read_json, dir_empty
from utils import dbtable_to_csvfile, connect, dir_exists
from utils import dump, dump_and_drop

__doc__="Init database with references and clean files stored in datasets/clean/"

CHAPTER_COLORS = {
	1: "#9670E0",
	2: "#FFE822",
	3: "#ED9AB5",
	4: "#A84349",
	5: "#3F32A5",
	6: "#9FF9AB",
	7: "#C3C2C4",
	8: "#FFAF57",
	9: "#50FEE4",
	10: "#7AD1FF",
	11: "#C3C2C4",
	12: "#FFE822",
	13: "#A84349",
	14: "#ED9AB5",
	15: "#9FF9AB",
	16: "#3F32A5",
	17: "#50FEE4",
	18: "#7AD1FF",
  	19: "#FFAF57",
	20: "#9670E0"
	}


def generate_files_list(source_dir, report=False):
    '''
    iterate throught files from source_dir
    yield [dataset_name, student_id, classroom_id, kid_id, tablet_id, filepath]
    if files set to True:
        insert report on files
    '''
    db = connect()
    if report:
        db.files.drop()
    
    for _filename in os.listdir(source_dir):
        try:
            student_id, dataset_name = _filename.split(".")[0].split("-")
            
            classroom_id, kid_id, tablet_id = student_id.split("_")
            student_id = int("".join(student_id.split("_")))
            
            if not os.path.isdir(_filename):    
                if report:
                    db.files.insert({"filename": _filename, "dataset": dataset_name, "student":int(student_id), "status":True})
                yield [
                    dataset_name, 
                    int(student_id), 
                    int(classroom_id),
                    int(kid_id),
                    int(tablet_id),
                    os.path.join(source_dir, _filename)]
        except ValueError:
            status = False
            msg = "Init Error: Filename {} doesn't match the pattern <classroomId_kidId_tabletId-datasetName.extension>. File will not be indexed.".format(_filename)
            # logger.warning(msg)
            if report:
                db.files.insert({"filename": _filename, "dataset": None, "student":None, "status":False, "msg":msg})
            pass
    return True, db.files.count()

@timeit
def insert_datasets(source_dir, debug=False):
    DATASETS = {
        "assessments_language": {"slug":"assessments","subject":"letters", "target":"chapter"},
        "assessments_maths": {"slug":"assessments","subject":"numbers", "target":"chapter"},
        "gp": {"slug":"gp", "subject":"letters", "target":"lesson"},
        "numbers": {"slug":"nb", "subject":"numbers", "target":"lesson"},
        "gapfill_lang": {"slug":"gapfill", "subject":"letters", "target": "words"}
    }
    status = True
    msg = ""
    db = connect()
    db.datasets.drop()
    db.datasets.create_index(
        [("dataset", pymongo.DESCENDING)],
        unique=True
    )
    datasets_files = dict(Counter([n[0] for n in generate_files_list(source_dir, True)]))
    for k,v in DATASETS.items():
        count = datasets_files[k]
        if count == 0:
            status = False
            msg =  "No files found for dataset `{}`".format(k)
            # logger.warning("No files found for dataset `{}`".format(k))
        v["msg"] = msg
        v["status"] = status
        v["files_nb"] = count
        v["dataset"] = k
        try:
            db.datasets.insert(v)
        except Exception as e:
            msg = "Insert dataset {} failed with Exception: {}".format(v, e)
            return False, msg
    if list(datasets_files.keys()) != list(DATASETS.keys()):
        undeclared_datasets = set(datasets_files.keys()).difference(set(DATASETS.keys()))
        for n in undeclared_datasets:
            dataset = { "slug" : n, "subject" : None, "target" : None, "files_nb" : 0, "dataset" : n, "status":False, "msg":"Undeclared dataset"}
            db.datasets.insert(dataset)
        status = False
        msg = "Found undeclared datasets in files: {}. They will NOT be inserted.".format("`,`".join(undeclared_datasets))
    # dbtable_to_csvfile(REFERENCES_FILES["datasets"][0], table_name="datasets")
    msg = "{} datasets declared in which {} are false".format(db.datasets.count(), db.datasets.count({"status":False}))
    return status, msg

@timeit
def insert_students(source_dir, reference_dir):
    ''' 
    create table students from list of files found
     - group set to None
     - files_nb is set to value of the counter dict students_files 
     - lang set to 'fr'
    iterate from references file studentid_group.csv
    if student exists:
     - set group 
     - set status to True
    if student doesn't exists :
     - set group
     - set file_nb to None
     - set status to False
    
    '''
    db = connect()
    db.students.drop()
    student_files_count = dict(Counter([n[1] for n in generate_files_list(source_dir)]))
    student_files = set([tuple(n[1:-1]) for n in generate_files_list(source_dir)])
    status = True
    msg = ""
    for student in student_files:
        student = [int(n) for n in student]
        ref_student = dict(zip(["student", "classroom" , "tablet", "kid"], student))
        ref_student["group"] = None
        ref_student["files_nb"] = student_files_count[ref_student["student"]]
        ref_student["_id"] = ref_student["student"]
        ref_student["status"] = False
        ref_student["lang"] = "fr"
        db.students.insert(ref_student)

   
    sourcef = os.path.join(reference_dir, "studentid_group.csv")    
    for student  in read_csv(sourcef, delimiter=","):
        existing_student = db.students.find({"student": int(student["ID"])})
        if existing_student is not None:
            db.students.update({"student": int(student["ID"])}, {"$set": {"group": student["group"], "status":True}})
        else:
            db.students.insert({
                "_id":int(student["ID"]),
                "student": int(student["ID"]),
                "classroom": int(student["classroomID"]),
                "kid": int(student["kidID"]),
                "group": student["group"],
                "files_nb": None,
                "status": False
            })
    msg = "{} students in which {} are False".format(db.students.count(), db.students.count({"status": False}))
    return status, msg
@timeit
def insert_gapfill_path(reference_dir):
    db = connect()
    status = True
    msg = ""
    words_files = [f for f in os.listdir(reference_dir) if "stimuli_wordsorting.csv" in f]
    for f in words_files:
        lang = f.split("_")
        if len(lang) == 1:
            #default one
            lang = "fr"
        else:
            lang = lang[0]
        sourcef = os.path.join(reference_dir, f)
        header_file = ["chapter", "stimuli", "type"]
        row_counter = 0
        for row in read_csv(sourcef, delimiter=","):
            line = {k:row[k] for k in header_file} 
            line["lesson"] = None
            line["chapter"] = int(line["chapter"])
            line["subject"] = "letters"
            line["dataset"] = "gapfill_lang"
            line["lang"] = lang
            db.path.insert(line)
            row_counter +=1
        db.references.insert({"filename":sourcef, "status":True, "nb_records":row_counter})
    msg = "{} references inserted in which {} are False".format(db.references.count(), db.references.count({"status":False})) 
    return status, msg

@timeit
def insert_gp_path(reference_dir):
    db = connect()
    status = True
    msg = ""
    subject = "letters"
    words_files = [f for f in os.listdir(reference_dir) if "gp_progression_tag.csv" in f]
    for f in words_files:
        lang = f.split("_")
        if lang[0] == "gp":
            #default one
            lang = "fr"
        else:
            lang = lang[0]
        sourcef = os.path.join(reference_dir, f)
        header_file = ["gp", "grapheme", "phoneme", "lesson", "chapter", "tag", "CV"]
        row_counter = 0
        for row in read_csv(sourcef):
            line = {k:row[str(k.upper())] for k in header_file} 
            ref = {
                "chapter": int(line["chapter"]),
                "chapter_color": CHAPTER_COLORS[int(line["chapter"])],
                "lesson": int(line["lesson"]),
                "subject": subject,
                "dataset": "gp",
                "visualaudio": line["gp"],
                "visual": line["grapheme"],
                "audio": line["phoneme"],
                "CV": line["CV"],
                "tag": line["tag"],
                "lang": lang
            }
            db.path.insert(ref)
            row_counter +=1
        db.references.insert({"filename":sourcef, "status":True, "nb_records":row_counter})
    msg = "{} references inserted in which {} are False".format(db.references.count(), db.references.count({"status":False})) 
    return status, msg

@timeit
def insert_sorting_path(reference_dir):
    db = connect()
    status = True
    msg = ""
    subject = "numbers"
    dataset = "assessments_maths"
    sourcef = os.path.join(reference_dir, "sorting.json")
    data = read_json(sourcef)
    row_counter = 0
    for k, v in data.items():
        db.path.insert_one({"tag":k, "chapter": v["CHAPTER"], "higher":v["HIGHER NUM"],"lower": v["OTHER NUM"], "lesson": None, "dataset":dataset, "subject":subject})
        row_counter +=1
    db.references.insert({"filename":sourcef, "status":True, "nb_records":row_counter})
    return status, msg
@timeit
def insert_nb_path(reference_dir):
    db = connect()
    status = True
    msg = ""
    subject = "numbers"
    sourcef = os.path.join(reference_dir, "nb_progression_tag.csv")
    row_counter = 0
    for row in read_csv(sourcef):
        try:
            tag = int(row["VALUE"])
        except ValueError:
            # No chapter 13
            continue
        line = {}
        line["lesson"] = int(row["LESSON"]) 
        line["chapter"] = int(row["CHAPTER"])
        line["visual"] = int(row["VALUE"])
        line["chapter_color"] = CHAPTER_COLORS[int(line["chapter"])]
        try:
            line["audio"] = line["visual"]
        except ValueError:
            line["audio"] = line["visual"]
        
        try:
            line["tag"] = int(row["VALUE"])
        except ValueError:
            line["tag"] = int(line["visual"])
        line["subject"] = subject
        line["dataset"] = "numbers"
        line["visualaudio"] = "-".join([str(line["visual"]), str(line["audio"])])
        db.path.insert(line)
        row_counter +=1
    db.references.insert({"filename":sourcef, "status":True, "nb_records":row_counter})
    msg = "{} references inserted in which {} are False".format(db.references.count(), db.references.count({"status":False})) 
    return status, msg

@timeit
def insert_path(reference_dir):
    '''
    insert step into path table
    '''
    status = True
    msg = ""    
    db = connect()
    db.path.drop()
    db.references.drop()
    insert_gapfill_path(reference_dir)
    insert_gp_path(reference_dir)
    insert_nb_path(reference_dir)
    # not necessary anymore
    #insert_sorting_path(reference_dir)
    for subject in ["letters", "numbers"]:
        sourcef = os.path.join(reference_dir, "{}_games_lesson.csv".format(subject))
        row_counter = 0    
        for line in read_csv(sourcef, delimiter="\t", encoding="utf-8-sig"):
            games = [line["1"], line["2"], line["3"]]
            db.path.update({"lesson":int(line["LESSON"]), "subject":subject},{'$set': {'games': games}})
            row_counter +=1
        db.references.insert({"filename":sourcef, "status":True, "nb_records":row_counter})
    msg = "{} references inserted in which {} are False".format(db.references.count(), db.references.count({"status":False})) 
    return status, msg



@timeit
def init(dirs, archived=True):
    statuses, msgs = [], []
    if not dir_exists("logs"):
        os.makedirs("logs")
    db = connect()
    clean_dir = dirs["to"]
    ref_dir = dirs["ref"]
    archived_dir = dirs["old"]
    if dir_empty(dirs["to"]):
        msg = "No files found found in {}. Aborting.".format(dirs["to"])
        # logger.critical(msg)
        return False, msg
    
    if archived is True:
        if not dir_exists(archived):
            os.makedirs(archived)
        # dump(archived_dir)
        dump_and_drop(archived_dir)
     
    insert_datasets(clean_dir, True)
    # print(status, msg)
    # statuses.append(status)
    # msgs.append(msg)
    insert_students(clean_dir, ref_dir)
    # msgs.append(msg)
    # statuses.append(status)
    insert_path(ref_dir)
    # statuses.append(status)
    # msgs.append(msg)
    # print(status, msg)
    return True, ""
    
if __name__ == "__main__":
    # dirs = {"to":CLEAN_DIR, "ref":REFERENCES_DIR, "old":ARCHIVED_DIR}
    # init(dirs, False)
    pass