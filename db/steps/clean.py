#!/usr/bin/python3
# encoding: utf-8

__doc__ = '''
from raw_data to clean_data
script to clean the datasets
'''
import os
import shutil
from utils import dir_empty
from utils import timeit
from settings import RAW_DIR, CLEAN_DIR

@timeit
def clean(dirs={"from": RAW_DIR, "to": CLEAN_DIR}):
	'''
	``clean()```: 
	Given the absolute dataset path (i.e the folder of the original datasets)
	remove the 1st two lines from each file from this folder 
	and store the result in another dataset folder
	..params  source_dir
	..params target_dir
	'''
	source_dir = dirs["from"]
	if dir_empty(dirs["from"]):
		msg = "Clean(), No student dataset files found in {}".format(default_directories["from"])
		logger.warning(msg)
		return False, msg
	msg = ""
	target_dir = dirs["to"]
	#removing files
	try:
		shutil.rmtree(target_dir)
	except FileNotFoundError:
		pass
	os.makedirs(target_dir)
	
	for _filename in os.listdir(source_dir):
		if _filename.endswith(".json") or _filename.endswith(".save"):
			_filepath = os.path.join(source_dir, _filename)
			last_updated_date = os.path.getmtime(os.path.join(source_dir, _filename))
			# print(last_updated_date)
			with open(_filepath, "r") as f:
				new_filename = _filename.split(" ")[1]
				new_filepath = os.path.join(target_dir, new_filename) 
				with open(new_filepath, "w") as fc:
					try:
						for i, line in enumerate(f.readlines()):
							if i > 1:
								fc.write(line)
						# insert_report(["clean", last_updated_date, _filename, new_filename, "Ok", None, i])
					except Exception as e:
						msg = "step.clean Error: encoutered error {} in filename {} File will not be cleaned.".format(str(e), _filename)
						logger.warning(msg)
						
						# insert_report(["clean", last_updated_date,_filename, new_filename, "Error", str(e), i])
				#change time of the new file
				os.utime(new_filepath, (last_updated_date, last_updated_date))
	# write_csv(report, os.path.join(report_dir, "clean.csv"))
	return True, msg

if __name__ == "__main__":
	dirs = {"to":CLEAN_DIR, "ref":REFERENCES_DIR, "old":ARCHIVED_DIR}
	clean(dirs)
	quit()