## Files

Files directory consists of 4 folders `references`,`raw`, `archived` and `clean`.

- `references` stores the configuration informations given by the admin : transformed from original XLS files to csv files.

- `raw` stores files ( students logs produced by the game) acquired at the download step. 

- `clean` stores files ( students logs produced by the game) cleaned at the clean step and ready for insertion.

- `archived` stores the old raw files and dumps of database before rebuilding it.

Each folder corresponds to the differents steps in processing the files till the insertion in the database:

* `init()` <= references

* `archive()` => archived

* `download()` => raw

* `clean()` => clean

### References

The directory `references` stores 8 mandatory setting files 

defined and edited by the admin:

- studentid_group.csv
- nb_progression_tag.csv
- gp_progression_tag.csv
- numbers_games_lessons.csv
- letters_games_lessons.csv
- stimuli_wordsorting.csv
- Letters_3game_perLesson.csv
- Numbers_3game_perLesson.csv

They have been declared in settings/files.py as REFERENCE_DIRS

```
REFERENCES_FILES = {
    "gapfill_lang":[join(REFERENCES_DIR, "stimuli_wordsorting.csv")],
    "gp": [join(REFERENCES_DIR,"gp_progression_tag.csv"), join(REFERENCES_DIR,"letters_games_lesson.csv"), join(REFERENCES_DIR,"Letters_3game_perLesson.csv")],
    "numbers": [join(REFERENCES_DIR,"nb_progression_tag.csv"), join(REFERENCES_DIR,"numbers_games_lesson.csv"),join(REFERENCES_DIR,"Numbers_3game_perLesson.csv")],
    "students": [join(REFERENCES_DIR,"studentid_group.csv")],
}
```

> As required, if one is missing run.py init step will abort   

Theses references files are used at `init()` step to build: 
- table `path` to define chapter and lesson delimitations
- table `student` to define student and classroom available
- table `records` adding contextual informations to each record  


### Raw

The directory `raw` stores  all the student files found in the [document server](#download) matching a special type/name of file that we called `dataset` internally. 

In the document server we can find multiple documents with:
1. different extensions:
- `.old` is the archive
- `.save` is the next archive candidate
- `.json` is the current dataset

2. a same naming convention 
`Class _<nb_class[range(1:60)]>_<Tablet_nb([range:1-8])>_<Kid_nb([range: 1-8])>___<filename>.<extension>`

3. We only download in raw the files that match the following filenames:

- `assessement_language`: student logs of each chapter of the game on subject langage
- `assessement_maths`: student logs of each chapter of the game on subject numbers
- `gp`: student logs of reading games
- `numbers`:  student logs of maths games
- `gapfill_lang`: student logs of words games

This matching filenames are defined in the table `datasets` at the `init()` step
and declared in settings

```
DATASETS = ["gapfill_lang", "assessments_language", "assessements_math", "gp", "numbers"]
```

### Clean

Clean files consists simply of a copy of raw files with check and sanitization of raw_files this folder is created at `clean()` step. This folder is used to insert records into table


### Archived

Archived folder simply consists of a copy of clean folder when new download is proceding.
And a dump of the previous database. Activated by default.

Archive action is an option of the `init()` step