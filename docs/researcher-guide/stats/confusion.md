
File: `db/stats/confusion.py`

In the game, the student is proposed to choose the correct value between 3 values shown on the screen.
Each  proposal take the form of a record with the corresponding values:
```
{ target:"a", value:"a", score:1}
{ target:"a", value:"o", score:0}
{ target:"a", value:"i", score:0}
```

Confusion aims to present the couple of target/value that are most confusing by grouping the couple target/value compute the total score, the % of correct answers, and dedecue the confusion rate that corresponds to % of wrong answer.
This create a confusion rate that is delimited by: 
- 1 totally confusing 
- 0 correct identification/no confusion   


### Fill student_confusion

Generate all the possibilities for a couple target/stimulus add default values into a table `student_confusion`
for each chapter

such as in sample and test
```python
tags = ["a", "b", "c"]
chapters = [1, 2, 3]
#generate tags combination for tags using cartesian product
>>> couples = itertools.product(tags, repeat=2)
>>> print(couples)
>>> [
    ("a", "a"), ("a", "b"), ("a", "c"), 
    ("b", "a"), ("b", "b"), ("b", "c"),
    ("c", "a"), ("c", "b"), ("c", "c")
]
# repeat the couples for each chapter
chapter_couples = [(chapter,couple) for couple in couples for chapter in chapters]
print(chapter_couples) 
>>> [
    (1, ("a", "a")), (1,("a", "b")), (1,("a", "c")), 
    (1,("b", "a")), (1,("b", "b")), (1,("b", "c")),
    (1,("c", "a")), (1,("c", "b")), (1,("c", "c")),
    (2, ("a", "a")), (2,("a", "b")), (2,("a", "c")), 
    (2,("b", "a")), (2,("b", "b")), (2,("b", "c")),
    (2,("c", "a")), (2,("c", "b")), (2,("c", "c")),
    (3, ("a", "a")), (3,("a", "b")), (3,("a", "c")), 
    (3,("b", "a")), (3,("b", "b")), (3,("b", "c")),
    (3,("c", "a")), (3,("c", "b")), (3,("c", "c"))
]
# insert into student_table using insert_bulk
```
fill student_confusion with tags that have been seen by the student
and following separation for letters between `C` and `V`

```python 
#get the chapters and tags by subject for one student 
subject_items = []
for subject_dataset in [("letters","gp"),("numbers","numbers")]:
    subject, dataset = subject_dataset
    # how many chapters?
    chapters = db.student_chapters.find_one({"student":student, "subject": subject})
    if chapters is None:
        continue
    else:
        chapters = chapters["chapter_ids"]
        # how many tags? 
        tags = db.student_tag.distinct("tag", {"student": student, "dataset":dataset})
        # print(chapters, tags)
        if len(tags) != 0:
            # print(tags, chapters)
            if subject == "letters":
                C_tags = [tag for tag in tags if get_CV(tag) == "C" ]
                V_tags = [tag for tag in tags if get_CV(tag) == "V" ]
                # print(C_tags, V_tags)
                if len(V_tags) != 0 and len(C_tags) == 0:
                    couples = [
                        ("V", list(itertools.product(V_tags, repeat=2)))
                    ]
                elif len(C_tags) != 0 and len(V_tags) == 0:
                    couples = [
                        ("C", list(itertools.product(V_tags, repeat=2)))
                    ]
                else:
                    couples = [
                        ("V", list(itertools.product(V_tags, repeat=2))), 
                        ("C", list(itertools.product(C_tags, repeat=2)))
                    ]
            else:		
                if len(tags) > 0:
                    couples = [
                        ("N", list(itertools.product(tags, repeat=2)))
                    ]
        for block in couples:
            CV, combos = block
            db.student_confusion.insert_many([
                build_item(student, chapter, subject, couple, CV) 
                    for chapter in chapters for couple in combos
            ])	
```

### Insert records to student_confusion

FROM student_chapter
INSERT into student_confusion TABLE
where all the possibilities previously generated manually
UNWIND all records 
IF stimulus is not None
WHEN document.target matches the  target, stimulus, student, chapter, subject, CV
UDPATE arrays (push) score, elapsedTime 
SUM nb_records, score (to CA)
UDPATE set lesson to lessons set (unique)
CALCULATE WA (SUM(nb_records) - CA)

as chapter is cumulated in student_chapters confusion respect the progression of the game by cumulating the records and thought the confusion rate for 

### Format confusion

Create the matrix needed for the heatmap
	where matrix will be: 
	
[y, [(x, WA), (x, WA), (x, WA)]]
[y, [(x, WA), (x, WA), (x, WA)]]
[y, [(x, WA), (x, WA), (x, WA)]]

such as:

[target, [(stimulus, WA), (stimulus, WA), (stimulus, WA)]]
[target, [(stimulus, WA), (stimulus, WA), (stimulus, WA)]]
[target, [(stimulus, CA), (stimulus, WA), (stimulus, WA)]]

FROM student_confusion
GROUP by student, dataset, classroom, CV, stimulus,
SET targets  as [target, target, target, ...]
SET WA_rate  as [WA, WA, WA, ...]
ZIP (target, WA_rate) into `arrays` such as 
    [(target, WA), (target, WA),(target, WA),(target, WA),...] 
GROUP by student, dataset, classroom, CV
SET stimuli as [stimulus, stimulus, stimulus, ...]
ZIP (stimuli, arrays) into `matrix` such as 
[
    [stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]],
    [stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]]
    [stimulus, [(target, WA), (target, WA),(target, WA),(target, WA),...]]
]

