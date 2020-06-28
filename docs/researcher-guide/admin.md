# Admin 

Admin endpoint provides interface facilities to manage the data at different levels:

- students
- classrooms
- files
- path

## Student

```
SELECT * from table students
See [stats/students.md]
```

Students table is created at insertion with the [references file](../contribution-guide/files.md) `student_group_id.csv`
and updated with the downloaded files to determine the status of the student:

- missing if no group has been found
- empty if student has not been declared in reference file


## Classroom

Classroom relies on students table and is simply a group of all students by classroom

```
SELECT student FROM table student
SORT by student.classroom
```

See [stats/students.md](stats/students.md)

## Files

Files give access to files table wich list all the files from download to insertion, the corresponding records found for this file the status with eventually the error attached

`SELECT * from files`

See [stats/files.md](stats/files.md)

## Path

Table path is built at initialization of the database

`SELECT * from path`
See [stats/path.md](stats/path.md)
