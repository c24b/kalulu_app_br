## Students


### students table
Table `students` consists of the description of the students who have records.

Student is declared at initialization from the list of `files/raw` found corresponding to his id. 
Student is also declared in required file reference `student_group_id.csv` to whom a group and a lang are attached 

- The files_nb consists of the sum of files found for this student

- The group is attached to student throught a reference files called studentid_group.csv and defined by admin

- The status corresponds to status of the student: status False corresponds with two cases:
    
    - files_nb != 0 and group == None: student has files (files_nb > 0) but was missing in studentid_group.csv file. 

    - files_nb == 0 and group != None: the group of the student was declared in in studentid_group.csv file but not files were found.
    

| id | student  | classroom |tablet | kid | group           | files_nb | status | lang|
|----|----------|-----------|-------|-----|-----------------|---------|--------|----|
| 1212 | 1212      | 12       |1    | 2 | "r/m"| 8 | True |  fr  |
| 1222 | 1222      | 12       |2    | 2 | None | 9 | False |     |
| 6022 | 6022      | 61       |2    | 2 | "guest" | 0 | False |  |
| 4111 | 4111      | 41       |1    | 1 | "m/r" | 11 | True |    |


### Student activity

#### day

Table: `student_day`

Script: `db/stats/day.py`

Compute records by student, dataset and day to get : 
- the nb of sequences 
- the timespent
- the records

Different type of treatement for datasets:
- `gp`, `nb` and `gapfill_lang` records 

records > student_dataset_day > student_dataset

- `assessments_maths` and `assessments_language` records 

records > student_dataset_sequence > student_dataset_day_lesson > student_dataset_day > student_dataset

Display the daily activity for one student: sequences are cumulated into lessons
We consider that when a new concept (tag) is proposed: the student validated the previous lesson.

Student_day table is used for defining activity on a subject, on a dataset, 
the progression over lessons and chapters


#### dataset

Table `student_dataset`

Script: `db/stats/activity.py`

FROM student_day
Group by student and by dataset computing timespent, CA, nb_records
OUT into student_dataset

Get global information on a student and  a dataset out from day scope


### subject

Table: `student_subject`
Script: `db/stats/activity.py`

FROM student_day
Group by student and by subject computing timespent, CA, nb_records
OUT into student_subject

Get global information on a student and  a subject out from day scope

### info

Script: `api/namespace/students.py`

Display the contextual information of student activity on subject.
Data came from student_subject and  

### last

Script: `api/namespace/students.py`


### Student progression

#### lesson

Table: `student_lesson` and `student_lessons` 
Script: `db/stats/lesson.py`



#### chapter

Table: `student_chapter` and `student_chapters` 
Script: `db/stats/chapter.py`

student_chapters consists of the overview of student_chapter

```json
    {
        "_id" : ObjectId("5de8156711d14daddedd403d"),
        "student" : 112,
        "classroom" : 1,
        "group" : "r/m",
        "dataset" : "gp",
        "chapter_ids" : [1,2,3,4,5,6,7,8,9],
        "chapter_nb" : 9,
        "tags" : ["z","es","est","gu",..."a","i","e","o"],
        "lessons" : [28,29,30,25,...1,2,3,4],
        "CAs" : [399,1091,610,287,690,1102,1372,1412,2089],
        "nb_records" : [456,1438,799,369,928,1597,1789,1929,2538],
        "timespents" : [1574,5033,3494,1307,3762,7962,4772,7599,5531]
    }
```
### Student tasks

#### decision

#### confusion

### Student numbers

#### association
#### counting
#### identification


### Student letters

#### syllabs

#### words
