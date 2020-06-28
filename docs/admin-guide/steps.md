## Steps

Steps is a python package made of scripts from acquisition of the files till insertion in the database

They are 4 main steps: 

- [download](###Download)
- [clean](###Clean)
- [init](###Init)
- [insert](###Insert)

### Download

This steps consists of:

- setting up credential using _settings.py references
- connecting to source document server throught ssh
- copying all the files that matchs the [datasets list](##Raw) inside `files/raw` 


### Clean

This steps consists of:

- taking all files from `files/raw`
- opening and cleaning each files
- log errors inside table `files`
- stores into `files/clean`


### Init

This steps consists of:

- dumping the previous database (archive in the archived folder and delete the files in current folder)
- creating the reference tables: `path` and `datasets` from references files provided
- creating the `students` table: first from list of files and adding therefore group information for the student and finally checking if declared students have no files
- creating the `files` tables to declare any problems in the files: incorrect file format, group missing, etc..

### Insert

This steps consists of :

- creating the `records` table by inserting from the `files/clean` directory
- creating the games table by querying the record table and matching with games references
- store complete logs of the inserting process (errors, infos, debug, warning) inside `admin/logs/insert.log` 
