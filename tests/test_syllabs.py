import unittest
import random
import pymongo
import requests
from sshtunnel import SSHTunnelForwarder

from settings.database import DB_NAME, DB_HOST, DB_URI
from settings.api import API_URL 


class TestSyllabs(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_syllabs"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/letters/syllabs/students/".format(API_URL)
    def test_table_exists(self):
        '''Test if table exists'''
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        ''' Test nb of records in table'''
        self.assertEqual(self.coll.count(), 43316)
    def test_count_students(self):
        ''' Test nb of unique students in tables '''
        self.assertEqual(len(self.coll.distinct("student")), 705)
    def test_record(self):
        record_model = {
            "classroom" : 9,
            "student" : 924,
            "group" : "r/m",
            "dataset" : "gp",
            "syllab" : "m-m.ou-u",
            "stimuli" : [
                "l-l.a-a",
                "s-s.ou-u",
                "m-m.ou-u",
                ""
            ],
            "CA" : 40,
            "nb_records" : 54,
            "%CA" : 74.07,
            "color" : "green",
            "word" : "mou"
        }
        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0})
            self.assertIn(k, list(record_item.keys()))
            self.assertEqual(type(v), type(record_item[k])) 
    def test_endpoint_status(self):
        students = [112, 2356, 7777777, 245, 4512]
        responses = [200, 404, 406, 404, 200]
        response_model = {
            "type": "syllabs",
            "student": 112,
            "subject_name": "Français",
            "subject": "letters",
            "syllabs": [
                    {
                        "nb_records": 22,
                        "syllab": "l-l.i-i",
                        "color": "orange",
                        "%CA": 63.64,
                        "word": "li"
                    },
                    {
                        "nb_records": 270,
                        "syllab": "p-p.a-a.s-#",
                        "color": "orange",
                        "%CA": 72.22,
                        "word": "pas"
                    }
            ],
            "data": [
                {
                    "color": "green",
                    "stimuli": [
                        "",
                        "f-f.é-e.e-#"
                    ],
                    "group": "r/m",
                    "word": "fée",
                    "syllab": "f-f.é-e.e-#",
                    "nb_records": 90,
                    "student": 112,
                    "CA": 69,
                    "%CA": 76.67,
                    "dataset": "gp",
                    "classroom": 1
                },
                {
                    "color": "orange",
                    "stimuli": [
                        "n-n.o-o.s-#",
                        "",
                        "p-p.a-a.s-#"
                    ],
                    "group": "r/m",
                    "word": "pas",
                    "syllab": "p-p.a-a.s-#",
                    "nb_records": 270,
                    "student": 112,
                    "CA": 195,
                    "%CA": 72.22,
                    "dataset": "gp",
                    "classroom": 1
                }
            ]
        }
        for s,resp in zip(students, responses):
            r = requests.get("{}{}".format(self.endpoint,s))
            self.assertEqual(r.status_code, resp)
            if resp != 200:
                self.assertIn("message", r.json().keys())
            else:
                response = r.json()
                for k,v in response_model.items():
                    self.assertIn(k, list(response.keys()))
                    self.assertEqual(type(v), type(response[k]))
                for k,v in response_model["syllabs"][1].items():
                    self.assertIn(k, list(response["syllabs"][1].keys()))
                    self.assertEqual(type(v), type(response["syllabs"][1][k]))
                for k,v in response_model["data"][1].items():    
                    self.assertIn(k, list(response["data"][1].keys()))
                    self.assertEqual(type(v), type(response["data"][1][k]))
                
    def test_csv(self):
        uri = "{}csv".format(self.endpoint)
        for student in random.choices(self.coll.distinct("student"), k=5):
            r = requests.get("{}{}/csv".format(self.endpoint,student))
            print(r.url)
            response = r.text.split("<br/>")
            header = response[0].split(",")
            self.assertEqual(len(header), len(response[3].split(",")), len(response[1].split(",")))


if __name__ == '__main__':
    unittest.main()