
## Stats

Stats is a python package that groups all the **scripts** that generates the tables for analyzing the records throught defined metrics.

Stats tables are built upon reference tables built at [init](./steps.md##Init) and [insert](./steps.md##Insert) preliminary steps:

- `datasets`
- `students`
- `path`
- `records` 

> For readability reasons and dependency relations between tables(that need to build tables a specific order), 
> we regrouped the table generation scripts into categorized functions inside the stats package __init__ that create shortcuts for scripts calls and corresponds roughly to API endpoints .

* Consult all the stats available at student level in (students.md)
* Consult all the stats available at global level in (global.md)

### Dependencies schema

Proceeding from table `records`:

- [day](../researcher-guide/stats/day.md)
    - [dataset](../researcher-guide/stats/datasets.md)
        - [subject](../researcher-guide/stats/datasets.md)
    - [lesson](../researcher-guide/stats/lesson.md)
        - [chapter](../researcher-guide/stats/chapter.md)
            - [confusion](../researcher-guide/stats/confusion.md)
            
- [tags]](../researcher-guide/stats/tags.md)
    - [decision](../researcher-guide/stats/decision.md)
    - [words](../researcher-guide/letters.md)

- [syllabs](../researcher-guide/letters.md)
- [counting](../researcher-guide/numbers.md)
- [association](../researcher-guide/numbers.md)
- [identification](../researcher-guide/numbers.md)


### Activity

Activity function regroups the scripts, function, and tables that define a gameplay sequence and a timespent for one student. They are built one after the other as they need to.  

|File name | Function               | Tables                                    | Method              |
|----------|------------------------|-------------------------------------------|---------------------|
|day.py    | create_student_nb_gapfill_gp_day    | student_dataset_day          | agg pipeline group by (day, student, dataset) |
|day.py    | create_student_assessments_day      | student_dataset_day          | python cumul + agg pipeline|
|dataset.py| create_student_dataset | student_dataset                           | agg pipeline group|
|subject.py| create_student_subject | student_subject                           | agg pipeline group|

Detailled explaination on methods used can be found  in each function docstring
with SQL equivalent


### Progression

Progression function regroups the scripts, functions and tables that define the pedagogical path and progression made by the students expressed in lesson and chapters. It requires the table student_dataset_day to have the information on gameplay sequences
They are built one after the other as they need to.

|File name     | Function               | Tables               | Methods                            |
|--------------|------------------------|----------------------|------------------------------------|
|lesson.py     | insert_student_gp_lesson  | student_dataset_lesson    |insert_one and python cumulative function groupby|
|lesson.py     | insert_student_nb_lesson  | student_dataset_lesson    | insert_one with python cumulative function groupby|
|lesson.py     | create_lessons          | lessons           | agg pipeline from student_dataset_lesson|
|lesson.py     | update_student_lesson  | student_lesson |update_one INTO student_dataset_lesson FROM lessons|
|lesson.py     | create_student_lessons| student_lessons | agg pipeline FROM student_lesson group by (student,dataset)|
|chapter.py    | create_student_chapter | student_chapter |agg pipeline FROM table student_lesson group by (chapter,student,and dataset)|
|chapter.py    | create_student_chapters| student_chapters |agg pipeline FROM table student_chapter group by (student,dataset)| 
|chapter.py    | update_student_chapters| student_chapters |update_one with python cumulative function|

Detailled explaination on methods used can be found  in each function docstring
with SQL equivalent when possible

### Skills

Skills regroups the specific scripts depending of the subject
Tag table is required for building words, the others are independent.
In API we deliberately separate skills into subjects numbers and letters

|File name     | Function               | Tables                                    |Methods     |
|--------------|------------------------|-------------------------------------------|------------|
| tag.py          | create_tag         | tags                                      | agg pipeline|
| tag.py          | create_student_tag | student_tags                              |agg pipeline|
| word.py         | create_student_words| student_words                             |agg pipeline|
| word.py         | create_words        |   words                                   | agg pipeline|
| syllabs.py      | create_student_syllabs | student_syllabs                        | agg pipeline|
| digits.py        | create_student_counting_table  | student_counting              | agg pipeline|
|digits.py        | create_student_association_table  |student_association          | agg pipeline|
|digits.py        | create_student_identification_table  |student_identification    |agg pipeline|

Detailled explaination on methods used can be found  in each function docstring
with SQL equivalent  

### Tasks

Tasks corresponds to 2 specific view asked for visualisation: decision and confusion.


### Confusion

student_confusion requires student_chapter tables
confusion table requires student_confusion table

|File name     | Function                        | Tables           | Methods              |
|--------------|---------------------------------|------------------|----------------------|
|confusion     | fill_student_confusion          | student confusion|python itertools.product + insert_many |
|confusion     | insert_student_confusion        | student confusion|agg pipeline merge    |
|confusion     | create_student_confusion_matrix | student_confusion_matrix|agg pipeline zip|
|confusion     | create_confusion                | confusion| agg pipeline group |
|confusion     | create_confusion_matrix         |  confusion_matrix| agg pipeline zip |


### Decision

student_decision proceeds from records and have two different process: one for numbers one for letters

|File name     | Function                                 | Tables          | Methods               |
|--------------|------------------------------------------|-----------------|-----------------------|
|decision      | create_lexical_decision                 | student_decision | python median + agg pipeline|
|decision      | create_digital_decision                 | student_decision| python median + agg pipeline|
