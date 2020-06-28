# Letters

Files: `API/namespaces/skills.py` `API/csv_blueprints/skills.py`

Letters provides information data on specific tasks for letters that manipulate:

- tags
- words
- syllabs

## Tags

File: `db/stats/tag.py`
Tag table is not displayed as it is but usefull to determine words/pseudowords globally
given in references files and stored in table [`path`](stats/path.md)

```
FROM records
	create table student_tag from records
	that group unique tag by student along with the full records for this tag
	OUT student_tag
```
## Words

File: `db/stats/word.py`

#### student_words
```
FROM student_tag 
    filter out dataset (gapfill_lang and assessments_language)
    filter out tag that has type="word" in db.path table
    filter out only words that have been clicked and have then an elapsedTime set (not -1)
    insert the scores into student_words table
    add color for each word (0.25 red, 0.50 orange, 0.75 green) 
OUT student_words
```

#### words
```
FROM student_words
group words, along with their nb_letters
sum nb_records
calculate AVG(median_time_reaction, %CA, nb_records
insert unique [student, student, ...] 
insert unique [classroom, classroom, ...]       
OUT words
```

## Syllabs

File: `db/stats/syllabs.py`

#### student_syllabs
```
FROM records
SELECT records WHERE dataset='gp' AND WHERE '.' in record[target] or '.' in record[stimulus] AND WHERE group != "guest" 
GROUP BY classroom, student, target
SUM nb_records, CA
ADD [stimulus, stimulus,...]
CALCULATE %CA, color(%CA), word
OUT student_syllabs
```