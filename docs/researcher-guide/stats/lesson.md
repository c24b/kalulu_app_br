## LESSON

File : `stats/lesson.py`

### Student_lesson
Using `student_day table` 
Compute records by student, dataset and day to get : 
by student
- the lesson 
- the timespent by lesson
- the score
and store it into student_lesson

student_lesson table is required to define
- `progression`:
    - `student_lesson`: at student and dataset level
    - `lessons`: globally by dataset 
    - `chapter`: at student and dataset level
    
Lesson records are cumulated over days till next lesson appears: 
- initialize the first lesson
- compare to previous lesson
    - if previous has the same tag:
        add records to existing records
        add timespent to existing timespent
        add sequences
        add scores
    - else:
        create a new lesson


`lessons table` 

### Lesson

From `student_lesson` table 
groups lesson to get the score for each student, 
compute: 
- the average correct_answer score `avg_%CA`
- the average timespent `avg_timespent`
- the average nb_records `avg_nb_records`
- the standard deviation of correct_answer score `std_%CA`
- the standard deviation of timespent score `std_timespent`

insert into `lessons` table

Student_lesson is then updated by comparing lesson average score with student_average score adding a color code name `score_color` following this rules:

``` python
avg_ca100 = record["avg_%CA"]
std_ca100 = record["std_%CA"]
avg_ts = record["avg_timespent"]
std_ts = record["std_timespent"]
if student_record["%CA"] < (avg_ca100 - (2 * std_ca100)):
    score_color = "red"
elif student_record["%CA"] >= (avg_ca100 - std_ca100):
    score_color = "green"
else:
    # elif student_record["%CA"] <= (avg_ca100 - std_ca100):
    score_color = "orange"
```