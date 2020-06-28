# Tasks

Files: `API/namespaces/tasks.py`, `API/csv_blueprint/tasks.py` 


Tasks category endpoint exposes two specific tasks in the game for a [student](stats/students.md)  on a [dataset](stats/datasets.md) or a [subject](stats/datasets.md) based on his [records](stats/records.md) and the [pedagogical progression path](stats/path.md). This two tasks requires specific analysis

Two main tasks are available:

- confusion
- decision


## Confusion

Confusion consists of analysing target and stimulus matching in records for a student on dataset gp for the subject letters and dataset numbers for the subject numbers in order to produce a confusion matrix. 

It relies on 2 tables:

- student_confusion 
- student_confusion_matrix

See how confusion is calculated consult [confusion documentation](stats/confusion.md)

## Decision

Decision consists of analysing the performance of assessments games:

- for letters it consists of showing median timereaction to choose between a word and a pseudoword 
- for numbers it consists of  showing median timereaction to choose the highest number

See how confusion is calculated consult [decision documentation](stats/decision.md)
