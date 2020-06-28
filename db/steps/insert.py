#!/usr/bin/python3
# encoding: utf-8
__doc__ = '''
Insert from clean directory inside database
'''
import argparse
import json
import logging
import os
import sys
# import time
from datetime import datetime as dt

import pymongo

from settings import LOG_DIR, REF_TABLES, DIRS
from utils import (connect, convert_to_date, convert_to_isodate, dir_empty,
                   dump_and_drop, flatten_records, insert_multi, read_csv,
                   read_json, timeit, check_dirs, check_tables, close)

from .init import generate_files_list



db = connect()
GP_TAGS = {r["visualaudio"]: r["tag"] for r in db.path.find({"dataset":"gp"})}
GP_TAGS[''] = None
NB_TAGS = {int(r["visual"]): int(r["tag"]) for r in db.path.find({"dataset":"numbers"})}
NB_TAGS[''] = None
close()

def insert_gp(_dataset, classroom_id, student_id, abs_filename, update=False, debug=False):
    '''
    insert GP records  into Records
    '''
    db = connect()
    status = True
    msg = ""
    try:
        dataset = read_json(abs_filename)
    except json.decoder.JSONDecodeError:
        status = False
        msg = "{} is corrupted. End file missing. Skipping insertion".format(abs_filename)
        # logger.warning(msg)
        return (status, msg, 0)

    games = set()
    header = None
    student = db.students.find_one({"student":student_id})
    try:
        group = student["group"]
    except KeyError:
        status = False
        msg = '[insert_gp] student {} has no group'.format(student)
        # logger.warning(')
        group = None
    
    values = 0
    records = []
    for key, v in dataset.items():    
        if len(v["records"]) > 0:
            step = db.path.find_one({"visualaudio":key})
            # send to report and call Cassandra
            if step is None:
                msg = "No chapter or lesson found in db.path with visualaudio=`{}`".format(key)
                if not "." in key:
                    step = db.path.find_one({"visual":key.split("-")[0]})
                    if step is None:
                        status = False
                        msg = "No chapter or lesson found in db.path with visual=`{}`".format(key.split("-")[0])
                        # logger.warning('[insert_gp] '+msg)
                        #insert_report(["warning", "insert_gp", abs_filename, "db.records", False, msg, len(v["records"]) ])
                        step = {"chapter":-1, "lesson":-1, "tag": key, "CV": ""}
                # syllabs handling: choose to affect it to first syllab ... :()
                else:
                    # print(key)
                    step = {"chapter":-1, "lesson":-1, "tag": key, "CV": "NA"}
                    # first_syllabs = key.split(".")
                    # step = db.path.find_one({"visualaudio":first_syllabs[0]})       
            game_ids = list(set([n["minigameId"] for n in v["records"]]))
            games.update(game_ids)
            for record in v["records"]:
                try:
                    record["stimulus_tag"] =  GP_TAGS[record["stimulus"]]
                    # print(record["stimulus_tag"])
                except KeyError:
                    status = False
                    msg = '[insert_gp] No tag in path found for stimulus_tag {}'.format(record["stimulus"])
                    # logger.warning(')
                    record["stimulus_tag"] = None            
                record["classroom"] = classroom_id
                record["student"] = student_id
                record["group"] = group
                record["chapter"] = int(step["chapter"])
                record["lesson"] = int(step["lesson"])
                record["tag"] = step["tag"]
                record["target_tag"] = step["tag"]
                record["value"] = key
                record["dataset"] ="gp"
                record["subject"] = "letters"
                record["CV"] = step["CV"]
                record["day"] = convert_to_date(record["unixTime"])
                record["unixTime"] = convert_to_isodate(record["unixTime"])
                record["isClicked"] = int(record["isClicked"] == True)
                record["game"] = str(record["minigameId"])
                del record["minigameId"]
                values += 1
                records.append(record)
    
    try:
        db.records.insert_many(records)
    except Exception as e:
        status = False
        msg = '[insert_gp] fails to insert {} records for student {}. Error  {}'.format(values, student_id, e)
    if values == 0:
        status = False 
        msg = "[insert_gp] has no records for student {}".format(student_id)
    return (status, msg, values)

def insert_nb(_dataset, classroom_id, student_id, abs_filename, update=False, debug=False):
    '''
    insert numbers records into Records
    '''
    try:
        dataset = read_json(abs_filename)
    except json.decoder.JSONDecodeError:
        msg = "[insert_nb()] File {} is corrupted. JSON DECODE ERROR. Skipping insertion".format(abs_filename)
        # logger.warning(msg)
        return (False, msg, 0)
    db = connect()
    status = True
    msg = ""
    values = 0
    student = db.students.find_one({"student":student_id})
    try:
        group = student["group"]
    except KeyError:
        group = None

    header = None
    values = 0
    nb_records = []
    for nb,v in dataset.items():
        records = flatten_records(v)
        if len(records) > 0:
            try:
                step = db.path.find_one({"visual":int(nb)})
            except ValueError:
                step = None
                
            # send to report and call Cassandra
            if step is None:
                msg = "[insert_nb] No chapter or lesson found in db.path with visualaudio=`{}`".format(nb)
                # logger.warning("[insert_nb]"+ msg)
                step = db.path.find_one({"visual":nb.split("-")[0]})
                if step is None:
                    msg = "[insert_nb] No chapter or lesson found in db.path with visual=`{}`".format(nb.split("-")[0])
                    # logger.warning("[insert_nb]"+ msg)
                    step = {"chapter":-1, "lesson":-1, "tag": int(nb)}
            
            for record in records:
                if record["stimulus"] == "":
                    record["stimulus"] = None
                    record["stimulus_tag"] = None
                    
                else:
                    record["stimulus"] = int(record["stimulus"])
                    record["stimulus_tag"] =  NB_TAGS[int(record["stimulus"])]
                record["tag"] = int(nb)
                record["value"] = int(nb)
                record["classroom"] =  classroom_id
                record["student"] = student_id
                record["group"] = group
                record["target"] = int(nb)                
                record["target_tag"] = step["tag"]
                record["chapter"] =  step["chapter"]
                record["lesson"] =  step["lesson"]
                record["dataset"] = "numbers"
                record["subject"] =  "numbers"
                record["isClicked"] = int(record["isClicked"] == True)
                record["day"] = convert_to_date(record["unixTime"])
                record["unixTime"] = convert_to_isodate(record["unixTime"])
                record["game"] = str(record["minigameId"]) 
                record["CV"] = "N"
                del record["minigameId"]
                nb_records.append(record)
                values +=1
    if len(nb_records) > 0 and values > 0:
        db.records.insert_many(nb_records)    
    else:
        status, msg = False, "[insert_nb()] No records inserted in dataset numbers for student {}".format(student_id)
        # logger.info("[insert_gp]"+ msg)
    #     return(status, msg, 0)
    # return(status, msg, values)
    return status, msg, values
    
def insert_assessments(_dataset, classroom_id, student_id, abs_filename, update=False, debug=False):
    '''
    insert assessments
    '''
    header = None
    msg = ""
    records = []
    nb_values = 0
    db = connect()
    status = True
    msg = ""
    # rank = db.path.find_one({"subject": _dataset["subject"]}, sort=[("chapter", -1)])
    student = db.students.find_one({"student":student_id})
    if student is None:
        status = False
        msg = "[insert_assessements] student not found {}".format(student_id)
        
    else:
        try:
            group = student["group"]
        except KeyError:
            group = None
 
    with open(abs_filename, "r") as f:
        try:
            for row in f.readlines():
                line = json.loads(row)
                if len(line["records"]) > 0:
                    for record in line["records"]:
                        record.update(
                            {k: v for k, v in line.items() if k != "records"})
                        record["tag"] = record["value"]
                        record["chapter"] = int(record["chapterId"])
                        record["lesson"] = None
                        del record["chapterId"]
                        record.update({
                            "classroom": classroom_id,
                            "student": student_id,
                            "group": group,
                            "dataset": _dataset["dataset"],
                            "subject": _dataset["subject"],
                            "game" : "fish"

                            })
                        if _dataset["subject"] == "letters":
                            record["word"] = record["value"]
                        record["day"] = convert_to_date(record["unixTime"])
                        record["unixTime"] = convert_to_isodate(record["unixTime"])
                        record["assessmentEndTime"] = convert_to_isodate(
                                    record["assessmentEndTime"])
                        try:
                            records.append(record)
                            nb_values +=1 
                        except pymongo.errors.DuplicateKeyError:
                            pass
            if nb_values == 0:
                status = False
                msg = "[insert_assessements] No records found for {}".format(abs_filename)
            db.records.insert_many(records)
        except json.decoder.JSONDecodeError:
            msg = "{} is corrupted. JSON DECODE Error".format(abs_filename)
            # logger.warning("[insert_assessement]"+ msg)
            # insert_report(["error", "insert_assessments", abs_filename, "db.records", False, msg, "" ])
            return (False, msg, 0)
    return(status, msg, nb_values)


def insert_gapfill(_dataset, classroom_id, student_id, abs_filename, update=False, debug=False):
    '''insert gapfill into records'''
    status = True
    msg = ""
    try:
        dataset = read_json(abs_filename)
    except json.decoder.JSONDecodeError:
        msg = "[insert_gapfill] {} is corrupted. JSON Decode Error.".format(abs_filename)
        logger.critical(msg)    
        return (False, msg, 0)
    header = None
    nb_values = 0
    records = []
    db = connect()
    student = db.students.find_one({"student":student_id})
    try:
        group = student["group"]
    except KeyError:
        group = None
    for chap, v in dataset.items():
        if len(v["records"]) > 0:
            for record in v['records']:
                # chapter = get_lesson_from_stimulus(record["target"])
                record.update({
                        "classroom": classroom_id,
                        "student": student_id,
                        "group": group,
                        "word_nb": int(chap),
                        # "chapter": None,
                        "chapter": int(chap),
                        "subject":"letters",
                        "tag": record["target"],
                        "word": record["target"],
                        "value": record["target"],
                        "dataset": _dataset["dataset"],
                        "lesson": None
                        })
                record["day"] = convert_to_date(record["unixTime"]) 
                record["unixTime"] = convert_to_isodate(record["unixTime"])
                record["game"] = str(record["minigameId"]) 
                record["isClicked"] = int(record["isClicked"] == True)
                del record["minigameId"]
                del record["targetId"]
                record["elapsedTime"] = float(record["elapsedTime"])
                records.append(record)
                nb_values +=1
    try:
        db.records.insert_many(records)
    except Exception as e:
        status = False
        msg = "[insert_assessements()] failed to insert records for student {}. Error:{}".format(student_id, e)
    if nb_values == 0:
        status = False
        msg = "[insert_assessements()] . No records found for {}".format(student_id)
    return(status, msg, nb_values)


@timeit
def insert_records(source_dir, update=False, debug =False):
    '''main function to launch insert function varying from dataset name/type''' 
    # logger.info("INSERT RECORDS")
    db = connect()
    status = True
    msg = ""
    total = 0
    sorted_dataset_list = sorted(list(generate_files_list(source_dir, False)))
    if len(sorted_dataset_list) == 0:
        status = False
        msg = " No dataset file found in {}. Abort.".format(source_dir)
        logger.critical("[insert_records]"+ msg)
        # sys.exit(1, "No file found in {}. Cancel operations".format(source_dir))
        return status, msg, 0
    else:
        for dataset_name, student_id,classroom_id,kid_id, tablet_id, target_file in sorted_dataset_list:
            if db.datasets.count() == 0:
                insert_datasets(source_dir, debug=debug)
            dataset = db.datasets.find_one({"dataset": dataset_name})
            if dataset is not None:
                try:
                    func_str = "insert_{}".format(dataset["slug"])
                    func = getattr(sys.modules[__name__], func_str)
                    func(dataset, classroom_id, student_id,
                        target_file, update, debug)
                    # total += nb_records
                    db.files.update_one(
                        {"dataset":dataset["dataset"], "student": int(student_id)}, 
                        {
                            "$set": {
                                "status": status, 
                                "message": msg, 
                                "level": "info",
                                "nb_records": nb_records}
                        }
                    )
                except Exception as e:
                    func_str = "insert_{}".format(dataset["slug"])
                    msg = "Exception in {}: {}".format(func_str, e)
                    db.files.update_one({"dataset":dataset["dataset"], "student": int(student_id)}, 
                        {"$set": {
                            "status": False, 
                            "level": "error",
                            "message": "In {} function : {}, Exception log {}".format(os.path.basename(__file__),func_str,str(e)), 
                            "nb_records": 0
                            }
                        })
                    pass            
    return True, msg, db.records.count({"dataset":"numbers"})

@timeit
def insert(dirs):
    '''
    ``insert()`` populate database from source_dir and reference_dir:    
    - insert_records
    - insert_games
    '''
    #check directories
    
    status, msg = check_dirs(dirs, ["ref", "to"])
    if status is False:
        logger.critical(msg)
        return status, msg
    
    #check tables
    for table in REF_TABLES:
        status, msg = check_tables(REF_TABLES)
        if status is False:
            return status, msg   
    db.records.drop()
    insert_records(dirs["to"])
    if status is False:
        logger.critical(msg)
        return status, msg
    # else:
    #     msg = msg + " {} record inserted".format(count)
    insert_games()
    return status, msg
    
@timeit    
def insert_games(debug=False):
    # logger.info("INSERT GAMES") 
    db = connect()
    db.games.drop()
    # print("Games")
    for dataset in db.datasets.distinct("dataset"):
        games = db.records.distinct("game", {"dataset": dataset})
        if len(games) > 0:
            #correction of monkeys
            # insert game='monkey' for dataset 'numbers' where game is a number
            if dataset == "numbers":
                monkeys_gids = [g for g in games if g.isdigit()]
                # print("Correction of", len(monkeys_gids), "games")
                for g_id in [g for g in games if g.isdigit()]:
                    db.records.update_many({"game": g_id}, {"$set": {"game": "monkey"}})
            # too long 7 min in my computer
            # for game in games:
            #     count = db.records.count({"game":game, "dataset":dataset})
            #     db.games.insert_one({"game":game, "dataset":dataset,"records_nb":count})    
    return True, ""

if __name__ == "__main__":
    insert(DIRS)
    quit()