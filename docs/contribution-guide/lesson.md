## LESSON

File : `stats/lesson.py`

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

Scripts creates the table by simply grouping student_lesson on dataset and lesson
computing simple statistics
