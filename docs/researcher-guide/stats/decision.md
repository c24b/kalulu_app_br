File: `db/stats/decision.py`

## DECISION for numbers

- create decision for numbers
- compute avg_decision and add to table
- format into decision_matrix

#### Context

The game 'fish' is proposed at each end of a chapter to be able to pass to next level: the child is proposed two numbers among which he has to choose
the higher.

#### Logs
Log file (stored in `assessments-maths.json` take this form:
```json
{"chapterId":9, "assessmentEndTime":"1548754384", "records":[
{"unixTime":"1548754317", "score":1, "elapsedTime":0.160576, "value":"4"},
{"unixTime":"1548754317", "score":1, "elapsedTime":0.160576, "value":"8"},
{"unixTime":"1548754319", "score":1, "elapsedTime":1.104797, "value":"2"},
{"unixTime":"1548754319", "score":1, "elapsedTime":1.104797, "value":"7"},
]}
```
#### Records

The corresponding logs are stored into the `records` table:
```json
{ "unixTime" : ISODate("2019-06-04T09:47:06Z"), "score" : 0, "value" : "4", "elapsedTime" : 1.016616, "assessmentEndTime" : ISODate("2019-06-04T09:48:26Z"), "tag" : "4", "chapter" : 9, "lesson" : null, "classroom" : 1, "student" : 111, "group" : "r/m", "dataset" : "assessments_maths", "subject" : "numbers", "game" : "fish", "day" : "2019-06-04" }
{ "unixTime" : ISODate("2019-06-04T09:47:06Z"), "score" : 0, "value" : "8", "elapsedTime" : 1.016616, "assessmentEndTime" : ISODate("2019-06-04T09:48:26Z"), "tag" : "8", "chapter" : 9, "lesson" : null, "classroom" : 1, "student" : 111, "group" : "r/m", "dataset" : "assessments_maths", "subject" : "numbers", "game" : "fish", "day" : "2019-06-04" }
{ "unixTime" : ISODate("2019-06-04T09:47:07Z"), "score" : 1, "value" : "2", "elapsedTime" : 0.083434, "assessmentEndTime" : ISODate("2019-06-04T09:48:26Z"), "tag" : "2", "chapter" : 9, "lesson" : null, "classroom" : 1, "student" : 111, "group" : "r/m", "dataset" : "assessments_maths", "subject" : "numbers", "game" : "fish", "day" : "2019-06-04" }
{ "unixTime" : ISODate("2019-06-04T09:47:07Z"), "score" : 1, "value" : "7", "elapsedTime" : 0.083434, "assessmentEndTime" : ISODate("2019-06-04T09:48:26Z"), "tag" : "7", "chapter" : 9, "lesson" : null, "classroom" : 1, "student" : 111, "group" : "r/m", "dataset" : "assessments_maths", "subject" : "numbers", "game" : "fish", "day" : "2019-06-04" }
```

> Here the pair of numbers proposed are (4,8) and (2,7) as elapsedTime and 
> unixTime are the same. Score is 1: it means that the child has chosen the 
> right upper number.

### Student_decision on subject `numbers`

`student_decision` table on subject `numbers` 
stores the following descriptive informations:

- chapter
- lower
- upper
- time_reaction
- difference
- score
- nb_records

That display the information as a table:

|Chapitre | Valeur min | Valeur max |Temps de réaction | Ecart (max-min)| Score | Total|
|---------|------------|------------|------------------|----------------|-------|------|
|         |            |            |                  |                |       |      |

Then it calculates the average for difference over the chapters 

### Student_decision_matrix subject `numbers`

student_decision_matrix from subject "numbers" takes the records of `student_decision` table that have the subject numbers 
and group each record of the same (student, chapter)
by difference (upper-lower) to calculate:

- the median time reaction (median(elapsedTime))
- the % of correct answers (score/nb_records*100)


Then it group it by chapter:
producing for one chapter
- a list of difference
- for each difference the avg median time reaction
- the % of correct answer


|Chapter | Difference | Avg(median_time_reaction)| CA% |
|---------|----------------|-------------------|--------------|
|         |                |                   |              |

This is stored into a matrix and format into a graph structure
to exposed in the API and used in the student page of the dashboard

### Graph student_decision numbers

A slider by chapter allows to select the chapter and displays consequently in:
  - xaxis: the difference (upper-lower)
  - yaxis: avg(median_time_reaction)
  - when hovering on the point(x,y) the % of correct answers is displayed

#### Create student_decision

1. Detect pairs from chapters:

FROM records
WHERE dataset ="assessements_maths'
select DISTINCT student, chapter, (unixTime, elapsedTime)
push tags [lower,upper]
SUM scores/2 
SUM nb_records/2
push elapsedTime.0 as time_reaction
COMPUTE difference (upper-lower)

2. group by (chapter, student, subject, difference)

push score as CA []
push nb_records as nb_records []
push time_reaction as time_reactions []

3. Compute median_time reaction and %CA
(no median available in mongodb using statistics python)
OUT student_decision

#### Compute average

FROM student_decision subject 'numbers'
COMPUTE AVERAGE chapter
INSERT into student_chapter as average

#### Format into matrix

Transform matrix [[[],[],[] ],[[],[],[] ]] into a graph


## DECISION for Letters

The game `fish` is proposed at each end of a chapter to be able to pass to next level: the child is proposed two words one existing one call pseudo among which he has to choose the existing.

- create decision for letters
- compute avg_decision and add to table
- format into decision_matrix

#### Create decision for letters

relies on table `student_tag` that list all the tag and it's corresponding type "word" or "pseudo word"

FROM student_tag
WHERE dataset="gapfill_lang" and group!="guest"
GROUP by "student", "classroom", "chapter", "nb_letters", "type"
FILTER elapsedTime WHERE elapsedTime != 0 
compute median(elapasedTimes)
MERGE INTO student_decision

#### Compute average

FROM student_decision subject 'letters'
COMPUTE AVERAGE chapter as 'average'

#### Format matrix

FROM student_lexical_decision
GROUP INTO A MATRIX
1.  ["$nb_letters", "$time_reactions"]
2. ["$type"]
3. ["chapter"]
OUT student_decision_matrix