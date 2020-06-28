import unittest
import random
import pymongo
import requests
# from sshtunnel import SSHTunnelForwarder
from settings.api import API_URL
from settings.database import DB_NAME, DB_HOST, DB_PORT

class TestStudentDecision(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_decision"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.api_endpoint = "{}/tasks/confusion/".format(API_URL)
    
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({"chapter":{"$ne": "average"}}), 32915)
        self.assertEqual(self.coll.count_documents({"chapter":"average"}), 6834)
        self.assertEqual(self.coll.count_documents({}), 32915+6834)
    def test_count_chapters(self):
        #21 because average
        self.assertEqual(len(self.coll.distinct("chapter")), 21)
        self.assertIn("average", self.coll.distinct("chapter"))
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"numbers"})), 21)
        self.assertIn("average", self.coll.distinct("chapter",{"subject":"numbers"}))
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"letters"})), 14)
        self.assertIn("average", self.coll.distinct("chapter",{"subject":"letters"})) 

    def test_count_subjects(self):
        self.assertEqual(len(self.coll.distinct("subject")), 2)
        self.assertEqual(self.coll.count_documents({"subject":"numbers", "chapter": {"$ne":"average"}}), 9770)
        self.assertEqual(self.coll.count_documents({"subject":"numbers", "chapter": "average"}), 1600)
        self.assertEqual(self.coll.count_documents({"subject":"numbers"}), 1600+9770)
        self.assertEqual(self.coll.count_documents({"subject":"letters","chapter": "average"}), 5234)
        self.assertEqual(self.coll.count_documents({"subject":"letters","chapter": {"$ne":"average"}}), 23145)
        self.assertEqual(self.coll.count_documents({"subject":"letters"}), 5234+23145)

    def test_count_students(self):
        # 782 because only not guests
        self.assertEqual(len(self.coll.distinct("student")), 782)
       
    def test_record_numbers(self):
        record_model = {
            "classroom" : 25,
            "student" : 2561,
            "chapter" : 4,
            "subject" : "numbers",
            "distance" : 2,
            "higher" : [
                "3"
            ],
            "lower" : [
                "1"
            ],
            "nb_sequences" : 2,
            "timespent" : 30.194227,
            "CA" : 1,
            "nb_records" : 13,
            "CA_rate" : 0.21,
            "median_time_reaction" : 1.707746
        }
        for record in self.coll.find({"subject":"numbers", "chapter":{"$ne":"average"}}, {"_id":0}).limit(5):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                self.assertEqual(type(v), type(record[k]), k)
    def test_record_average_numbers(self):
        pass

    def test_record_letters(self):
        record_model = {
            "student" : 111,
            "classroom" : 1,
            "chapter" : 2,
            "nb_letters" : 2,
            "type" : "pseudoword",
            "elapsedTimes" : [
                2.006883,
                0.90251,
                19.673519,
                5.688268,
                1.319648,
                1.990466,
                1.172185,
                0.986166,
                1.255789,
                0.80415,
                4.349272,
                1.072165,
                1.254194,
                3.363314,
                2.677374,
                1.555156,
                1.173747,
                1.391735,
                0.804222,
                1.840921
            ],
            "median_time_reaction" : 1.3556914999999998,
            "words" : [
                "ul",
                "um",
                "ua"
            ],
            "subject" : "letters"
        }
        for record in self.coll.find({"subject":"letters", "chapter":{"$ne":"average"}}, {"_id":0}).limit(5):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                self.assertEqual(type(v), type(record[k]), k)
            self.assertIn(record["type"], ["word", "pseudoword"])

    def test_record_average_letters(self):
        record_model = {
            "chapter" : "average",
            "classroom" : 38,
            "median_time_reaction" : 1.8851585,
            "nb_letters" : 2,
            "student" : 3835,
            "subject" : "letters",
            "type" : "pseudoword"
        }
        for record in self.coll.find({"subject":"letters", "chapter":"average"}, {"_id":0}).limit(5):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                self.assertEqual(type(v), type(record[k]))

class TestStudentDecisionMatrix(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_decision_matrix"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/tasks/decision/".format(API_URL)
    
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 1442)

    def test_count_subjects(self):
        self.assertEqual(len(self.coll.distinct("subject")), 2)
        self.assertEqual(self.coll.count_documents({"subject":"numbers"}), 767)
        self.assertEqual(self.coll.count_documents({"subject":"letters"}), 675)
    def test_count_students(self):
        # 782 because only not guests
        self.assertEqual(len(self.coll.distinct("student")), 782)
    def test_numbers_record(self):
        record_model = {
            "classroom" : 7, 
            "matrix" : [ 
                [ 3, [ [ [ 1, 2 ], [ [ 1, 2.62 ], [ 2, 2.25 ] ] ] ] ], 
                [ 6, [ [ [ 1, 2 ], [ [ 1, 2.16 ], [ 2, 2.07 ] ] ] ] ], 
                [ 9, [ [ [ 1, 2 ], [ [ 1, 1.96 ], [ 2, 1.57 ] ] ] ] ], 
                [ 7, [ [ [ 1, 2 ], [ [ 1, 2.01 ], [ 2, 1.59 ] ] ] ] ], 
                [ 2, [ [ [ 1, 2 ], [ [ 1, 1.49 ], [ 2, 1.49 ] ] ] ] ], 
                [ 1, [ [ [ 1, 2 ], [ [ 1, 2.65 ], [ 2, 3.13 ] ] ] ] ], 
                [ 4, [ [ [ 1, 2 ], [ [ 1, 1.87 ], [ 2, 1.91 ] ] ] ] ], 
                [ 8, [ [ [ 1, 2 ], [ [ 1, 1.87 ], [ 2, 1.81 ] ] ] ] ], 
                [ 5, [ [ [ 1, 2 ], [ [ 1, 1.89 ], [ 2, 3.13 ] ] ] ] ] 
            ], 
            "student" : 733, 
            "subject" : "numbers", 
            "graph" : 
                { 
                    "subject" : "numbers", 
                    "data" : { 
                        "1" : { "series" : [ 
                                { 
                                    "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", 
                                    "y" : [ 2.65, 3.13 ], "x" : [ 1, 2 ], "z" : [ [ 1, 2.65 ], [ 2, 3.13 ] ] 
                                } 
                                ], 
                            "xaxis" : [ 1, 2 ] 
                            }, 
                        "2" : { 
                            "series" : [ 
                                { 
                                    "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", 
                                    "y" : [ 1.49, 1.49 ], "x" : [ 1, 2 ], "z" : [ [ 1, 1.49 ], [ 2, 1.49 ] ] 
                                } 
                                ], 
                                "xaxis" : [ 1, 2 ] }, 
                        "3" : { 
                            "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 2.62, 2.25 ], "x" : [ 1, 2 ], "z" : [ [ 1, 2.62 ], [ 2, 2.25 ] ] } ], 
                            "xaxis" : [ 1, 2 ] }, 
                        "4" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 1.87, 1.91 ], "x" : [ 1, 2 ], "z" : [ [ 1, 1.87 ], [ 2, 1.91 ] ] } ], "xaxis" : [ 1, 2 ] }, 
                        "5" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 1.89, 3.13 ], "x" : [ 1, 2 ], "z" : [ [ 1, 1.89 ], [ 2, 3.13 ] ] } ], "xaxis" : [ 1, 2 ] }, 
                        "6" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 2.16, 2.07 ], "x" : [ 1, 2 ], "z" : [ [ 1, 2.16 ], [ 2, 2.07 ] ] } ], "xaxis" : [ 1, 2 ] }, 
                        "7" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 2.01, 1.59 ], "x" : [ 1, 2 ], "z" : [ [ 1, 2.01 ], [ 2, 1.59 ] ] } ], "xaxis" : [ 1, 2 ] }, 
                        "8" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 1.87, 1.81 ], "x" : [ 1, 2 ], "z" : [ [ 1, 1.87 ], [ 2, 1.81 ] ] } ], "xaxis" : [ 1, 2 ] }, 
                        "9" : { "series" : [ { "name" : [ 1, 2 ], "label" : "Distance entre les deux nombres", "color" : "blue", "y" : [ 1.96, 1.57 ], "x" : [ 1, 2 ], "z" : [ [ 1, 1.96 ], [ 2, 1.57 ] ] } ], "xaxis" : [ 1, 2 ] } 
                    }, 
                    "xaxis_label" : "Distance entre deux nombres", 
                    "yaxis_label" : "Temps médian de réaction(en sec.)", 
                    "title" : "Reconnaissance des nombres" 
                } 
            }
        record_items  = self.coll.find({"subject": "numbers"}).limit(5)
        for record_item in record_items:
            for k,v in record_model.items():
                self.assertIn(k, record_item)
                self.assertEqual(type(v), type(record_item[k]))
    def test_letters_record(self):
        record_model = { 
            "student" : 3815, "classroom" : 38, "subject" : "letters", 
            "matrix" : [ 
                [ 3, [ 
                        [ "pseudoword", [ [ 2, 3.18 ], [ 3, 0.96 ], [ 4, 6.54 ], [ 5, 2.14 ] ] ], 
                        [ "word", [ [ 2, 1.27 ], [ 3, 1.46 ], [ 4, 0.66 ], [ 5, 1.66 ] ] ] ] 
                ], 
                [ 2, [ 
                    [ "pseudoword", [ [ 2, 1.49 ], [ 3, 1.64 ], [ 4, 0.96 ] ] ], 
                    [ "word", [ [ 2, 2.18 ], [ 3, 1.1 ], [ 4, 0.97 ] ] ] ] 
                ], 
                [ 5, [ 
                    [ "word", [ [ 2, 1.46 ], [ 3, 0.1 ], [ 4, 0.45 ], [ 5, 0.12 ] ] ], 
                    [ "pseudoword", [ [ 2, 0.15 ], [ 3, 0.49 ], [ 4, 0.18 ], [ 5, 0.53 ] ] ] ] 
                ], 
                [ "average", [ 
                    [ "word", [ [ 2, 1.56 ], [ 3, 0.92 ], [ 4, 1.02 ], [ 5, 1.16 ] ] ], 
                    [ "pseudoword", [ [ 2, 1.61 ], [ 3, 1.14 ], [ 4, 2.25 ], [ 5, 1.27 ] ] ] ] ], 
                [ 4, [ 
                    [ "word", [ [ 2, 1.32 ], [ 3, 1.01 ], [ 4, 1.98 ], [ 5, 1.69 ] ] ], 
                    [ "pseudoword", [ [ 2, None ], [ 3, 1.48 ], [ 4, 1.34 ], [ 5, 1.13 ] ] ] ] ] 
                ], 
            "graph" : 
                { 
                    "subject" : "letters", 
                    "data" : 
                    { 
                        "2" : { 
                            "series" : [ 
                                { "name" : "pseudoword", "label" : "Pseudo Mot", "color" : "red", "y" : [ 1.49, 1.64, 0.96 ], "x" : [ 2, 3, 4 ], "z" : [ [ 2, 1.49 ], [ 3, 1.64 ], [ 4, 0.96 ] ] }, 
                                { "name" : "word", "label" : "Mot", "color" : "green", "y" : [ 2.18, 1.1, 0.97 ], "x" : [ 2, 3, 4 ], "z" : [ [ 2, 2.18 ], [ 3, 1.1 ], [ 4, 0.97 ] ] } 
                            ], 
                            "xaxis" : [ 2, 3, 4 ] 
                            }, 
                        "3" : { 
                            "series" : [ 
                                { "name" : "pseudoword", "label" : "Pseudo Mot", "color" : "red", "y" : [ 3.18, 0.96, 6.54, 2.14 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 3.18 ], [ 3, 0.96 ], [ 4, 6.54 ], [ 5, 2.14 ] ] }, 
                                { "name" : "word", "label" : "Mot", "color" : "green", "y" : [ 1.27, 1.46, 0.66, 1.66 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 1.27 ], [ 3, 1.46 ], [ 4, 0.66 ], [ 5, 1.66 ] ] } 
                            ], 
                            "xaxis" : [ 2, 3, 4, 5 ] }, 
                        "4" : { 
                            "series" : [ 
                                { "name" : "word", "label" : "Mot", "color" : "green", "y" : [ 1.32, 1.01, 1.98, 1.69 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 1.32 ], [ 3, 1.01 ], [ 4, 1.98 ], [ 5, 1.69 ] ] }, 
                                { "name" : "pseudoword", "label" : "Pseudo Mot", "color" : "red", "y" : [ None, 1.48, 1.34, 1.13 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, None ], [ 3, 1.48 ], [ 4, 1.34 ], [ 5, 1.13 ] ] } ], 
                            "xaxis" : [ 2, 3, 4, 5 ] }, 
                        "5" : { 
                            "series" : [ 
                                    { "name" : "word", "label" : "Mot", "color" : "green", "y" : [ 1.46, 0.1, 0.45, 0.12 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 1.46 ], [ 3, 0.1 ], [ 4, 0.45 ], [ 5, 0.12 ] ] }, 
                                    { "name" : "pseudoword", "label" : "Pseudo Mot", "color" : "red", "y" : [ 0.15, 0.49, 0.18, 0.53 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 0.15 ], [ 3, 0.49 ], [ 4, 0.18 ], [ 5, 0.53 ] ] }
                            ], 
                            "xaxis" : [ 2, 3, 4, 5 ] }, 
                        "average" : { 
                            "series" : [ 
                                { "name" : "word", "label" : "Mot", "color" : "green", "y" : [ 1.56, 0.92, 1.02, 1.16 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 1.56 ], [ 3, 0.92 ], [ 4, 1.02 ], [ 5, 1.16 ] ] }, 
                                { "name" : "pseudoword", "label" : "Pseudo Mot", "color" : "red", "y" : [ 1.61, 1.14, 2.25, 1.27 ], "x" : [ 2, 3, 4, 5 ], "z" : [ [ 2, 1.61 ], [ 3, 1.14 ], [ 4, 2.25 ], [ 5, 1.27 ] ] } ], 
                            "xaxis" : [ 2, 3, 4, 5 ] } 
                    }, 
                    "xaxis_label" : "Nombre de lettres", "yaxis_label" : "Temps médian de réaction(en sec.)", "title" : "Reconnaissance des mots" } 
                }
        record_items  = self.coll.find({"subject": "letters"}).limit(5)
        for record_item in record_items:
            for k,v in record_model.items():
                self.assertIn(k, record_item)
                self.assertEqual(type(v), type(record_item[k]))
    def test_status_api_students_ko(self):
        datasets = ["letters", "numbers"]
        students = [608787, 110, 5911, 455, "A"]
        responses = [406, 406, 404, 404, 404]
        full_params = [(s,d) for s in students for d in datasets]
        full_responses = [c for c in responses for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            msg = "Wrong response code for {}: actual {} and expected {}.".format(uri, response_code, r)
            self.assertEqual(r, response_code, msg)
        
    def test_status_api_students_ok(self):
        full_params = [] 
        full_responses = []
        for d in ["numbers", "letters"]:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_response_api(self):
        record_model = { 
            "type": "decision",
            "student": 112,
            "subject": "letters",
            "subject_name": "Français",
            "title": "Reconnaissance des mots",
            "xaxis_label": "Temps médian de réaction(en sec.)",
            "yaxis_label": "Nombre de lettres",
            "data": [],
            "decision": { }
        }
        full_params = [] 
        full_responses = []
        for d in ["numbers", "letters"]:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            for k, v in record_model.items():
                self.assertIn(k, response_data)
                self.assertIsInstance(v, type(v)) 
            if p[1] == "letters":
                self.assertEqual(response_data["subject"], "letters")
                self.assertEqual(response_data["subject_name"], "Français")
                self.assertEqual(response_data["title"], "Reconnaissance des mots")
            else:
                self.assertEqual(response_data["subject"], "numbers")
                self.assertEqual(response_data["subject_name"], "Maths")
                self.assertEqual(response_data["title"], "Reconnaissance des nombres")
            self.assertEqual(list(sorted([str(n[0]) for n in response_data["data"]])), list(response_data["decision"].keys()))

if __name__ == '__main__':
    unittest.main()