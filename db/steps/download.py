#!/usr/bin/python3
# encoding: utf-8

__doc__ = '''
download the files from ftp server /ssh server
'''

import sys
import os
import shutil
import argparse
from datetime import datetime as dt
import subprocess
from utils import timeit, dir_empty
from settings.src_server import SRC_DIR, HOST, LOGIN

@timeit
def archive_datasets(target_dir, ref_dir):
    '''archive previously downloaded datasets changing from (*.json|*.save) into .old'''
    archived_d = os.path.join(ref_dir, "raw") 
    files = os.listdir(target_dir)
    counter = 0
    for f in files:
        if not os.path.isdir(f):
            # logger.info("archive_datasets() Archiving {} into {}".format(os.path.join(target_dir,f), archived_d))
            counter +=1
            try:
                shutil.move(os.path.join(target_dir,f), archived_d)
            except shutil.Error:
                os.remove(os.path.join(target_dir,f))
    # ref_dir = os.path.join(ref_dir, "raw")
    # counter = 0
    # for _file in os.listdir(target_dir):
    #     new_file = os.path.join(ref_dir, _file)
    #     _file = os.path.join(target_dir, _file)
        
    #     if not os.path.isdir(_file):
    #         if ".old" in _file:
    #             os.remove(_file)
    #         elif ".listing" in _file:
    #             pass
    #         else:
    #             counter += 1 
    #             new_file = new_file + ".old"
    #             os.rename(_file, new_file)
    #             insert_report(["archive", dt.now(), _file, new_file, True, "archived", 1])
    # insert_report(["info", "archive", dt.now(), target_dir, archived_d, True, "Raw files archived", counter])
    # return (True, "", counter)

@timeit    
def cmd_download_datasets(host, login, source_dir, target_dir):
    print("Download dataset")
    extension_filter="'*{.save,.json}'"
    bashCommand = "scp -p -r {}@{}:{}\'{}\' {}/".format(
            login, host, source_dir, extension_filter, target_dir)
    os.system(bashCommand)
    

@timeit    
def download_datasets(host, login, source_dir, target_dir):
    from paramiko import SSHClient
    from scp import SCPClient
    print("Download datasets into {}".format(target_dir))
    ssh = SSHClient()
    ssh.load_host_keys('.ssh/known_hosts')
    # ssh.load_system_host_keys()
    # ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=login)
    with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path=source_dir+"*.json", local_path=target_dir)
        scp.get(remote_path=source_dir+"*.save", local_path=target_dir)
        
@timeit        
def download(dirs, host=HOST, login=LOGIN, src_dir=SRC_DIR):
    '''
    download() copy dataset_files  from doc server defined in _settings.py to filepath <project_dir>/datasets/raw
        :param raw_dir: directory path where are stored datasets downloaded default <project_dir>/datasets/raw/ 
        :param archived_dir: directory path where are stored previous datasets archived default <project_dir>/datasets/archived/
        :params host: hostname of server where to download the raw file default set in _setting.py
        :params login: login of server where to download the raw file default set in _setting.py
        :params src_dir: directory path where raw files are stored in the server
        :type raw_dir: str
        :type archived_dir: str
        :type host: str
        :type login: str
        :type src_dir: str
        :return: None
        
    ''' 
    archive_datasets(dirs["from"], dirs["old"])
    archive_datasets(dirs["to"], dirs["old"])
    cmd_download_datasets(HOST, LOGIN, SRC_DIR, dirs["from"])
    # download_datasets(HOST, LOGIN, SRC_DIR, raw_dir)
    # generate_report(raw_dir)                
    return dir_empty(dirs["from"]), ""

if __name__ == "__main__":
    dirs = {"to":CLEAN_DIR, "ref":REFERENCES_DIR, "old":ARCHIVED_DIR}
    download(dirs, HOST, LOGIN, SRC)
    quit()
