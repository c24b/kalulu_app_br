Files: `API/namespaces/skills.py` `API/csv_blueprints/skills.py`
# Numbers

Numbers provides information data on specific tasks for letters that mobilize differents competencies:

- association
- counting
- identification

File: `db/stats/digits.py`

## student_association

```sql
FROM records 
WHERE dataset='numbers' and game matchs [crabs, jellyfish, ants]
GROUP BY student, subject, subject
FILTER timespent != -1
CREATE timespents [timespent, timespent, ...]
```

## student_counting

```
FROM records 
WHERE dataset='numbers' and game matchs [caterpillar, monkey, turtle]
GROUP BY student, subject, subject
FILTER timespent != -1
CREATE timespents [timespent, timespent, ...]
CREATE games unique[game, game, ...] 
CREATE tags unique [tag, tag, ...]
SUM score, nb_records
CALCULATE %CA, color(%CA)
OUT student_counting
```

## student_identification
```
FROM records 
WHERE dataset='numbers' and game matchs [crabs, jellyfish, ants]
GROUP BY student, subject, subject
FILTER timespent != -1
CREATE timespents [timespent, timespent, ...]

CREATE games unique[game, game, ...] 
CREATE tags unique [tag, tag, ...]
SUM score, nb_records
CALCULATE %CA, color(%CA)
OUT student_identification
```