# ACTIVITY

Compute records by student, dataset and day to get : 
- the nb of sequences 
- the timespent
- the records

### Day

Compute records by student, dataset and day to get : 
- the nb of sequences 
- the timespent
- the records

and then aggregate it for a whole dataset and a whole subject

to see how this is calculated consult the documentation on [day](day.md)

### Dataset

Proceeding from [table `student_day`](day.md)

Script `db/stats/dataset.py` groups records and sum timespent along days
to get activity for a student and for a dataset.

```json
{
	"_id" : ObjectId("5ea81d52e4a2eb696fc3157d"),
	"student" : 111,
	"classroom" : 1,
	"group" : "r/m",
	"dataset" : "assessments_language",
	"subject" : "letters",
	"nb_records" : 536,
	"start" : ISODate("2018-11-13T09:41:27Z"),
	"end" : ISODate("2019-02-04T09:02:55Z"),
	"timespent" : 1291,
	"days" : [
		"2018-12-14",
		"2018-11-20",
		"2018-12-10",
		"2018-11-23",
		"2019-01-25",
		"2019-02-04",
		"2018-11-30",
		"2018-11-13"
	],
	"end_date" : "2019-02-04 10:02:55",
	"start_date" : "2018-11-13 10:41:27",
	"timespent_sec" : 1291,
	"timespent_min" : 21.516666666666666,
	"nb_days" : 8,
	"nb_sequences" : 20
}
```

### Subject

Script db/stats/subject.py groups student_dataset by  subject and student 
sum timespent to get global timespent
add records of the subject

```json
{
	"_id" : ObjectId("5ea958d5e4a2eb696fc323d8"),
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
	"start" : ISODate("2018-11-13T09:41:27Z"),
	"end" : ISODate("2019-02-08T11:05:48Z"),
	"timespent" : 1291,
	"end_date" : "2019-02-08 12:05:48",
	"start_date" : "2018-11-13 10:41:27",
	"timespent_sec" : 1291,
	"timespent_min" : 21.516666666666666,
	"days" : [
		"2018-10-15",
		"2018-10-16",
		"2018-10-19",
		"2018-11-05",
		"2018-11-06",
		"2018-11-09",
		"2018-11-12",
		"2018-11-13",
		"2018-11-16",
		"2018-11-19",
		"2018-11-20",
		"2018-11-23",
		"2018-11-26",
		"2018-11-27",
		"2018-11-30",
		"2018-12-03",
		"2018-12-04",
		"2018-12-07",
		"2018-12-10",
		"2018-12-14",
		"2019-01-07",
		"2019-01-08",
		"2019-01-11",
		"2019-01-14",
		"2019-01-15",
		"2019-01-21",
		"2019-01-22",
		"2019-01-25",
		"2019-01-28",
		"2019-01-29",
		"2019-02-01",
		"2019-02-04",
		"2019-02-08"
	],
	"nb_sequences" : 65,
	"nb_days" : 33
}
```