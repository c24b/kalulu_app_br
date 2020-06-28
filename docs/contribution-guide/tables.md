# Tables


## Administrative tables

### From reference

* [path](path.md)
* [references](files.md)
* [datasets](datasets.md)

### From files
* [files](files.md)
* [students](students.md)

### From converted files
* [records](records.md)

## Statistical tables

### Activity
student_day
student_subject
student_dataset

### Progression
student_lesson
student_lessons
lessons

student_chapter
student_chapters

### Tasks

student_confusion
student_confusion_matrix

student_decision
student_decision_matrix

confusion
confusion_matrix


### Letters
student_tag
student_tags
student_syllabs
student_words
words

### Numbers
student_identification
student_association
student_counting




## Sources

Table are created at the end of the downloading and cleaning process
then came from different sources (table references, raw files or computed)

### From references

This two table are created from csv files previously given and stored into dataset/references:

- datasets
- path

### From data

This tables are built by iterating over raw files:

- records
- students
- games

students and games are then corrected for additional files given as references
and stored into datasets/references

#### From computing

These tables are built on the top of main tables: records, dataset and path

- student_info
- student_days
- student_tags
- tags

- student_words
- words

- student_dataset_days
- student_lessons
- lessons
- student_chapters
- chapters

- student_lexical_decision
- global_lexical_decision

- student_lessons_confusion
- student_chapters_confusion
- student_confusion
- confusion

## Tables description and schema

### Dataset


### path

Table path is populated from references files:

- nb_progression_tag.csv
- gp_progression_tag.csv
- stimuli_wordsorting.csv

And updated by adding games from the following files:

- numbers_games_lessons.csv
- letters_games_lessons.csv

| chapter | stimuli | type  | subject   | dataset       | games           |
|---------|---------|-------|-----------|---------------|-----------------|
|  3      | "fée"   | "word"| "letters" | "gapfill_lang |

### Students

|ID  | classroomID  | kidId   | tabletId   |  group                          |
|----|--------------|---------|------------|---------------------------------|
|    |              |         |            | (guest or r/m or m/r)           |


```
{
	"_id" : ObjectId("5d24d04c773b4c1a66a708a2"),
	"ID" : "4053",
	"classroomID" : "40",
	"tabletID" : "5",
	"kidID" : "3"
    "group": ""
}
```
Student table is first populated by iterating throught the raw file list of data
then updated to add the group information from the reference table `student_id_group.csv`


### Records

The main information unit is expressed as a 'record': it consists of all the information stored by the game for any interaction by any student on any dataset.

Records are stored from dataset raw files as one line for one interaction along with the contextual information such as student_id, classroom_id, dataset.

Fields of records vary in the *raw dataset files- provided
insertion script create correspondancy to have same key and value for each record that need to be process (e.g tag)
and compute some field to ease postprocessing (e.g. date)
- gp and numbers:

```json
{
        "unixTime" : ISODate("2019-02-08T11:05:31Z"),
	"isClicked" : 1,
	"score" : 1,
	"elapsedTime" : 1.241623,
	"stimulus" : "é-e",
	"target" : "é-e",
	"classroom" : 1,
	"student" : 111,
	"max_chapter" : 20,
	"max_lesson" : 63,
	"chapter" : 3,
	"lesson" : 9,
	"tag" : "é",
	"value" : "é-e",
	"dataset" : "gp",
	"date" : "2019-02-08",
	"game" : "25"
 }
```

- gapfill_lang
```json
{
	"_id" : ObjectId("5d1b11adbc61b6d221d97f88"),
	"unixTime" : ISODate("2019-01-15T09:30:23Z"),
	"isClicked" : 1,
	"score" : 1,
	"elapsedTime" : 3.762145,
	"stimulus" : "foudre",
	"target" : "foudre",
	"classroom" : 1,
	"student" : 111,
	"word_nb" : 89,
	"chapter" : null, // No chapter info
	"tag" : "foudre", // Computed but not in raw dataset (tag = value = target)
	"value" : "foudre",
	"dataset" : "gapfill_lang",
	"lesson" : null, //No lesson info
	"date" : "2019-01-15",
	"game" : "ants"
}
```
- assessments_maths and assessments_language
```json
{
	"_id" : ObjectId("5d1b1191bc61b6d221d371cb"),
	"unixTime" : ISODate("2019-05-21T09:00:44Z"),
	"score" : 1,
	"elapsedTime" : 0.184267,
	"value" : "7",
	"assessmentEndTime" : ISODate("2019-05-21T09:00:47Z"),
	"tag" : "7",
	"chapter" : 8,
	"lesson" : null,
	"max_chapter" : 20,
	"classroom" : 1,
	"student" : 111,
	"dataset" : "assessments_maths",
	"game" : "fish",
	"date" : "2019-05-21"
}
```


### Student_info

Get some overview of the student

```json
> db.student_info.findOne()
{
	"_id" : ObjectId("5d34f3870b37f027b86a5a2c"),
	"student" : 3031,
	"classroom" : 30,
	"days" : [
		"2019-06-14",
		"2019-06-07",
		...
		"2019-03-21",
		"2019-03-22"
	],
	"datasets" : [
		"gp",
		"assessments_language",
		"numbers",
		"gapfill_lang",
		"assessments_maths"
	],
	"subjects" : [
		"numbers",
		"letters"
	],
	"nb_records" : 8624,
	"start" : ISODate("2018-10-08T09:37:20Z"),
	"end" : ISODate("2019-06-18T09:29:57Z")
}
```

### Student_days

This table presents all the records for a student and a day

{
	"_id" : ObjectId("5d34f6400b37f027b86c4ab4"),
	"student" : 34102,
	"classroom" : 34,
	"day" : "2019-06-04",
	"start" : ISODate("2019-06-04T10:30:32Z"),
	"end" : ISODate("2019-06-04T10:41:58Z"),
	"duration" : 686,
	"datasets" : [
		"assessments_maths"
	],
	"subjects" : [
		"numbers"
	],
	"nb_records:18
}

### Student_dataset_days

{
	"_id" : ObjectId("5d34f77d0b37f027b86eba3b"),
	"student" : 111,
	"classroom" : 1,
	"dataset" : "assessments_language",
	"day" : "2018-11-13",
	"records" : [
		{
			"tag" : "le",
			"unixTime" : ISODate("2018-11-13T09:41:27Z"),
			"score" : 1,
			"chapter" : 2
		},
		{
			"tag" : "ul",
			"unixTime" : ISODate("2018-11-13T09:41:30Z"),
			"score" : 1,
			"chapter" : 2
		},
		{
			"tag" : "ul",
			"unixTime" : ISODate("2018-11-13T09:41:33Z"),
			"score" : 0,
			"chapter" : 2
		},
		...
	]
}

## STUDENTS

### student_info

```json
{
	"_id" : ObjectId("5d49f55384a8b176df23a40c"),
	"student" : 3031,
	"classroom" : 30,
	"days" : [
		"2018-12-03",
		...

	],
	"datasets" : [
		"gp",
		"assessments_language",
		"numbers",
		"gapfill_lang",
		"assessments_maths"
	],
	"subjects" : [
		"numbers",
		"letters"
	],
	"nb_records" : 9014,
	"nb_days" : 62,
	"nb_datasets" : 5,
	"nb_subjects" : 2,
	"start" : ISODate("2018-10-08T09:37:20Z"),
	"end" : ISODate("2019-06-18T09:30:07Z")
}
```

### student_days
```json
{
	"_id" : ObjectId("5d49f56884a8b176df23a74b"),
	"student" : 34102,
	"classroom" : 34,
	"day" : "2019-06-04",
	"start" : ISODate("2019-06-04T10:30:32Z"),
	"end" : ISODate("2019-06-04T10:41:58Z"),
	"duration" : 686,
	"datasets" : [
		"numbers",
		"assessments_maths"
	],
	"subjects" : [
		"numbers"
	],
	"nb_records" : 25
}

```
## LESSONS

### student_lessons
```
{
	"_id" : ObjectId("5d49f5da84a8b176df2439d6"),
	"student" : 111,
	"classroom" : 1,
	"dataset" : "gp",
	"lesson" : 1,
	"chapter" : 1,
	"tag" : "a",
	"timespent" : 1598,
	"%CA" : 76.05321507760532,
	"CA" : 343,
	"TOTAL" : 451,
	"%CA_avg" : 94.73811464137482,
	"%CA_color" : "red",
	"timespent_avg" : 862.1345646437994,
	"timespent_color" : "green"
}

```
### lessons
```
{
	"_id" : ObjectId("5d49f5e284a8b176df260dc1"),
	"dataset" : "gp",
	"lesson" : 44,
	"chapter" : 14,
	"tag" : "au_eau",
	"avg_%CA" : 87.08578552226398,
	"avg_timespent" : 3787.6,
	"std_%CA" : 7.25805337434845,
	"std_timespent" : 5734.082127071429,
	"students" : [
		161,
		4324,
		1941,
		761,
		3863
	],
	"nb_students" : 5
}
```
## CHAPTERS

### student_chapters

```json
{
	"_id" : ObjectId("5d4a04f684a8b176df7bd635"),
	"student" : 34102,
	"classroom" : 34,
	"dataset" : "gp",
	"chapter" : 2,
	"tags" : [
		"l",
		"s",
		"s",
		"l",
		"m",
		"u",
		"s",
		"m",
		"s",
		"m",
		"l",
		"m",
		"s",
		"l",
		"l",
		"m",
		"m",
		"u",
		"s",
		"s",
		"u"
	],
	"stimuli" : [
		"ss-s",
		"s-s",
		"e-%",
		"a-a",
		"None",
		"i-i",
		"",
		"o-o",
		"u-y",
		"u-8",
		"l-l",
		"m-m",
		"o-O"
	],
	"targets" : [
		"u-y",
		"m-m",
		"o-O",
		"ss-s",
		"i-i",
		"e-%",
		"a-a",
		"o-o",
		"s-s",
		"l-l",
		"u-8"
	],
	"CA" : 1658,
	"TOTAL" : 2132,
	"%CA" : 77.76735459662288,
	"hits" : 648,
	"misses" : 158,
	"crs" : 1010,
	"fas" : 316
}

```
### student_chapters_confusion
```json
{
	"_id" : ObjectId("5d4a04ef84a8b176df740baf"),
	"student" : 111,
	"classroom" : 1,
	"dataset" : "gp",
	"chapter" : 1,
	"target" : "a-a",
	"stimulus" : "",
	"tags" : [
		"a",
		"e",
		"i"
	],
	"CA" : 319,
	"TOTAL" : 319,
	"%CA" : 100,
	"hits" : 0,
	"misses" : 0,
	"crs" : 319,
	"fas" : 0
}
```

## TAGS

### tags

## WORDS

### STUDENT WORDS

{
	"_id" : ObjectId("5d4a01e246976c72e102efbf"),
	"classroom" : 1,
	"student" : 153,
	"word" : "aller",
	"ca100" : 100,
	"ca" : 2,
	"nb_records" : 2
}

### WORDS
db.words.findOne()

```
{
	"_id" : ObjectId("5d4a0c4884a8b176df7f3416"),
	"word" : "été",
	"avg_ca100" : 53.33225035050593,
	"avg_nb_records" : 2.385395537525355
}
```

### STUDENT LEXICAL DECISION
```json
{ "_id" : ObjectId("5d4a024446976c72e103b061"), "student" : 111, "classroom" : 1, "chapter" : 2, "nb_letters" : 3, "type" : "pseudoword", "elapsedTimes" : [ 1.473626, 1.038695, 1.071773, 0.937984, 1.086596, 2.492871, 1.656966, 1.256822, 1.305365, 1.524285, 2.058923, 1.673283, 1.237399, 0.92043, 1.78977, 1.558131, 0.78851, 2.160016, 0.820057, 0.786917, 1.889858, 1.990725, 3.027259, 1.305831 ], "median_time_reaction" : 1.3897285, "words" : [ "ilu", "ima", "lum", "slo" ] }
{ "_id" : ObjectId("5d4a024446976c72e103b062"), "student" : 111, "classroom" : 1, "chapter" : 2, "nb_letters" : 3, "type" : "word", "elapsedTimes" : [ 1.354796, 1.056687, 1.190276, 0.837297, 1.157396, 2.426976, 1.371384, 1.254185, 1.021137, 3.651427, 1.406702, 1.221416, 1.035932, 1.005864, 0.953926, 1.020534, 2.879373, 1.606867, 1.506822, 1.137988, 1.121109, 2.709864, 5.053611, 0.954757 ], "median_time_reaction" : 1.205846, "words" : [ "sol", "ami", "mal", "lui" ] }

```
### LEXICAL DECISION

```json
{ "_id" : ObjectId("5d4a0bef84a8b176df7f339b"), "chapter" : 9, "type" : "word", "nb_letters" : 3, "avg_median_time_reaction" : 1.6010204095238096, "words" : [ "zoo", "est", "les", "mes" ] }
```
