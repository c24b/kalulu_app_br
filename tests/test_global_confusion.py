#!/usr/bin/env python3

import unittest
import random
import pymongo

from settings.api import API_URL
from settings.database import DB_NAME

class TestConfusion(unittest.TestCase):
    def setUp(self):
        self.table_name = "confusion"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
    
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 121599)
        self.assertEqual(len(self.coll.distinct("dataset")), 2)
        self.assertEqual(self.coll.count_documents({"dataset":"numbers"}), 108639)
        self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 12960)
    
    def test_record_numbers(self):
        record_model = {
            "dataset" : "numbers",
            "target" : 34,
            "stimulus" : 38,
            "chapter" : 17,
            "avg_CA_rate" : 0.9,
            "avg_WA_rate" : 0.1,
            "nb_records": 1753
        }
        int_values = ["target", "stimulus", "chapter", "nb_records"]
        rates = ["WA_rate", "CA_rate"]
        for record in self.coll.find({"dataset":"numbers", "nb_records": {"$ne":0}}, {"_id":0, "lessons":0}).limit(10):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                if k == "timespent":
                   continue
                elif k != "CV":
                    self.assertEqual(type(v), type(record[k]), k)
                else:
                    self.assertIsNone(record["CV"])
                
                for k in int_values:
                    self.assertIsInstance(record[k], int)
            # if record["nb_records"] == 0:
            #     self.assertIsNone(record["avg_CA_rate"])
            #     self.assertIsNone(record["avg_WA_rate"])
            # else:
            self.assertIsNotNone(record["avg_CA_rate"])
            self.assertLessEqual(record["avg_WA_rate"], 1)
            self.assertGreaterEqual(record["avg_WA_rate"], 0)
            self.assertGreaterEqual(record["avg_CA_rate"], 0)
    
    def test_record_letters(self):
        record_model = {
            "avg_WA_rate" : 0.17,
	        "dataset" : "gp",
	        "chapter" : 18,
	        "stimulus" : "é",
	        "target" : "e",
	        "avg_WA_rate" : 0.83,
            "avg_CA_rate": 0.17,
            "CV": "V"
        }
        int_values = ["chapter"]
        rates = ["WA_rate", "CA_rate"]
        for record in self.coll.find({"dataset":"gp", "nb_records":{"$ne": 0}}, {"_id":0}).limit(10):
            for k,v in record_model.items():
                self.assertIn(k, record.keys())
                if k in int_values:
                    self.assertIsInstance(record[k], int)
                else:
                    self.assertIsInstance(record[k], type(v))
            self.assertIn(record["CV"], ["C", "V"])
            self.assertIsNotNone(record["avg_WA_rate"])
            self.assertIsNotNone(record["avg_CA_rate"])
            self.assertLessEqual(record["avg_WA_rate"], 1)
            self.assertLessEqual(record["avg_CA_rate"], 1)
            self.assertGreaterEqual(record["avg_WA_rate"], 0)
            self.assertGreaterEqual(record["avg_CA_rate"], 0)


class TestConfusionMatrix(unittest.TestCase):
    def setUp(self):
        self.table_name = "confusion_matrix"
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
    def test_table_exists(self):
        self.assertIn(self.table_name, self.db.list_collection_names())
    
    def test_count_records(self):
        self.assertEqual(self.coll.count_documents({}), 55)
    
    def test_count_datasets(self):
        self.assertEqual(len(self.coll.distinct("dataset")), 2)
        self.assertEqual(self.coll.count_documents({"dataset":"numbers"}),27)
        self.assertEqual(self.coll.count_documents({"dataset":"gp"}), 28)
    
    def test_count_chapters(self):
        self.assertEqual(len(self.coll.distinct("chapter")), 20)
    
    def test_matrix_axis_order_letters_V(self):
        raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "V"})
        matrix = raw_confusion["matrix"]
        for i in range(len(matrix)):
            self.assertEqual(matrix[i][0], matrix[i][1][i][0])
    
    def test_matrix_size_letters_V(self):
        raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "V"})
        matrix = raw_confusion["matrix"]
        print(matrix[0])
        col_size = len(matrix[0])
        for c in range(col_size):
            line_size = len(matrix[c][1])
            self.assertEqual(col_size, line_size)
    
    def test_matrix_axis_order_letters_C(self):
        raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "C"})
        matrix = raw_confusion["matrix"]
        for i in range(len(matrix)):
            self.assertEqual(matrix[i][0],matrix[i][1][i][0])
    
    def test_matrix_size_letters_C(self):
        raw_confusion = self.coll.find_one({"dataset": "gp", "CV": "C"})
        matrix = raw_confusion["matrix"]
        col_size = len(matrix)
        for c in range(col_size):
            line_size = len(matrix[c][1])
            self.assertEqual(col_size, line_size)
    
    def test_matrix_axis_order_numbers(self):
        raw_confusion = self.coll.find_one({"dataset": "numbers"})
        matrix = raw_confusion["matrix"]
        for i in range(len(matrix)):
            self.assertEqual(matrix[i][0],matrix[i][1][i][0])
    
    def test_matrix_size_numbers(self):
        raw_confusion = self.coll.find_one({"dataset": "numbers"})
        matrix = raw_confusion["matrix"]
        col_size = len(matrix)
        for c in range(col_size):
            line_size = len(matrix[c][1])
            self.assertEqual(col_size, line_size)

if __name__ == "__main__":
    unittest.main()
