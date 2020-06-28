
File: `db/stats/chapter.py`

student_chapter is defined by grouping student records by chapter into student_lesson table

```
FROM table student_lesson
group by chapter student and dataset
Available only for dataset="gp" and dataset="numbers"
OUT student_chapter
```