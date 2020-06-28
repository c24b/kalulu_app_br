import unittest
import pymongo
import requests
from sshtunnel import SSHTunnelForwarder
import os
# from os import listdir
# from os.path import isfile, join
import subprocess

from settings import DIRS, DATASETS_DIR, RAW_DIR, CLEAN_DIR, REFERENCES_DIR
from settings import DB_NAME

raw_files = 13549
clean_files = 11859
records = 10067554

class TestFiles(unittest.TestCase):
    def test_dirs_exists(self):
        # dataset_dirs = [DATASETS_DIR, RAW_DIR, CLEAN_DIR, REFERENCES_DIR]
        for d in DIRS:
            exists = "test -d {} && echo True || echo False;".format( d)
            process = subprocess.Popen(exists.split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout,stderr = process.communicate()
            if stderr is None:
                exists = (stdout).decode("utf-8").strip()
            else:
                std_error = (stderr).decode("utf-8").strip()
            self.assertEqual("True", exists, "Directory {} is missing".format(d))    
            
    def test_raw_files(self):
        '''Test nb files in datasets/raw'''
        process = subprocess.Popen(cmd, shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = process.communicate()
        if stderr is None:
            nb = int((stdout).decode("utf-8").strip()) 
        else:
            std_error = (stderr).decode("utf-8").strip()
        self.assertEqual(nb, 13549, "Missing files in {}: {}".format(RAW_DIR, nb-13549))
    
    def test_clean_files(self):
        '''Test nb files in datasets/raw'''
        exists = "test -d {} && echo True || echo False;".format(RAW_DIR)
        cmd = ["ls", "-l", CLEAN_DIR, "|", "wc", "-l"]
        process = subprocess.Popen(exists.split(" "), shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = process.communicate()
        
        if stderr is None:
            exists = (stdout).decode("utf-8").strip() 
        else:
            std_error = (stderr).decode("utf-8").strip()
        self.assertEqual("True", exists, "Directory {} is missing".format(CLEAN_DIR))

        
        process = subprocess.Popen(cmd, shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = process.communicate()
        if stderr is None:
            nb = int((stdout).decode("utf-8").strip()) 
        else:
            std_error = (stderr).decode("utf-8").strip()
        self.assertEqual(nb, 11859, "Missing files in {}: {}".format(CLEAN_DIR, nb-11859))
    
    def test_reference_files(self):
        '''Test nb files in datasets/raw'''
        cmd = ["ls", "-l", REFERENCES_DIR, "|", "wc", "-l"]
        exists = "test -d {} && echo True || echo False;".format(RAW_DIR)
        process = subprocess.Popen(exists.split(" "), shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = process.communicate()
        
        if stderr is None:
            exists = (stdout).decode("utf-8").strip() 
        else:
            std_error = (stderr).decode("utf-8").strip()
        self.assertEqual("True", exists, "Directory {} is missing".format(REFERENCES_DIR))

        process = subprocess.Popen(cmd, shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = process.communicate()
        if stderr is None:
            nb = int((stdout).decode("utf-8").strip()) 
        else:
            std_error = (stderr).decode("utf-8").strip()
        self.assertEqual(nb, 16, "Missing files in {}: {}".format(REFERENCES_DIR, nb-16))

    def test_records(self):
        self.table_name = "records" 
        client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = client[DB_NAME]
        self.coll = self.db[self.table_name]
        self.assertEqual(records, self.coll.count(), "Missing {} records".format(self.coll.count() - records))

if __name__ == '__main__':
    unittest.main()