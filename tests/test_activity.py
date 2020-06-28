import unittest
import pymongo
import requests
import random
# from sshtunnel import SSHTunnelForwarder
from settings import DB_NAME, DB_HOST, DB_URI
from settings import API_URL

class TestStudentDay(unittest.TestCase):
    '''Student Dataset Day table is not exposed throught API'''
    def setUp(self):
        self.table_name = "student_dataset_day"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        # self.endpoint = "{}/letters/words/".format(API_URL)
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 50599, self.table_name)
    def test_count_datasets(self):
        self.assertEqual(len(self.coll.distinct("dataset")), 5, self.table_name)

    def test_count_students(self):
        self.assertEqual(len(self.coll.distinct("student")), 811, self.table_name)
    def test_count_classrooms(self):
        self.assertEqual(len(self.coll.distinct("classroom")), 39, self.table_name)
    def test_db_record(self):
        record_model = {
            "classroom" : 1,
            "dataset" : "gapfill_lang",
            "day" : "2018-11-23",
            # "end" : ISODate("2018-11-23T10:52:26Z"),
            "group" : "r/m",
            "nb_records" : 39,
            "nb_sequences" : 1,
            "sequences" : [
                # [
                #     ISODate("2018-11-23T10:49:01Z"),
                #     ISODate("2018-11-23T10:52:26Z")
                # ]
            ],
            # "start" : ISODate("2018-11-23T10:49:01Z"),
            "student" : 111,
            "subject" : "letters",
            "timespent" : 205.1,
            "records": []
        }

        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0})
            self.assertIn(k, list(record_item.keys()), k)
            self.assertEqual(type(v), type(record_item[k]), "Wrong type for {}".format(k))

class TestStudentDatasetActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_dataset"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username= USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 3500, self.table_name)
    def test_count_datasets(self):
        self.assertEqual(len(self.coll.distinct("dataset")), 5, self.table_name)

    def test_count_students(self):
        self.assertEqual(len(self.coll.distinct("student")), 811, self.table_name)
    def test_count_classrooms(self):
        self.assertEqual(len(self.coll.distinct("classroom")), 39, self.table_name)
    def test_db_record(self):
        record_model = {		
            "student" : 111,
            "classroom" : 1,
            "group" : "r/m",
            "dataset" : "assessments_language",
            "subject" : "letters",
            "nb_records" : 536,
            # "start" : ISODate("2018-11-13T09:41:27Z"),
            # "end" : ISODate("2019-02-04T09:02:55Z"),
            "timespent" : 1291.12,
            "nb_days" : 8,
            "nb_sequences" : 20,
            "records": []
	    }
        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0})
            
            self.assertIn(k, list(record_item.keys()), k)
            self.assertEqual(type(v), type(record_item[k]), "Wrong type for {}".format(k))
    def test_api_response_datasets_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("student"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_datasets_ok(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_students_ko(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        students = [608787, 110, "A", 5911, 455]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in datasets]
        full_responses = [c for c in responses for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_students_ok(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            
    def test_api_format(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"dataset": d}), k=2)
            for student in students:
                full_params.append((student, d))
        response_model = {
            'student': 3823, 'dataset': 'gapfill_lang', 'classroom': 38, 'subject': 'letters', 'subject_name': 'Français', 'type': 'activity', 
            'activity': [
                {'nb_days': 10, 'nb_sequences': 10, 'nb_records': 321, 'start': '2018-12-13 09:20:37', 'end': '2019-01-29 11:07:32', 'timespent': '01:04:38'}], 
            'data': [
                {'student': 3823, 'classroom': 38, 'group': 'r/m', 'dataset': 'gapfill_lang', 'subject': 'letters', 'nb_records': 321, 'start': '2018-12-13 09:20:37', 'end': '2019-01-29 11:07:32', 'timespent': '01:04:38', 'nb_days': 10, 'nb_sequences': 10, 'timespent_sec': 3878.0}],
            "csv":"",
            "doc": ""
        }
        for p in full_params: 
            uri = "{}students/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            for k,v in response_model.items():
                self.assertIn(k,response_data )
                self.assertEqual(type(v), type(response_data[k]), k)
            for k,v in response_model["activity"][0].items():
                self.assertIn(k,response_data["activity"][0], "activity.0."+k)
                self.assertEqual(type(v), type(response_data["activity"][0][k]))
            for k,v in response_model["data"][0].items():
                self.assertIn(k,response_data["data"][0])
                self.assertEqual(type(v), type(response_data["data"][0][k]))
    def test_csv_url(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/datasets/{}/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            self.assertEqual(r, response_code)

    def test_csv_response(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                
        for p in full_params:
            uri = "{}students/{}/datasets/{}/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            csv_doc = response.text.split("<br/>")
            header = csv_doc[0].split(",")
            row = csv_doc[1].split(",")
            self.assertEqual(len(header), len(row))

class TestStudentSubjectActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_subject"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username=USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     # print(db)
        #     # print(self.collections)
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 1569)
    def test_count_subjects(self):
        self.assertEqual(len(self.coll.distinct("subject")), 2)
    def test_count_students(self):
        self.assertEqual(len(self.coll.distinct("student")), 811)
    def test_count_classrooms(self):
        self.assertEqual(len(self.coll.distinct("classroom")), 39)
    def test_db_record(self):
        record_model = {
            "student" : 111,
            "classroom" : 1,
            "group" : "r/m",
            "datasets" : [
                "assessments_language",
                "gapfill_lang",
                "gp"
            ],
            "subject" : "letters",
            "nb_records" : 6118,
            # "start" : ISODate("2018-11-13T09:41:27Z"),
            # "end" : ISODate("2019-02-08T11:05:48Z"),
            "timespent" : 46878.2,
            "nb_days" : 0,
            "nb_sequences" : 65, 
            "records":[]
        }
        for k,v in record_model.items():
            record_item = self.coll.find_one({}, {"_id":0})
            self.assertIn(k, list(record_item.keys()))
            self.assertEqual(type(v), type(record_item[k]))
    
    def test_api_response_subjects_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("student"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_subjects_ok(self):
        subjects = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_students_ko(self):
        subjects = ["letters", "numbers"]
        students = [608787, 110, "A", 5911, 455]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in subjects]
        full_responses = [c for c in responses for x in subjects]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)

    def test_api_response_students_ok(self):
        subjects = ["letters", "numbers"] 
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            
    def test_api_format(self):
        subjects = ["letters", "numbers"]
        full_params = [] 
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=2)
            for student in students:
                full_params.append((student, subject))
        response_model = {
            "student": 311,
            "classroom": 3,
            "subject": "letters",
            "subject_name": "Français",
            "type": "activity",
            "activity": [
                {
                "nb_days": 0,
                "nb_sequences": 38,
                "nb_records": 4722,
                "start": "2018-12-11 13:59:02",
                "end": "2019-03-07 14:44:06",
                "timespent": "06:31:32"
                }
            ],
            "data": [
                {
                "student": 311,
                "classroom": 3,
                "group": "r/m",
                "datasets": [
                    "assessments_language",
                    "gapfill_lang",
                    "gp"
                ],
                "subject": "letters",
                "nb_records": 4722,
                "start": "2018-12-11 13:59:02",
                "end": "2019-03-07 14:44:06",
                "timespent": "06:31:32",
                "nb_days": 0,
                "nb_sequences": 38,
                "timespent_sec": 23492.1
                }
            ],
            "doc": "",
            "csv":""
        }
        for p in full_params: 
            uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            if response_code == 200:
                response_data = response.json()
                for k,v in response_model.items():
                    self.assertIn(k,response_data)
                    self.assertEqual(type(v),type(response_data[k]))
                for k,v in response_model["activity"][0].items():
                    self.assertIn(k,response_data["activity"][0])
                    self.assertEqual(type(v), type(response_data["activity"][0][k]))
                for k,v in response_model["data"][0].items():
                    self.assertIn(k,response_data["data"][0])
                    self.assertEqual(type(v), type(response_data["data"][0][k]), k)
    def test_csv_url(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            self.assertEqual(r, response_code, uri)

    def test_csv_response(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                
        for p in full_params:
            uri = "{}students/{}/subjects/{}/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            csv_doc = response.text.split("<br/>")
            header = csv_doc[0].split(",")
            row = csv_doc[1].split(",")
            self.assertEqual(len(header), len(row))

class TestStudentInfoActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_subject"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username=USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     # print(db)
        #     # print(self.collections)
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    def test_api_response_subjects_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("student"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/info".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_subjects_ok(self):
        subjects = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/info".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {} : actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_students_ko(self):
        subjects = ["letters", "numbers"]
        students = [608787, 110, "A", 5911, 455]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in subjects]
        full_responses = [c for c in responses for d in subjects]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/info".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)

    def test_api_response_students_ok(self):
        subjects = ["letters", "numbers"] 
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/info".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            
    def test_api_format(self):
        subjects = ["letters", "numbers"]
        full_params = [] 
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=2)
            for student in students:
                full_params.append((student, subject))
        response_model = {
            "type": "activity",
            "subject": "numbers",
            "student": 112, 
            "subject_name": "Maths",
            "timespent": "01:05:02",
            "chapter": 9,
            "lesson": 21,
            "nb_days": 1,
            "nb_sequences": 32,
            "timespent_sec": 45217.6,
        }
        for p in full_params:
            uri = "{}students/{}/subjects/{}/info".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            if response_code == 200:
                response_data = response.json()
                for k,v in response_model.items():
                    self.assertIn(k,response_data, k)
                    self.assertEqual(type(v),type(response_data[k]), k)
    def test_csv(self):
        subjects = ["letters", "numbers"]
        full_params = [] 
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=2)
            for student in students:
                full_params.append((student, subject))
        response_model = {
            "type": "activity",
            "subject": "numbers",
            "student": 112, 
            "subject_name": "Maths",
            "timespent": "01:05:02",
            "chapter": 9,
            "lesson": 21,
            "nb_days": 1,
            "nb_sequences": 32,
            "timespent_sec": 45217.6,
        }
        for p in full_params:
            uri = "{}students/{}/subjects/{}/info/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            if response_code == 200:
                response_data = response.text
                table = response_data.split("<br/>")
                header = table[0].split(",")
                row = table[-1].split(",")
                self.assertEqual(len(header), len(row), uri)
                for k in response_model.keys():
                    self.assertIn(k, header, "{} not in Header")
                
                # for k,v in response_model.items():
                #     self.assertIn(k,response_data, k)
                #     self.assertEqual(type(v),type(response_data[k]), k)

class TestStudentLastActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_chapter"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username=USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     # print(db)
        #     # print(self.collections)
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    # def test_table_exists(self):
    #     self.assertIn(self.table_name, self.db.list_collection_names())
    # def test_count_records(self):
    #     self.assertEqual(self.coll.count_documents({}), 1514)
    # def test_count_datasets(self):
    #     self.assertEqual(len(self.coll.distinct("dataset")), 2)
    # def test_count_subjects(self):
    #     self.assertEqual(len(self.coll.distinct("subject")), 2)
    # def test_count_students(self):
    #     self.assertEqual(len(self.coll.distinct("student")), 804)
    # def test_record(self):
    #     record_model = 	{
    #         "chapter" : 4,
    #             "student" : 4511,
    #             "dataset" : "gp",
    #             "subject" : "letters",
    #             "x" : [
    #                 "a",
    #                 "i",
    #                 "e",
    #                 "o",
    #                 "u",
    #                 "l",
    #                 "m",
    #                 "s",
    #                 "é",
    #                 "v",
    #                 "r",
    #                 "ou",
    #                 "n"
    #             ],
    #             "y" : [
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511
    #             ],
    #             "z" : [
    #                 [
    #                     "i",
    #                     "e"
    #                 ],
    #                 [
    #                     "e",
    #                     "u"
    #                 ],
    #                 [
    #                     "ou",
    #                     "é"
    #                 ],
    #                 [
    #                     "é",
    #                     "a"
    #                 ],
    #                 [
    #                     "ou",
    #                     "i"
    #                 ],
    #                 [
    #                     "s",
    #                     "v"
    #                 ],
    #                 [
    #                     "l",
    #                     "v"
    #                 ],
    #                 [
    #                     "l",
    #                     "v"
    #                 ],
    #                 [
    #                     "e",
    #                     "i"
    #                 ],
    #                 [
    #                     "s",
    #                     "l"
    #                 ],
    #                 [
    #                     "s",
    #                     "l"
    #                 ],
    #                 [
    #                     "a",
    #                     "i"
    #                 ],
    #                 [
    #                     "s",
    #                     "v"
    #                 ]
    #             ],
    #             "markers" : [
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star",
    #                 "star"
    #             ],
    #             "colors" : [
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow",
    #                 "yellow"
    #             ],
    #             "z_scores" : [
    #                 0.07,
    #                 0.1,
    #                 0.21,
    #                 0.1,
    #                 0.25,
    #                 0.21,
    #                 0.04,
    #                 0.17,
    #                 0.07,
    #                 0.02,
    #                 0.37,
    #                 0.16,
    #                 0.14
    #             ],
    #             "xaxis" : [
    #                 "a",
    #                 "i",
    #                 "e",
    #                 "o",
    #                 "u",
    #                 "l",
    #                 "m",
    #                 "s",
    #                 "é",
    #                 "v",
    #                 "r",
    #                 "ou",
    #                 "n"
    #             ],
    #             "yaxis" : [
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511,
    #                 4511
    #             ]
    #         }
    #     for record in self.coll.find({}, {"_id":0, "lessons":0}).limit(10):
    #         for k,v in record_model.items():
    #             self.assertIn(k, record.keys())
    #             self.assertEqual(type(v), type(record[k]), k)
    #         self.assertEqual(len(record["x"]), len(record["y"])) 
    #         self.assertEqual(len(record["x"]), len(record["z"]))
    #         self.assertEqual(len(record["markers"]), len(record["colors"]))
    
    def test_api_response_subjects_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("student"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/last".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_subjects_ok(self):
        subjects = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/last".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_students_ko(self):
        subjects = ["letters", "numbers"]
        students = [608787, 110, "A", 5911, 455]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in subjects]
        full_responses = [c for c in responses for d in subjects]
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/last".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)

    def test_api_response_students_ok(self):
        subjects = ["letters", "numbers"] 
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/last".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            
    def test_api_format(self):
        subjects = ["letters", "numbers"]
        full_params = [] 
        for subject in subjects:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=2)
            for student in students:
                full_params.append((student, subject))
        response_model = {
            "type": "activity",
            "subject": "letters",
            "student": 112,
            "subject_name": "Français",
            "chapter": 9,
            "data": [
                {
                "chapter": 9,
                "student": 112,
                "dataset": "gp",
                "subject": "letters",
                "x": [
                    "a",
                    "i",
                    "e",
                    "o",
                    "u",
                    "l",
                ],
                "y": [
                    112,
                    112,
                    112,
                    112,
                    112,
                    112,
                ],
                "z": [
                    [
                        "un",
                        "o"
                    ],
                    [
                        "ou",
                        "o"
                    ],
                    [
                        "é",
                        "o"
                    ],
                    [
                        "un",
                        "ou"
                    ],
                    [
                        "o",
                        "un"
                    ],
                    [
                        "d",
                        "j"
                    ],
                    ...
                ],
                "markers": [
                    "star",
                    "star",
                    "star",
                    "star",
                    "star",
                    "star",
                ],
                "colors": [
                    "yellow",
                    "yellow",
                    "yellow",
                    "yellow",
                    "yellow",
                    "yellow",
                ],
                "xaxis": [
                    "a",
                    "i",
                    "e",
                    "o",
                    "u",
                    "l",
                    
                ],
                "yaxis": [
                    112,
                    112,
                    112,
                    112,
                    112,
                    112,
                    112,
                    
                ],
                "title": "Activité de l'élève 112 en Français- Chapitre  9",
                "xaxis_label": "Leçon",
                "yaxis_label": "Elève",
                "zaxis": [
                    [
                        "un",
                        "o"
                    ],
                    [
                        "ou",
                        "o"
                    ],
                    [
                        "é",
                        "o"
                    ],
                    [
                        "un",
                        "ou"
                    ],
                    [
                        "o",
                        "un"
                    ],
                ],
                "zaxis_label": "confondu avec",
                "legend": "Etoile jaune : moyenne de bonnes réponses > 25%, Croix rouge: < 75%"
                }
            ],
            "activity": [
                {
                    "chapter": 9,
                    "student": 112,
                    "dataset": "gp",
                    "subject": "letters",
                    "x": [
                        "a",
                        "i",
                        "e",
                        "o",
                        "u",
                        "l",
                    ],
                    "y": [
                        112,
                        112,
                        112,
                        112,
                        112,
                        112,
                        
                    ],
                    "z": [
                        [
                            "un",
                            "o"
                        ],
                        [
                            "ou",
                            "o"
                        ],
                        [
                            "é",
                            "o"
                        ],
                        [
                            "un",
                            "ou"
                        ],
                        [
                            "o",
                            "un"
                        ],
                        [
                            "d",
                            "j"
                        ],
                        
                    ],
                    "markers": [
                        "star",
                        "star",
                        "star",
                        "star",
                        "star",
                        "star",
                        
                    ],
                    "colors": [
                        "yellow",
                        "yellow",
                        "yellow",
                        "yellow",
                        "yellow",
                        "yellow",
                        
                    ],
                    "xaxis": [
                        "a",
                        "i",
                        "e",
                        "o",
                        "u",
                        "l",
                        
                    ],
                    "yaxis": [
                        112,
                        112,
                        112,
                        112,
                        112,
                        112,
                        112,
                        
                    ],
                }
            ],
            "doc":"",
            "csv":"",
        }
        for p in full_params:
            uri = "{}students/{}/subjects/{}/last".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            if response_code == 200:
                response_data = response.json()
                for k,v in response_model.items():
                    self.assertIn(k,response_data)
                    self.assertEqual(type(v),type(response_data[k]), k)
                for k,v in response_model["activity"][0].items():
                    self.assertIn(k,response_data["activity"][0], k)
                    self.assertEqual(type(v), type(response_data["activity"][0][k]))
                for k,v in response_model["data"][0].items():
                    self.assertIn(k,response_data["data"][0], k)
                    self.assertEqual(type(v), type(response_data["data"][0][k]))

    def test_csv_url(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}students/{}/subjects/{}/last/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            self.assertEqual(r, response_code, uri)

    def test_csv_response(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                
        for p in full_params:
            uri = "{}students/{}/subjects/{}/last/csv".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            csv_doc = response.text.split("<br/>")
            header = csv_doc[0].split(",")
            row = csv_doc[1].split(",")
            self.assertEqual(len(header), len(row), uri)

class TestClassroomDatasetActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_dataset"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username=USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     # print(db)
        #     # print(self.collections)
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    
    def test_api_response_datasets_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("classroom"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_datasets_ok(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("classroom", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_classrooms_ko(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        students = [61, 0, "A", 41, 47]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in datasets]
        full_responses = [c for c in responses for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_classrooms_ok(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("classroom", {"dataset": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
            
    def test_api_format(self):
        datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
        students = [c for c in random.choices(self.coll.distinct("classroom"), k=5)]
        full_params = [[s,d] for d in datasets for s in students]
        response_model = {
            "type": "activity",
            "subject": "letters",
            "subject_name": "Français",
            "dataset": "assessements_language",
            "classroom": 3,
            "csv": "",
            "doc":"",
            "data": [
                {
                "classroom": 3,
                
                "group": "r/m",
                "student": 311,
                "dataset": "assessments_language",
                "subject": "letters",
                "start": "2018-12-11 13:59:02",
                "end": "2019-03-07 14:44:06",
                "timespent": "06:31:32",
                "nb_sequences": 38,
                "nb_days": 26,
                "nb_records": 4722
                },
            ],
            "activity": [
                {
                    "classroom": 3,
                    "group": "r/m",
                    "student": 311,
                    "dataset": "assessments_language",
                    "subject": "letters",
                    "start": "2018-12-11 13:59:02",
                    "end": "2019-03-07 14:44:06",
                    "timespent": "06:31:32",
                    "nb_sequences": 38,
                    "nb_days": 26,
                    "nb_records": 4722
                },
            ]
        }
        for p in full_params: 
            uri = "{}classrooms/{}/datasets/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            for k,v in response_model.items():
                self.assertIn(k,response_data )
                self.assertEqual(type(v), type(response_data[k]), k)
            for k,v in response_model["activity"][0].items():
                self.assertIn(k,response_data["activity"][0], "activity.0."+k)
                self.assertEqual(type(v), type(response_data["activity"][0][k]))
            for k,v in response_model["data"][0].items():
                self.assertIn(k,response_data["data"][0])
                self.assertEqual(type(v), type(response_data["data"][0][k]))
        def test_csv_url(self):
            datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
            full_params = [] 
            full_responses = []
            for d in datasets:
                students = random.choices(self.coll.distinct("classroom", {"dataset": d}), k=5)
                for student in students:
                    full_params.append((student, d))
                    full_responses.append(200)
            for p, r in zip(full_params, full_responses):
                uri = "{}classrooms/{}/datasets/{}/csv".format(self.endpoint, p[0], p[1])
                response = requests.get(uri)
                response_code = response.status_code
                self.assertEqual(r, response_code, uri)

        def test_csv_response(self):
            datasets = ["assessments_language", "assessments_maths", "gp", "numbers", "gapfill_lang"]
            full_params = [] 
            for d in datasets:
                students = random.choices(self.coll.distinct("classroom", {"dataset": d}), k=5)
                for student in students:
                    full_params.append((student, d))
                    
            for p in full_params:
                uri = "{}classrooms/{}/datasets/{}/csv".format(self.endpoint, p[0], p[1])
                response = requests.get(uri)
                response_code = response.status_code
                csv_doc = response.text.split("<br/>")
                header = csv_doc[0].split(",")
                row = csv_doc[1].split(",")
                self.assertEqual(len(header), len(row), uri)

        
class TestClassroomSubjectActivity(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_subject"
        # if ENV != "local":
        #     server = SSHTunnelForwarder(
        #         HOST,
        #         ssh_username=USER,
        #         remote_bind_address=('127.0.0.1', 27017)
        #     )
        #     server.start()
        #     client = pymongo.MongoClient('127.0.0.1', 27017) 
        #     #server.local_bind_port) # server.local_bind_port is assigned local port
        #     self.db = client[DB_NAME]
        #     self.coll = self.db[self.table_name]
        #     # print(db)
        #     # print(self.collections)
        #     server.stop()
        # else:
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.endpoint = "{}/activity/".format(API_URL)
    def test_api_response_subjects_ko(self):
        datasets = ["geometry"]
        students = random.choices(self.coll.distinct("classroom"), k=2)
        full_responses = [406, 406]
        full_params = [(s,d) for s in students for d in datasets]
        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    def test_api_response_subjects_ok(self):
        subjects = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("classroom", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)
    
    def test_api_response_classrooms_ko(self):
        subjects = ["letters", "numbers"]
        students = [61, 0, "A", 41, 47]
        responses = [406, 406, 406, 404, 404]
        full_params = [(s,d) for s in students for d in subjects]
        full_responses = [c for c in responses for x in subjects]
        for p, r in zip(full_params, full_responses):
            
            uri = "{}classrooms/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)

    def test_api_response_classrooms_ok(self):
        subjects = ["letters", "numbers"] 
        full_params = [] 
        full_responses = []
        for subject in subjects:
            students = random.choices(self.coll.distinct("classroom", {"subject": subject}), k=5)
            for student in students:
                full_params.append((student, subject))
                full_responses.append(200)

        for p, r in zip(full_params, full_responses):
            uri = "{}classrooms/{}/subjects/{}".format(self.endpoint, p[0], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
            self.assertEqual(r, response_code, msg)

    def test_api_format(self):
        subjects = ["numbers", "letters"]
        full_params = []
        for s in subjects: 
            classrooms  = random.choices(self.coll.distinct("classroom", {"subject":s}), k=5)
            full_params.extend([[c,s] for s in subjects for c in classrooms])
        response_model = {
            "type": "activity",
            "subject": "letters",
            "subject_name": "Français",
            "classroom": 3,
            "doc": "",
            "csv": "",
            "data": [
                {
                "classroom": 3,
                "datasets": ["assessements_language", "gapfill_lang", "gp"],    
                "group": "r/m",
                "student": 311,
                "subject": "letters",
                "start": "2018-12-11 13:59:02",
                "end": "2019-03-07 14:44:06",
                "timespent": "06:31:32",
                "nb_sequences": 38,
                "nb_days": 26,
                "nb_records": 4722
                },
            ],
            "activity": [
                {
                    "classroom": 3,
                    "group": "r/m",
                    "student": 311,
                    "datasets": ["assessements_language", "gapfill_lang", "gp"],
                    "subject": "letters",
                    "start": "2018-12-11 13:59:02",
                    "end": "2019-03-07 14:44:06",
                    "timespent": "06:31:32",
                    "nb_sequences": 38,
                    "nb_days": 26,
                    "nb_records": 4722
                },
            ]
        }
        
        for p in full_params:
            uri = "{}classrooms/{}/subjects/{}".format(self.endpoint, str(p[0]), str(p[1]))
            response = requests.get(uri)
            response_code = response.status_code
            response_data = response.json()
            for k,v in response_model.items():
                self.assertIn(k,response_data )
                self.assertEqual(type(v), type(response_data[k]), k)
            for k,v in response_model["activity"][0].items():
                self.assertIn(k,response_data["activity"][0], "activity.0."+k)
                self.assertEqual(type(v), type(response_data["activity"][0][k]))
            for k,v in response_model["data"][0].items():
                self.assertIn(k,response_data["data"][0])
                self.assertEqual(type(v), type(response_data["data"][0][k]))
    def test_csv_url(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        full_responses = []
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                full_responses.append(200)
        for p, r in zip(full_params, full_responses):
            classroom = self.db.students.find_one({"student":p[0]})
            uri = "{}classrooms/{}/subjects/{}/csv".format(self.endpoint, classroom["classroom"], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            self.assertEqual(r, response_code, uri)

    def test_csv_response(self):
        datasets = ["numbers", "letters"]
        full_params = [] 
        for d in datasets:
            students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            for student in students:
                full_params.append((student, d))
                
        for p in full_params:
            classroom = self.db.students.find_one({"student":p[0]})
            uri = "{}classrooms/{}/subjects/{}/csv".format(self.endpoint, classroom["classroom"], p[1])
            response = requests.get(uri)
            response_code = response.status_code
            csv_doc = response.text.split("<br/>")
            header = csv_doc[0].split(",")
            row = csv_doc[1].split(",")
            self.assertEqual(len(header), len(row), uri)

if __name__ == '__main__':
    unittest.main()
