#!/usr/bin/python3
# encoding: utf-8

import csv
import datetime
import functools
import json
import logging
import os
import time
import pandas
from datetime import timedelta
from io import BytesIO, StringIO

from csvalidate import ValidatedWriter
from flask import send_file

def check_dirs(dirs, mandatory=['ref', 'from']):
	for dirname, dirpath in dirs.items():
		if dir_exists(dirpath) is False:
			if dirname in mandatory:
				msg = "Directory {} at {} doesn't exists. Aborting executing".format(dirname, dirpath)
				# sys.exit(1)
				return False, msg
			else:
				# logger.info("Directory {} at {} doesn't exists. Creating".format(dirname, dirpath))
				os.makedirs(dirpath)
		if dir_empty(dirpath):
			if dirname in mandatory:
				msg = "Directory {} at {} is empty. Aborting executing".format(dirname, dirpath)
				# sys.exit(1)
				return False, msg
	return True, "" 
def dir_exists(dirpath):
	return os.path.exists(dirpath)

def dir_empty(dirpath):
	return bool(len(os.listdir(dirpath))== 0)

def convert_time(str_timestamp):
	''' From datetime to str YYYY-MM-DD hour:min:seconds''' 
	return datetime.datetime.fromtimestamp(int(str_timestamp)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def convert_to_isodate(str_timestamp):
	''' From datetime to isodate'''
	return datetime.datetime.fromtimestamp(int(str_timestamp))

def convert_to_date(str_timestamp):
	''' From datetime to str YYYY-MM-DD'''
	return convert_to_isodate(str_timestamp).strftime("%Y-%m-%d")

def convert_iso_to_dhms(str_timestamp):
	''' From iso to str YYYY-MM-DD hour:min:seconds'''
	
	return convert_to_isodate(str_timestamp).strftime("%Y-%m-%d %H:%M:%S")

def get_date(datetime_o):
	'''from datatime to str YYYY-MM-DD '''
	return datetime_o.strftime("%Y-%m-%d")

def convert_datetime_to_str(dt):
	'''from datetime to str YYYY-MM-DD HH-MM-SS'''
	dt.strftime("%Y-%m-%d %H:%M:%S")

def convert_timedelta(duration):
	'''from duration to (hour, minutes, seconds) '''
	days, seconds = duration.days, duration.seconds
	hours = days * 24 + seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = (seconds % 60)
	return hours, minutes, seconds

def convert_sec_to_min(seconds):
	'''from seconds to minutes '''
	return (seconds % 3600) // 60

def convert_timestamp(ts):
	'''from timestamp int to datetime'''
	return datetime.datetime.fromtimestamp(int(ts))

def convert_date_to_timestamp(ts):
	'''from timestamp int to datetime'''
	return datetime.datetime.timestamp(ts)

def timedelta(d1, d2):
	'''from timestamp delta to seconds'''
	return((d2 - d1).total_seconds())

def timediff(d1, d2):
	'''from timestamp delta to minutes'''
	d1 = datetime.datetime.fromtimestamp(int(d1))
	d2 = datetime.datetime.fromtimestamp(int(d2))
	c = d2 - d1
	return c / timedelta(minutes=1)

def timeit(func):
	@functools.wraps(func)
	def newfunc(*args, **kwargs):
		startTime = time.time()
		func(*args, **kwargs)
		elapsedTime = time.time() - startTime
		# print(elapsedTime)
		timespent_sec = round(elapsedTime, 2)
		timespent_min = round(elapsedTime / 60, 2)
		msg = "function [{}] finished in {} seconds ({} min.)".format(
			func.__name__, timespent_sec, timespent_min)
		# print(msg)
		# print('function [{}] finished in {} seconds'.format(
		# 	func.__name__, round(elapsedTime, 2)))
		logging.info(msg)
	return newfunc

def get_unique_sequence_list(series):
	result = []
	# unique = set(seq)
	prev = None
	for tag, unixTime in series:
		curr = (tag,unixTime)
		if prev is not None:
			if curr[0] != prev[0]:
				result.append(curr)

		else:
			result.append(curr)
		prev = curr
	timespentlist = []
	for i,l in enumerate(result):
		if i == 0:
			timespentlist.append(l)
		else:
			timediff = timedelta(result[i-1][1], l[1])
			timespentlist.append((l[0], timediff))
	return timespentlist

def get_time_spent_by_unique_sequence(series):
	'''regroup element of a list by unique sequence series
	and calculate timedelta between each unique sequence
	return sum of timespent by sequence
	'''
	timespentlist = get_unique_sequence_list(series)
	return sum([r[1] for r in timespentlist][1:])

def group_unique_series(series):
	'''regroup element of a list by unique sequence series
	Example:
	in: [0,0,0,1,0,1,1,1,1, 2, 2, 2, 1]
	group_unique_series([0,0,0,1,0,1,1,1,1, 2, 2, 2, 1])
	out: [0, 1, 0, 1, 2, 1]
	'''

	result = []
	# unique = set(seq)
	prev = None
	for n in series:
		curr = n
		if prev is not None:
			if curr != prev:
				result.append(n)
		else:
			result.append(n)
		prev = curr
	return result

def unique_seen(seq):
	'''get unique set preserving order'''
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]

def read_json(filename):
	with open(filename, 'r') as f:
		data = json.load(f)
		return data

def write_json(data, filename):
	with open(filename, 'w') as f:
		json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)


def read_csv(filename, delimiter="\t",  encoding="utf-8"):
	with open(filename, "r", encoding=encoding) as f:
		reader = csv.DictReader(f, delimiter=delimiter, quoting=csv.QUOTE_NONE)
		return [dict(n) for n in reader]

def write_csv(data, filename):
	with open(filename, "w") as f:
		writer = csv.writer(f, delimiter='\t')
		for row in data:
			writer.writerow(row)

def write_csv_dict(fieldnames, data, filename):
	with open(filename, "w") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for row in data:
			writer.writerow(row)


def convert_csv_to_df(matrix):
	header = matrix[0]
	return pandas.DataFrame(matrix[1:], columns=header)

def convert_raw_to_df(header, columns):
	return pandas.DataFrame(header, columns=columns)

def convert_json_to_df(adict):
	header = list(adict)
	return pandas.DataFrame(list(adict.values()), columns=header)

def convert_jsonl_to_df(alistofdict):
	header = list(alistofdict[0].keys())
	matrix = []
	for item in alistofdict:
		matrix.append(item.values())
	return pandas.DataFrame(matrix, columns=header)

def convert_df_to_json(df):
	return df.to_dict()


def convert_df_to_csv(df):
	matrix = [df.columns].append(df.values.tolist())
	return matrix


def flatten_records(d, parent_key=[]):
	'''get the last leaf of the tree consisting of a list of records if records is a key'''
	items = []
	for k,v in d.items():
		if not "records" in v.keys():
			items.extend(flatten_records(v))
		else:
			if len(v["records"]) > 0:
				items.extend(v["records"])

	return items


def write_csv(iterable, filename, fields=None, schema=None, delimiter=',',
			  encoding='utf-8', writer_kwargs=None, **kwargs):
	buf = StringIO()
	writer_cls = ValidatedWriter
	if schema:
		writer_cls = ValidatedWriter.from_schema(schema)
	writer_kwargs = writer_kwargs or {}
	writer = writer_cls(buf, fields, delimiter=delimiter, **writer_kwargs)
	writer.writeheader()
	for line in iterable:
		writer.writerow(line)
	return writer
		# buf.seek(0)
	# buf = BytesIO(buf.read().encode(encoding))
	# mimetype = 'Content-Type: text/csv; charset='+encoding
	# print(buf)

def send_csv(iterable, filename, fields=None, schema=None, delimiter=',',
			 encoding='utf-8', writer_kwargs=None, **kwargs):
	buf = StringIO()
	writer_cls = ValidatedWriter
	if schema:
		writer_cls = ValidatedWriter.from_schema(schema)
	writer_kwargs = writer_kwargs or {}
	writer = writer_cls(buf, fields, delimiter=delimiter, **writer_kwargs)
	writer.writeheader()
	for line in iterable:
		writer.writerow(line)
	buf.seek(0)
	buf = BytesIO(buf.read().encode(encoding))
	mimetype = 'Content-Type: text/csv; charset='+encoding

	return send_file(buf, attachment_filename=filename, as_attachment=True,
					 mimetype=mimetype, **kwargs)
def convert_df_to_csv(df):
	return df.to_csv(line_terminator="\n")



def convert_raw_data(raw_data):
    data = pandas.DataFrame(raw_data["data"])
    return data.to_csv(index=None)

	# return data.to_csv(line_terminator='<br/>', index=None)


def convert_data(raw_data):
    data = pandas.DataFrame(raw_data["data"])
    # data.drop(columns=["_id"], axis=1)
    # print(data.head)
    return data.to_csv(line_terminator="\n", index=None)

if __name__ == "__main__":
	pass
