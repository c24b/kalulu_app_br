## DAY

File : `stats/day.py`

Compute records by student, dataset and day to get : 
- the nb of sequences 
- the timespent
- the records


student_day table is required to define
- `activity`:
    - `student_dataset` at student and dataset level
    - `student_subject` at student and subject level
- `progression`:
    - `lesson`: at student and dataset level 
    - `chapter`: at student and dataset level

Different type of treatement for datasets:
- `gp`, `nb` and `gapfill_lang` records 

 records (GP, NB, GAPFILL_LANG) > student_day

- `assessments_maths` and `assessments_language` records 

 records (ASSESSMENTS_LANGUAGE, ASSESSMENTS_MATHS) > student_dataset_sequence > student_dataset_day_lesson > student_dataset_day > student_dataset


### For gapfill_lang, nb, gp

- records > student_dataset_day > student_dataset

> Time unit is day: into records table day is attached to each records: so first aggregation consists of grouping dataset of a student by day and sorted to create new table student_day

> Timespent is calculated following this steps:
- records are sorted by unixTime and corresponds to ISODate
- end and start are respectively last and first record unixTime in ISODate
- timespent is the result of subtraction between end and start using [subtract operation]
https://docs.mongodb.com/manual/reference/operator/aggregation/subtract/#subtract-two-dates
expressed in milliseconds
- timespent is then divided by 1000 to transform milliseconds in seconds

Added multiple control values
```
"end_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$end",  "timezone": "Europe/Paris"} },
"start_date": { "$dateToString": { "format": "%Y-%m-%d %H:%M:%S", "date": "$start",  "timezone": "Europe/Paris"} },
"timespent_sec": {"$divide": [{"$subtract": ["$end", "$start"]}, 1000]},
"timespent_min": {"$divide": [{"$subtract": ["$end", "$start"]}, 60000]},
"timespent_hms": { "$dateToString": { "format": "%H:%M:%S", "date": {"$toDate":{"$divide": [{"$subtract": ["$end", "$start"]}, 1000]}}, "timezone": "Europe/Paris"} },
"sum_elapsedTime": {"$sum": {"$records.elpasedTime"}}
```

```sql
# pseudo code in SQL
FROM RECORDS 
SELECT record
GROUP BY student,dataset,day
SORTED BY student, dataset and unixtime
SELECT FIRST unixTime LAST unixTime
CALCULATE timespent (LAST-FIRST)
INSERT into student_day

```


### For assessments_maths, assessments_language

- records > student_dataset_sequence > student_dataset_day_lesson > student_dataset_day > student_dataset

> Time unit is day: into records table day is attached to each records 
but assessments are ordered by chapters and assessmentEndTime means that records of same chapter can belong to different days

> Timespent is calculated following this steps:
- records are grouped by assessmentEndTime and sorted by unixTime to define a sequence with a start and an end that corresponds to assessementEndTime
- we  compute the timespent within the sequence
- timespent is the result of subtraction between end and start using [subtract operation]
(https://docs.mongodb.com/manual/reference/operator/aggregation/subtract/#subtract-two-dates)
expressed in milliseconds
- timespent is then divided by 1000 to transform milliseconds in seconds
- group sequence then by day and sum the timespent and concatenate records



```sql
FROM records
WHERE dataset in ["assessments_maths", "assessments_language"]
Group RECORDS by UNIQUE classroom, student, subject, dataset, day, assessmentEndTime AS sequence
SORT records by start(unixTime) and assessementEndTime
GROUP by UNIQUE classroom, student, subject, dataset, day
COMPUTE timespent 
MERGE into student_day
```

