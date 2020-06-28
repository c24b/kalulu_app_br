import unittest
import random
import pymongo
import requests
from sshtunnel import SSHTunnelForwarder

from settings.api import API_URL
from settings.database import DB_NAME


class TestStudentConfusion(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_confusion"
        client = pymongo.MongoClient('127.0.0.1', 27017) 
        #server.local_bind_port) # server.local_bind_port is assigned local port
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.students = random.choices(self.coll.distinct("student"), k=5)
        self.subjects = ["letters", "numbers"]
        self.datasets = ["gp", "numbers"]
        self.endpoint = "{}/tasks/confusion/".format(API_URL)
        
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 3679386)
    
    def test_count_datasets(self):
        self.assertEqual(len(self.coll.distinct("dataset")), 2)
        self.assertEqual(self.coll.count_documents({"dataset":"numbers"}), 2370203)
        self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 1309183)
    def test_count_students(self):
        self.assertEqual(len(self.coll.distinct("student")), 804)
    def test_count_chapters(self):
        self.assertEqual(len(self.coll.distinct("chapter")), 20)
    def test_record_numbers(self):
        record_model = {
            "student" : 1651,
            "dataset" : "gp",
            "chapter" : 1,
            "CV" : None,
            "target" : 1,
            "stimulus" : 1,
            "timespent" : 47.736482,
            "WA_rate" : 0.09195402298850575,
            "CA_rate" : 0.9080459770114943,
            "CA" : 79,
            "nb_records" : 87,
            # "lessons" : [
            #     1,
            #     2,
            #     3,
            #     4
            # ]
        }

        int_values = ["target", "stimulus", "chapter"]
        rates = ["WA_rate", "CA_rate", "CA"]
        for record in self.coll.find({"dataset":"numbers"}, {"_id":0, "lessons":0}).limit(50):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                if k not in ["timespent"] + rates:
                    if  k != "CV":
                        self.assertEqual(type(v), type(record[k]), k)
                    else:
                        self.assertIsNone(record["CV"])
                
            for k in int_values:
                self.assertIsInstance(record[k], int)
            if record["nb_records"] == 0:
                self.assertIsNone(record["WA_rate"])
                self.assertIsNone(record["CA_rate"])
                self.assertIsNone(record["CA"])
            else:
                self.assertIsNotNone(record["WA_rate"])
                self.assertIsNotNone(record["WA_rate"])
                self.assertIsNotNone(record["CA"])
                self.assertLessEqual(record["WA_rate"], 1)
                self.assertLessEqual(record["CA_rate"], 1)
                self.assertGreaterEqual(record["WA_rate"], 0)
                self.assertGreaterEqual(record["CA_rate"], 0)

    def test_record_letters(self):
        record_model = {
            "student" : 1651,
            "dataset" : "gp",
            "chapter" : 2,
            "CV" : "C",
            "target" : "l",
            "stimulus" : "l",
            "timespent" : 83.633428,
            "WA_rate" : 0.1515151515151515,
            "CA_rate" : 0.8484848484848485,
            "nb_records" : 33,
            "CA" : 24,
            
        }
        int_values = ["chapter"]
        rates = ["WA_rate", "CA_rate"]
        for record in self.coll.find({"dataset":"gp"}, {"_id":0}).limit(50):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                self.assertIn(record["CV"], ["C", "V"])
                for k in int_values:
                    self.assertIsInstance(record[k], int)
                if record["nb_records"] == 0:
                    self.assertIsNone(record["WA_rate"])
                    self.assertIsNone(record["CA_rate"])
                    self.assertIsNone(record["CA"])
                else:
                    self.assertIsNotNone(record["WA_rate"])
                    self.assertIsNotNone(record["WA_rate"])
                    self.assertIsNotNone(record["CA"])
                    self.assertLessEqual(record["WA_rate"], 1)
                    self.assertLessEqual(record["CA_rate"], 1)
                    self.assertGreaterEqual(record["WA_rate"], 0)
                    self.assertGreaterEqual(record["CA_rate"], 0)
    
    def test_csv(self):
        for subject in self.subjects:
            for student in self.students:
                uri = "{}students/{}/subjects/{}/csv".format(self.endpoint, student, subject)
                response = requests.get(uri)
                self.assertEqual(response.status_code, 200, uri)
                csv_doc = response.text.split("<br/>")
                header = csv_doc[0].split(",")
                row = csv_doc[1].split(",")
                self.assertEqual(len(header), len(row), uri)


class TestStudentConfusionMatrix(unittest.TestCase):
    def setUp(self):
        self.table_name = "student_confusion_matrix"
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
            server.stop()
        else:
            client = pymongo.MongoClient('127.0.0.1', 27017)
            self.db = client[DB_NAME]
            self.coll = self.db[self.table_name]
        self.students = random.choices(self.coll.distinct("student"), k=5)
        self.subjects = ["letters", "numbers"]
        self.datasets = ["gp", "numbers"]
        self.endpoint = "{}/tasks/confusion/".format(API_URL)
    # def test_table_exists(self):
    #     '''Test if table exists'''
    #     self.assertIn(self.table_name, self.db.list_collection_names())
    # def test_count_records(self):
    #     ''' Test nb of records in table'''
    #     self.assertEqual(self.coll.count_documents({}), 13941)
    
    # def test_count_datasets(self):
    #     self.assertEqual(len(self.coll.distinct("dataset")), 2)
    #     self.assertEqual(self.coll.count_documents({"dataset":"numbers"}), 5369)
    #     self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 8572)
    # def test_count_students(self):
    #     self.assertEqual(len(self.coll.distinct("student")), 804)
    # def test_count_chapters(self):
    #     self.assertEqual(len(self.coll.distinct("chapter")), 20)
        
    # def test_matrix_axis_order_letters_V(self):
    #     '''test order of the matrix'''
    #     raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "V"})
    #     matrix = raw_confusion["matrix"]
    #     for i in range(len(matrix)):
    #         self.assertEqual(matrix[i][0],matrix[i][1][i][0])
    # def test_matrix_size_letters_V(self):
    #     '''test size of the matrix: should be squared'''
    #     raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "V"})
    #     matrix = raw_confusion["matrix"]
    #     col_size = len(matrix)
    #     for c in range(col_size):
    #         line_size = len(matrix[c][1])
    #         self.assertEqual(col_size, line_size)
    # def test_matrix_axis_order_letters_C(self):
    #     '''test order of the matrix'''
    #     raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "C"})
    #     matrix = raw_confusion["matrix"]
    #     for i in range(len(matrix)):
    #         self.assertEqual(matrix[i][0],matrix[i][1][i][0])
    # def test_matrix_size_letters_C(self):
    #     '''test size of the matrix: should be squared'''
    #     raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "C"})
    #     matrix = raw_confusion["matrix"]
    #     col_size = len(matrix)
    #     for c in range(col_size):
    #         line_size = len(matrix[c][1])
    #         self.assertEqual(col_size, line_size)
    # def test_matrix_axis_order_numbers(self):
    #     raw_confusion = self.coll.find_one({"dataset": "numbers"})
    #     matrix = raw_confusion["matrix"]
    #     for i in range(len(matrix)):
    #         self.assertEqual(matrix[i][0],matrix[i][1][i][0])
    # def test_matrix_size_numbers(self):
    #     '''test size of the matrix: should be squared'''
    #     raw_confusion = self.coll.find_one({"dataset": "numbers"})
    #     matrix = raw_confusion["matrix"]
    #     col_size = len(matrix)
    #     for c in range(col_size):
    #         line_size = len(matrix[c][1])
    #         self.assertEqual(col_size, line_size)
    # def test_status_api_subjects_ko(self):
    #     datasets = ["geometry"]
    #     full_params = [] 
    #     full_responses = []
    #     for d in datasets:
    #         students = random.choices(self.coll.distinct("student"), k=5)
    #         for student in students:
    #             full_params.append((student, d))
    #             full_responses.append(406)
    #     for p, r in zip(full_params, full_responses):
    #         uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         response_data = response.json()
    #         msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
    #         self.assertEqual(r, response_code, msg)
        
    # def test_status_api_students_ko(self):
    #     datasets = ["letters", "numbers"]
    #     students = [608787, 110, "A", 455]
    #     responses = [406, 406, 406, 404]*2
    #     full_params = [(s,d) for s in students for d in datasets]
    #     full_responses = [c for c in responses for d in datasets]
    #     for p, r in zip(full_params, full_responses):
    #         uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
    #         # print(p, uri)
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         response_data = response.json()
    #         msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, response_code, 200, response_data)
    #         self.assertEqual(r, response_code, msg)
        
    # def test_status_api_students_ok(self):
    #     for student in random.choices(self.coll.distinct("student", {"subject":"letters"}), k= 3):
    #         uri = "{}students/{}/subjects/letters".format(self.endpoint, student)
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         response_data = response.json()
    #         msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, response_code, 200, response_data)
    #         self.assertEqual(response_code, 200, msg)
    #     for student in random.choices(self.coll.distinct("student", {"subject":"numbers"}), k= 3):
    #         uri = "{}students/{}/subjects/numbers".format(self.endpoint, student)
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         response_data = response.json()
    #         msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, response_code, 200, response_data)
    #         self.assertEqual(response_code, 200, msg)
        
    
    def test_api_chapters(self):
        for s in ["numbers", "letters"]:
            students = random.choices(self.coll.distinct("student", {"subject": s}), k=2)
            
            for sid in students:
                uri = "{}students/{}/subjects/{}".format(self.endpoint, sid, s)
                response = requests.get(uri)
                response_code = response.status_code
                try:
                    response_data = response.json()
                except Exception:
                    raise Exception(uri, response_code)
                chapters = response_data["chapters"]
                matrix = response_data["confusion"][0]
                self.assertEqual(list(set(chapters)), chapters, (s,sid, uri))
                self.assertEqual(chapters, sorted(chapters))
                matrix_data  = matrix["data"]
                data_chapter = [n["chapter"] for n in matrix_data]
                self.assertEqual(list(set(data_chapter)), data_chapter, (s,sid, uri))
                
                self.assertEqual(chapters, data_chapter)
                
                self.assertEqual(len(chapters), len(matrix_data), (s,sid, uri))
                if s == "numbers":
                    continue
                elif s == "letters":
                    matrix2 = response_data["confusion"][1]
                    matrix2_data  = matrix2["data"]
                    data_chapter2 = [n["chapter"] for n in matrix2_data]
                    self.assertEqual(data_chapter, data_chapter2, chapters)
                    self.assertEqual(list(set(data_chapter2)), data_chapter2)
                    self.assertEqual(len(matrix), len(matrix2), len(chapters))

    def test_api_axis(self):
        for subject in ["numbers", "letters"]:
            students = random.choices(self.coll.distinct("student", {"subject": subject}), k=1)
            for student in students:
                uri = "{}students/{}/subjects/{}".format(self.endpoint, student,subject)
                response = requests.get(uri)
                response_code = response.status_code
                response_data = response.json()
                matrix = response_data["confusion"][0]
                x_axis = matrix["xaxis"]
                y_axis = matrix["yaxis"]
                matrix_first = matrix["data"][0]
                matrix_last = matrix["data"][-1]
                matrix_random = random.choice(matrix["data"])
                first_col = [n[0] for n in matrix_first["matrix"]]
                # last_col = [n[0] for n in matrix_last["matrix"]]
                # random_col = [n[0] for n in matrix_random["matrix"]]
                # self.assertEqual(last_col, first_col, random_col)
                # self.assertEqual(last_col, x_axis, (subject, student))
                # self.assertEqual(first_col, x_axis, (subject, student))
                # self.assertEqual(random_col, x_axis, (subject, student))
                first_line = [[i[0] for i in n[1]] for n in matrix_first["matrix"]]
                print(first_col, first_line)
                # last_line = [[i[0] for i in n[1]] for n in matrix_last]
                # random_line = [[i[0] for i in n[1]] for n in matrix_random]
                # self.assertEqual(last_line, first_line, random_line)
                # self.assertEqual(last_line, x_axis, (subject, student))
                # self.assertEqual(first_line, x_axis, (subject, student))
                # self.assertEqual(random_line, x_axis, (subject, student))
                # for x,y,z in zip(first_line, last_line, random_line):                   
                #     self.assertEqual(x, x_axis, y_axis)
                #     self.assertEqual(y, x_axis, y_axis)
                #     self.assertEqual(z, x_axis, y_axis)
                # for x,y,z in zip(first_col, last_col, random_col):                   
                #     self.assertEqual(x, x_axis, y_axis)
                #     self.assertEqual(y, x_axis, y_axis)
                #     self.assertEqual(z, x_axis, y_axis)
    # def test_chapter_order(self):
    #     full_params = [] 
    #     full_responses = []
    #     for d in ["numbers", "letters"]:
    #         students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
    #         for student in students:
    #             full_params.append((student, d))
    #             full_responses.append(200)

    #     for p, r in zip(full_params, full_responses):
    #         uri = "{}students/{}/subjects/{}".format(self.endpoint, p[0], p[1])
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         response_data = response.json()
    #         msg = "Wrong response code for {}: actual {} and expected {}. {}".format(uri, r, response_code, response_data)
    #         chapters = response_data["chapters"]
    #         x_axis = [n["chapter"] for n in response_data["confusion"][0]["data"]]
    #         self.assertEqual(chapters, x_axis)
    #         self.assertEqual(x_axis, sorted(x_axis))
    #         self.assertEqual(len(chapters), len(response_data["confusion"][0]["data"]))
    
    # def test_response_format_api(self):
    #     record_model ={
    #         "type": "confusion",
    #         "student": 112,
    #         "subject": "letters",
    #         "title": "Lettres",
    #         "CV": [
    #             "V",
    #             "C"
    #         ],
    #         "titles": [
    #             "Voyelles",
    #             "Consonnes"
    #         ],
    #         "subject_name": "Français",
    #         "chapters": [
    #             1,
    #             2,
    #             3,
    #             4,
    #             5,
    #             6,
    #             7,
    #             8,
    #             9
    #         ],
    #         "confusion": []
    #     }
    #     confusion_model = [
    #         {
    #         "chapters": [
    #             1,
    #             2,
    #             3,
    #             4,
    #             5,
    #             6,
    #             7,
    #             8,
    #             9
    #         ],
    #         "title": "Voyelles",
    #         "CV": "V",
    #         "xaxis": [
    #             "a",
    #             "i",
    #             "e",
    #             "o",
    #             "u",
    #             "é",
    #             "ou",
    #             "un",
    #             "es",
    #             "est"
    #         ],
    #         "yaxis": [
    #             "a",
    #             "i",
    #             "e",
    #             "o",
    #             "u",
    #             "é",
    #             "ou",
    #             "un",
    #             "es",
    #             "est"
    #         ],
    #         "xaxis_label": "Valeur proposée",
    #         "yaxis_label": "Cible",
    #         "data": []
    #             }
    #     ]
    #     data_model = {
    #       "student": 112,
    #       "subject": "letters",
    #       "dataset": "gp",
    #       "chapter": 1,
    #       "CV": "V",
    #       "matrix": []
    #     }
    #     full_params = [] 
    #     for d in ["numbers", "letters"]:
    #         students = random.choices(self.coll.distinct("student", {"subject": d}), k=2)
    #         for student in students:
    #             full_params.append((student, d))
    #     for student,d in full_params:
    #         uri = "{}students/{}/subjects/{}".format(self.endpoint, student, d)
    #         response = requests.get(uri)
    #         response_code = response.status_code
    #         self.assertEqual(response_code, 200, uri)
    #         response_data = response.json()
    #         for k, v in record_model.items():
    #             self.assertIn(k, response_data)
    #             self.assertIsInstance(v, type(v)) 
    #         if d == "letters":
    #             self.assertEqual(response_data["subject"], "letters")
    #             self.assertEqual(response_data["subject_name"], "Français")
    #             self.assertEqual(response_data["title"], "Lettres")
    #             self.assertEqual(len(response_data["titles"]), 2)
    #             self.assertEqual(len(response_data["CV"]), 2)
    #         else:
    #             self.assertEqual(response_data["subject"], "numbers")
    #             self.assertEqual(response_data["subject_name"], "Maths")
    #             self.assertEqual(response_data["title"], "Nombres")
    #             self.assertEqual(len(response_data["titles"]), 1)
    #             self.assertEqual(len(response_data["CV"]), 1)
            
    #         self.assertEqual(len(response_data["confusion"][0]["xaxis"]), len(response_data["confusion"][0]["yaxis"]))
    #         self.assertEqual(len(response_data["confusion"][-1]["xaxis"]), len(response_data["confusion"][-1]["yaxis"]))
               
    # def test_matrix(self):
    #     ''' Test matrix on a single chapter '''
    #     for d in ["numbers", "letters"]:
    #         students = random.choices(self.coll.distinct("student", {"subject": d}), k=5)
            
    #         for student in students:
    #             uri = "{}students/{}/subjects/{}".format(self.endpoint, student, d)
    #             response = requests.get(uri)
    #             response_code = response.status_code
    #             api_data = response.json()
    #             db_data = self.coll.find_one({"student":student, "subject":d}, {"_id":0})
    #             # print(db_data["xaxis"])
    #             # print(db_data["yaxis"])
    #             cols = [n[0] for n in db_data["matrix"]]
                
    #             self.assertEqual(cols, db_data["xaxis"], db_data["yaxis"])
    #             lines = [[i[0] for i in n[1]] for n in db_data["matrix"]]
    #             # print("Lines", lines[0], student, d)
                
    #             self.assertTrue(all([len(x) for x in lines]))
    #             self.assertTrue(lines[0], db_data["xaxis"])
    #             # self.assertEqual(lines, db_data["xaxis"], db_data["yaxis"])
                
if __name__ == '__main__':
    unittest.main()