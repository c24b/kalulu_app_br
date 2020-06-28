import unittest
import random
import pymongo
import requests
from sshtunnel import SSHTunnelForwarder

from settings.api import API_URL
from settings.database import DB_NAME, DB_HOST, DB_PORT


class TestStudentCounting(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_counting"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/numbers/counting/".format(API_URL)
    
    def test_table_exists(self):
        '''Test if table exists'''
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        ''' Test nb of records in table'''
        self.assertEqual(self.coll.count_documents({}), 802)
    def test_count_students(self):
        ''' Test nb of unique students in tables '''
        self.assertEqual(len(self.coll.distinct("student")), 802)
    def test_record(self):
        record_model = {
            "games" : [
                "caterpillar"
            ],
            "classroom": 7,
            "student" : 713,
            "%CA" : 91.98,
            "score" : 2006,
            "timespent" : 1326.2588,
            "nb_records" : 2181,
            "dataset" : "numbers",
            "subject" : "numbers",
            "color" : "green"
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
            "type": "counting",
            "student": 112,
            "subject": "numbers",
            "subject_name": "Maths",
            "classroom": 1,
            "data": [{
                "games": [
                    "caterpillar"
                ],
                "score": 7997,
                "nb_records": 9107,
                "student": 112,
                "subject": "numbers",
                "dataset": "numbers",
                "timespent": 5686.550823,
                "%CA": 87.81,
                "color": "green"
            }],
            "counting": [{
                "games": [
                    "caterpillar"
                ],
                "%CA": 87.81,
                "timespent": "01:34:46",
                "color": "green"
            }]
        }
        students = [112, 2356, 69450, 245, 4512, 256]
        responses = [200, 404, 406, 404, 200, 404]
        for s,rcode in zip(students, responses):
            uri = "{}students/{}".format(self.endpoint,s)
            r = requests.get(uri)
            self.assertEqual(r.status_code, rcode, uri)
            response = r.json()
            if rcode == 500:
                raise Exception("Database table is empty!")
            elif rcode != 200:
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
                for r_m in response_model["data"]:
                    for k,v in r_m.items():
                        for r_i in response["data"]:
                            self.assertIn(k, list(r_i.keys()))
                            self.assertEqual(type(v), type(r_i[k]), k)
                for r_m in response_model["counting"]:
                    for k,v in r_m.items():
                        for r_i in response["counting"]:
                            self.assertIn(k, list(r_i.keys()))
                            self.assertEqual(type(v), type(r_i[k]), k)
    def test_csv(self):
        for student in random.choices(self.coll.distinct("student"), k=5):
            r = requests.get("{}students/{}/csv".format(self.endpoint,student))      
            print(r.url)
            response = r.text.split("<br/>")
            header = response[0].split(",")
            self.assertEqual(len(header), len(response[1].split(",")))
        
class TestStudentIdentification(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_identification"
        if ENV != "local":
            server = SSHTunnelForwarder(
                MONGO_HOST,
                ssh_username=MONGO_USER,
                remote_bind_address=('127.0.0.1', 27017)
            )
            server.start()
            client = pymongo.MongoClient('127.0.0.1', 27017) 
            #server.local_bind_port) # server.local_bind_port is assigned local port
            self.db = client[DB_NAME]
            self.coll = self.db[self.table_name]
            # print(db)
            # print(self.collections)
            server.stop()
        else:
            client = pymongo.MongoClient('127.0.0.1', 27017)
            self.db = client[DB_NAME]
            self.coll = self.db[self.table_name]
        self.endpoint = "{}/numbers/identification/".format(API_URL)
    def test_table_exists(self):
        '''Test if table exists'''
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        ''' Test nb of records in table'''
        self.assertEqual(self.coll.count_documents({}), 877)
    def test_count_students(self):
        ''' Test nb of unique students in tables '''
        self.assertEqual(len(self.coll.distinct("student")), 877)
    def test_record(self):
        record_model = {
            "games" : [
                "caterpillar"
            ],
            "classroom": 7,
            "student" : 713,
            "%CA" : 91.98,
            "score" : 2006,
            "timespent" : 1326.2588,
            "nb_records" : 2181,
            "dataset" : "numbers",
            "subject" : "numbers",
            "color" : "green"
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
                "type": "identification",
                "student": 112,
                "subject": "numbers",
                "subject_name": "Maths",
                "classroom": 1,
                "data": [
                    {
                    "games": [
                        "jellyfish",
                        "crabs",
                        "ants"
                    ],
                    "score": 4567,
                    "nb_records": 5041,
                    "student": 112,
                    "subject": "numbers",
                    "dataset": "numbers",
                    "timespent": 1877.383449,
                    "%CA": 90.6,
                    "color": "green"
                    }
                ],
                "identification": [
                    {
                    "games": [
                        "jellyfish",
                        "crabs",
                        "ants"
                    ],
                    "%CA": 90.6,
                    "timespent": "00:31:17",
                    "color": 90.6
                    }
                ]
                }
        students = [112, 2356, 69450, 245, 4512, 256]
        responses = [200, 404, 406, 404, 200, 404]
        for s,rcode in zip(students, responses):
            uri = "{}students/{}".format(self.endpoint,s)
            r = requests.get(uri)
            self.assertEqual(r.status_code, rcode, uri+ "curr:"+str(r.status_code)+" expected: "+str(rcode))
            response = r.json()
            if rcode == 500:
                raise Exception("Database table is empty!")
            elif rcode != 200:
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
                for r_m in response_model["data"]:
                    for k,v in r_m.items():
                        for r_i in response["data"]:
                            self.assertIn(k, list(r_i.keys()))
                            self.assertEqual(type(v), type(r_i[k]), k)
    def test_csv(self):
        for student in random.choices(self.coll.distinct("student"), k=5):
            r = requests.get("{}students/{}/csv".format(self.endpoint,student))    
            print(">>>", r.url)
            response = r.text.split("<br/>")
            header = response[0].split(",")
            self.assertEqual(len(header), len(response[1].split(",")))

if __name__ == '__main__':
    unittest.main()