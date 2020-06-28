import unittest
import pymongo
import requests
import random
from sshtunnel import SSHTunnelForwarder

from settings import DB_NAME, API_URL


class TestDBStudentLesson(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_lesson"        
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/progression/chapters/classrooms/".format(API_URL)
        self.students = list(self.db["students"].distinct("student", {"group": {"$ne": "guest"}}))
        self.subjects = ["letters", "numbers"]
        self.datasets = ["gp", "numbers"]
        self.lessons = {
            "letters":list(self.db["path"].find({"dataset":"gp"}, {"_id":0})), 
            "numbers":list(self.db["path"].find({"dataset":"numbers"}, {"_id": 0}))
        }

    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 25488)
        self.assertEqual(len(self.coll.distinct("student")), 804)
        self.assertEqual(len(self.coll.distinct("dataset")), 2)
        self.assertEqual(len(self.coll.distinct("subject")), 2)
        self.assertEqual(len(self.coll.distinct("lesson")), 45)
        self.assertEqual(len(self.coll.distinct("lesson", {"subject":"numbers"})),38)
        self.assertEqual(len(self.coll.distinct("lesson", {"subject":"letters"})),45)
        self.assertEqual(len(self.coll.distinct("chapter")), 20)
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"numbers"})),18)
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"letters"})),14)
        self.assertEqual(self.coll.count_documents({"subject":"numbers"}), 11231)
        self.assertEqual(self.coll.count_documents({"subject":"letters"}), 14257)
    
    def test_item(self):
        record_model = {
            "classroom" : 1,
            "group" : "r/m",
            "student" : 111,
            "dataset" : "gp",
            "subject" : "letters",
            "lesson" : 1,
            "chapter" : 1,
            # "start" : ISODate("2018-10-15T09:09:29Z"),
            # "end" : ISODate("2018-10-16T09:45:19Z"),
            "timespent" : 1598,
            "nb_records" : 451,
            "CA" : 343,
            # "tag" : "a",
            "tags" : [
                "a"
            ],
            "lessons" : [
                1
            ],
            "WA" : 108,
            "CA_rate" : 0.76,
            "WA_rate" : 0.24,
            "%WA" : 23.95,
            "%CA" : 76.05,
            "nb_days" : 2,
            "nb_sequence" : 2,
            "%CA_avg" : 94.74,
            "%CA_color" : "red",
            "timespent_avg" : 594.46,
            "timespent_color" : "green"
        }
        for s in self.subjects:
            record_item = self.coll.find_one({"subject":s}, {"_id":0})
            self.assertIn("tag", record_item.keys(), "tag")
            if s == "numbers":
                self.assertIsInstance(record_item["tag"], int, "tag")
            else:
                self.assertIsInstance(record_item["tag"], str, "tag")
            for k,v in record_model.items():
                self.assertIn(k, list(record_item.keys()), k)
                self.assertEqual(type(v), type(record_item[k]), k)
            self.assertEqual(len(record_item["records"]),record_item["nb_records"])

    def test_api_response(self):
        for subject in ["letters", "numbers"]:
            for classroom in random.choices(self.coll.distinct("classroom", {"subject":subject}), k=3):
                uri = "{}{}/subjects/{}".format(self.endpoint, classroom, subject)
                r = requests.get(uri)      
                print(r.url)
                response = r.json()
                self.assertEqual(len(response["students"]), len(self.coll.distinct("student", {"classroom":classroom, "subject": subject})))
class TestDBStudentChapter(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_chapter"
        
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.students = list(self.db["students"].distinct("student", {"group": {"$ne": "guest"}}))
        self.subjects = ["letters", "numbers"]
        self.datasets = ["gp", "numbers"]
        self.lessons = {
            "letters":list(self.db["path"].find({"dataset":"gp"}, {"_id":0})), 
            "numbers":list(self.db["path"].find({"dataset":"numbers"}, {"_id": 0}))
        }

    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 9110)
        self.assertEqual(len(self.coll.distinct("student")), 804)
        self.assertEqual(len(self.coll.distinct("dataset")), 2)
        self.assertEqual(len(self.coll.distinct("subject")), 2)
        # self.assertEqual(len(self.coll.distinct("lessons")), 45)
        # self.assertEqual(len(self.coll.distinct("lesson", {"subject":"numbers"})),38)
        # self.assertEqual(len(self.coll.distinct("lesson", {"subject":"letters"})),45)
        self.assertEqual(len(self.coll.distinct("chapter")), 20)
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"numbers"})),18)
        self.assertEqual(len(self.coll.distinct("chapter", {"subject":"letters"})),14)
        self.assertEqual(self.coll.count_documents({"subject":"numbers"}), 4796)
        self.assertEqual(self.coll.count_documents({"subject":"letters"}), 4314)
    
    def test_item(self):
        record_model = {
            "classroom" : 1,
            "group" : "r/m",
            "student" : 111,
            "dataset" : "gp",
            "subject" : "letters",
            #"lesson" : 1,
            "chapter" : 1,
            # "start" : ISODate("2018-10-15T09:09:29Z"),
            # "end" : ISODate("2018-10-16T09:45:19Z"),
            "timespent" : 1598,
            "nb_records" : 451,
            # "CA" : 343,
            # "tag" : "a",
            "tags" : [
                "a"
            ],
            # "lessons" : [
            #     1
            # ],
            # "WA" : 108,
            # "CA_rate" : 0.76,
            # "WA_rate" : 0.24,
            # "%WA" : 23.95,
            # "%CA" : 76.05,
            # "nb_days" : 2,
            # "nb_sequence" : 2,
            # "%CA_avg" : 94.74,
            # "%CA_color" : "red",
            # "timespent_avg" : 594.46,
            # "timespent_color" : "green"
        }
        for s in self.subjects:
            record_item = self.coll.find_one({"subject":s}, {"_id":0})
            self.assertIn("tags", record_item.keys(), "tags")
            # if s == "numbers":
            #     self.assertIsInstance(record_item["tag"], int, "tag")
            # else:
            #     self.assertIsInstance(record_item["tag"], str, "tag")
            for k,v in record_model.items():
                self.assertIn(k, list(record_item.keys()), k)
                self.assertEqual(type(v), type(record_item[k]), k)
            self.assertEqual(len(record_item["records"]),record_item["nb_records"])    

# class TestDBStudentChapter(unittest.TestCase):
#     def setUp(self):
#         self.table_name = "student_chapter"
#         if ENV != "local":
#             server = SSHTunnelForwarder(
#                 MONGO_HOST,
#                 ssh_username=MONGO_USER,
#                 remote_bind_address=('127.0.0.1', 27017)
#             )
#             server.start()
#             client = pymongo.MongoClient('127.0.0.1', 27017) 
#             #server.local_bind_port) # server.local_bind_port is assigned local port
#             self.db = client[DB_NAME]
#             self.coll = self.db[self.table_name]
#             # print(db)
#             # print(self.collections)
#             server.stop()
#         else:
#             client = pymongo.MongoClient('127.0.0.1', 27017)
#             self.db = client[DB_NAME]
#             self.coll = self.db[self.table_name]
#         self.endpoint = "{}/progression/".format(API_URL)
#         self.students_ok = random.choices(self.coll.distinct("student"), k=5)
#         self.students_ko = [11, 68241, "A", 219, 439]
#         self.students_responses_ko = [406, 406, 406, 404, 404] 
#         self.datasets = ["gp", "numbers"]
#         self.subjects = ["letters", "numbers"]

#     def test_table_exists(self):
#         self.assertIn(self.table_name, self.db.list_collection_names())
    
#     def test_count_records(self):
#         self.assertEqual(self.coll.count_documents({}), 9110)
#         self.assertEqual(len(self.coll.distinct("student")), 804)
#         self.assertEqual(len(self.coll.distinct("dataset")), 2)
#         self.assertEqual(len(self.coll.distinct("chapter")), 20)
#         self.assertEqual(len(self.coll.distinct("chapter", {dataset:"gp"})),14)
#         self.assertEqual(len(self.coll.distinct("chapter", {dataset:"numbers"})),18) 
#         self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 4314)
#         self.assertEqual(self.coll.count_documents({"dataset":"numbers"}), 4796)

#     def test_db_record(self):
#         db.student_chapter.findOne({}, {chapters:0, "_id":0})
#         record_model = {
#             "student" : 111,
#             "classroom" : 1,
#             "group" : "r/m",
#             "dataset" : "gp",
#             "chapter" : 1,
#             "tags" : [
#                 "a",
#                 "i",
#                 "e",
#                 "o"
#             ],
#             "lessons" : [
#                 1,
#                 2,
#                 3,
#                 4
#             ],
#             "CA" : 588,
#             "nb_records" : 753,
#             "timespent" : 3228,
#             "total_records" : 753
#         }

#         for n in self.datasets:
#             record_item = self.coll.find_one({"dataset":n}, {"_id":0, "chapters":0})
#         for k,v in record_model.items():
#             self.assertIn(k, list(record_item.keys()))
#             self.assertEqual(type(v), type(record_item[k]))

# class TestStudentChapter(unittest.TestCase):
#     def setUp(self):
#         self.table_name = "student_chapter"
#         if ENV != "local":
#             server = SSHTunnelForwarder(
#                 MONGO_HOST,
#                 ssh_username=MONGO_USER,
#                 remote_bind_address=('127.0.0.1', 27017)
#             )
#             server.start()
#             client = pymongo.MongoClient('127.0.0.1', 27017) 
#             #server.local_bind_port) # server.local_bind_port is assigned local port
#             self.db = client[DB_NAME]
#             self.coll = self.db[self.table_name]
#             # print(db)
#             # print(self.collections)
#             server.stop()
#         else:
#             client = pymongo.MongoClient('127.0.0.1', 27017)
#             self.db = client[DB_NAME]
#             self.coll = self.db[self.table_name]
#         self.endpoint = "{}/progression/".format(API_URL)
#         self.students_ok = random.choices(self.coll.distinct("student"), k=5)
#         self.students_ko = [11, 68241, "A", 219, 439]
#         self.students_responses_ko = [406, 406, 406, 404, 404] 
#         self.datasets = ["gp", "numbers"]
#         self.subjects = ["letters", "numbers"]

#     def test_table_exists(self):
#         self.assertIn(self.table_name, self.db.list_collection_names())
    
#     def test_count_records(self):
#         self.assertEqual(self.coll.count_documents({}), 9110)
#         self.assertEqual(len(self.coll.distinct("student")), 804)
#         self.assertEqual(len(self.coll.distinct("dataset")), 2)
#         self.assertEqual(len(self.coll.distinct("chapter")), 20)
#         self.assertEqual(len(self.coll.distinct("chapter", {dataset:"gp"})),14)
#         self.assertEqual(len(self.coll.distinct("chapter", {dataset:"numbers"})),18) 
#         self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 4314)
#         self.assertEqual(self.coll.count_documents({"dataset":"numbers"}), 4796)

#     def test_db_record(self):
#         record_model = {
#             "student" : 111,
#             "classroom" : 1,
#             "group" : "r/m",
#             "dataset" : "gp",
#             "chapter" : 1,
#             "tags" : [
#                 "a",
#                 "i",
#                 "e",
#                 "o"
#             ],
#             "lessons" : [
#                 1,
#                 2,
#                 3,
#                 4
#             ],
#             "CA" : 588,
#             "nb_records" : 753,
#             "timespent" : 3228,
#             "total_records" : 753
#         }
#         for n in self.datasets:
#             record_item = self.coll.find_one({"dataset":n}, {"_id":0, "chapters":0})
#         for k,v in record_model.items():
#             self.assertIn(k, list(record_item.keys()))
#             self.assertEqual(type(v), type(record_item[k]))
        
#     def test_api_response_students_ok(self):
#         for student in self.students:
#             for subject in self.subjects:
#                 uri = "{}students/{}/subjects/{}".format(self.endpoint, student, subject)
#                 r = 200
#                 response = requests.get(uri)
#                 response_code = response.status_code
#                 response_data = response.json()
#                 msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
#                 self.assertEqual(r, response_code, msg)
#     def test_api_response_students_ko(self):
#         self.students_ko = [11, 68241, "A", 219, 439]
#         self.responses_ko = [r for r in self.students_responses_ko for n in self.subjects]
#         uris = []
#         for student in self.students_ko:
#             for subject in self.subjects:
#                 uris.append("{}students/{}/subjects/{}".format(self.endpoint, student, subject))
#         for uri, r in zip(self.responses_ko, uris):
#             response = requests.get(uri)
#             response_code = response.status_code
#             response_data = response.json()
#             msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
#             self.assertEqual(r, response_code, msg)
    
#     def test_api_response_subjects_ko(self):
#         for student in self.students:
#             uri = "{}students/{}/subjects/{}".format(self.endpoint, student, "geometry")
#             r = 406
#             response = requests.get(uri)
#             response_code = response.status_code
#             response_data = response.json()
#             msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
#             self.assertEqual(r, response_code, msg)
    
#     def test_api_response_format(self):
#         for student in self.students:
#             for subject in self.subjects:
#                 uri = "{}students/{}/subjects/{}".format(self.endpoint, student, subject)
#                 r = 200
#                 response = requests.get(uri)
#                 response_code = response.status_code
#                 response_data = response.json()
#                 msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
#                 self.assertEqual(r, response_code, msg)
                    
#     def test_api_response_chapters_datasets(self):
#         raise NotImplementedError
#     def test_api_format_chapters_datasets(self):
#         raise NotImplementedError
#     def test_api_response_chapters_subjects(self):
#         raise NotImplementedError
#     def test_api_format_chapters_subjects(self):
#         raise NotImplementedError
if __name__ == '__main__':
    unittest.main()