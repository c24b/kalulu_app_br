import unittest
import random
import pymongo
import requests
# from sshtunnel import SSHTunnelForwarder
from settings import DB_NAME, API_URL

class TestStudents(unittest.TestCase):
    def setUp(self):
        self.table_name = "students"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/letters/words".format(API_URL)
    def test_table_exists(self):
        '''Test if table exists'''
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        ''' Test nb of records in table'''
        self.assertEqual(self.coll.count_documents({}), 157)
    # def test_count_students(self):
    #     ''' Test nb of unique students in tables '''
    #     self.assertEqual(len(self.coll.distinct("student")), 705)
    def test_record(self):
        record_model = {}
        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0})
            self.assertIn(k, list(record_item.keys()))
            self.assertEqual(type(v), type(record_item[k])) 
        
    def test_endpoint_status(self):
        response_model = {
        }
        r = requests.get("{}".format(self.endpoint))
        self.assertEqual(r.status_code, 200)
        response = r.json()
        for k,v in response_model.items():
            self.assertIn(k, list(response.keys()))
            self.assertEqual(type(v), type(response[k]))
        
        for k,v in response_model["words"][0].items():    
            self.assertIn(k, list(response["words"][0].keys()))
            self.assertEqual(type(v), type(response["words"][0][k]))
        for k,v in response_model["data"][1].items():
            
            self.assertIn(k, list(response["data"][1].keys()))
            self.assertEqual(type(v), type(response["data"][1][k]))
    
    def test_csv(self):
        r = requests.get("{}/csv".format(self.endpoint))
        self.assertEqual(r.status_code, 200)
        response = r.text
        table = response.split("<br/>")
        header = table[0].split(",")
        self.assertEqual(len(header), len(table[1].split(",")))
        self.assertEqual(len(table)-2, self.coll.count_documents({}))

class TestStudentWords(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_words"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/letters/words/".format(API_URL)
    def test_table_exists(self):
        '''Test if table exists'''
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        ''' Test nb of records in table'''
        self.assertEqual(self.coll.count_documents({}), 49308)
    def test_count_students(self):
        ''' Test nb of unique students in tables '''
        self.assertEqual(len(self.coll.distinct("student")), 743)
    def test_record(self):
        record_model = {
                "word" : "allé",
                "CA" : 2,
                "nb_records" : 3,
                "classroom" : 1,
                "nb_letters" : 4,
                "color" : "orange",
                "median_time_reaction" : 0.871655,
                "type" : "word",
                "%CA" : 66.67,
                "student" : 111
            }

        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0, "records":0})
            self.assertIn(k, list(record_item.keys()))
            self.assertEqual(type(v), type(record_item[k]), k) 
        # for r_m in record_model["records"]:
        #     for k,v in r_m.items():
        #         for r_i in record_item["records"]:
        #             self.assertIn(k, list(r_i.keys()))
        #             self.assertEqual(type(v), type(r_i[k]), k) 
    def test_endpoint_status(self):
        response_model = {
            "student": 112,
            "type": "words",
            "subject": "letters",
            "subject_name": "Français", 
            "words": [
                    {
                    "word": "allé",
                    "%CA": 62.5,
                    "color": "orange"
                    },
                    {
                    "word": "ami",
                    "%CA": 33.33,
                    "color": "red"
                    }
            ],
            "data": [
                {
                    "%CA": 83.33,
                    "nb_letters": 4,
                    "type": "word",
                    "median_time_reaction": 1.0619675000000002,
                    "classroom": 1,
                    "word": "allé",
                    "CA": 5,
                    "nb_records": 6,
                    "student": 112,
                    "color": "green"
                },
                {
                    "%CA": 0.0,
                    "nb_letters": 3,
                    "type": "word",
                    "median_time_reaction": 1.6829735000000001,
                    "classroom": 1,
                    "word": "ami",
                    "CA": 0,
                    "nb_records": 6,
                    "student": 112,
                    "color": "red"
                }
            ]
        }
        students = random.choices(self.coll.distinct("student"), k=5)
        responses = [200 ] * 5
        students.extend([2356, 7777777, 245])
        responses.extend([404, 406, 404])
        for s,rcode in zip(students, responses):
            uri = "{}students/{}".format(self.endpoint,s)
            r = requests.get(uri)
            self.assertEqual(r.status_code, rcode, uri)
            response = r.json()
            if rcode != 200:
                self.assertIn("message", response)
                # curr_msg = response["message"].split(". ")[0]
                # if rcode == 406:
                #     model_msg = "L'identifiant de l'élève {} est incorrect".format(s)
                #     self.assertEqual(model_msg,curr_msg, rcode)
                #     continue
                # elif rcode == 404:
                #     model_msg = "L'élève {} n'a pas encore vu de mots".format(s)
                #     self.assertEqual(model_msg,curr_msg, rcode)
                #     continue
            else:
                for k,v in response_model.items():
                    self.assertIn(k, list(response.keys()))
                    self.assertEqual(type(v), type(response[k]))
                for r_m in response_model["words"]:
                    for k,v in r_m.items():
                        for r_i in response["words"]:
                            self.assertIn(k, list(r_i.keys()))
                            self.assertEqual(type(v), type(r_i[k]), k)
                for r_m in response_model["data"]:
                    for k,v in r_m.items():
                        if k != "median_time_reaction":
                            pass
                        else:
                            for r_i in response["data"]:
                                self.assertIn(k, list(r_i.keys()))

                                self.assertEqual(type(v), type(r_i[k]), k)

    def test_csv(self):
        for s in random.choices(self.coll.distinct("student"), k=5):
            uri = "{}students/{}/csv".format(self.endpoint,s)
            r = requests.get(uri)
            response = r.text
            table = response.split("<br/>")
            header = table[0].split(",")
            self.assertEqual(len(header), len(table[1].split(",")))
            self.assertEqual(len(table)-2, self.coll.count_documents({"student":s}))    
if __name__ == '__main__':
    unittest.main()