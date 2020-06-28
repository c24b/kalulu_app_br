# Progression

Files: `API/namespaces/progression.py`, `API/csv_blueprint/progression.py` 


Progression category endpoint exposes the progression of a [student](stats/students.md) or a [classroom](stats/students.md) on a [dataset](stats/datasets.md) based on his [records](stats/records.md) and the [pedagogical progression path](stats/path.md).

Progression is defined by the records of each student which indicate the notion introduced. Records are split into lesson each time a new notion is introduced: progression relies on 3 tables in the database: 


- `student_lesson`
- `lessons`
- `student_chapter`


## Student_lesson

Each notion is attached to a lesson and a chapter into the table [path](stats/path.md).  

At insertion step, the corresponding lesson and chapter is attached to the record notion: each record is qualified by the lesson, chapter, unixTime and day and stored into table `student_day`

To see how student_lesson table is calculated and updated consult [lesson documentation](stats/lesson.md) 

## Lessons 

To see how lessons table is calculated consult [lesson documentation](stats/lesson.md)

## Student_chapter

To see how chapter is calculated consult [chapter](stats/chapter.md)