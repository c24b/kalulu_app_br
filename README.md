# Kalulu

## About Kalulu

Kalulu is a game developped by the research lab Unicog/Neurospin (Unité INSERM-CEA de Neuroimagerie Cognitive) dedicated to the learning throught game to numbers and letters.

http://www.ludoeducation.fr

The aim of this project is to give access throught a dashboard to the data collected by the game for teachers and researchers.

## About this repository

Kalulu app consists of 4 main functionnal **modules**

- [files](files.md)
- [db](db.md)
- [api](api.md)
- [front](front.md)


## OVERVIEW

![](./overview.png)

## INSTALL

Kalulu app can be installed in a server throught a shell script `setup.sh`

> See [installation documentation](install.md)

## CONFIGURE

Declare your settings in settings.json file stored in `conf`

> See [settings documentation](settings.md)



## Files

Stores the  references files and the raw files to populate the database
```
├── archived
├── clean
├── dump
├── raw
└── references
```

## DB

DB consists of a python package with all the python scripts to init, populate and update records of the database (MongoDB): 

```
├── __init__.py
├── run.py
├── stats
│   ├── chapter.py
│   ├── classroom.py
│   ├── confusion.py
│   ├── dataset.py
│   ├── day.py
│   ├── decision.py
│   ├── digits.py
│   ├── words.py
│   ├── lesson.py
│   ├── tag.py
│   ├── student.py
│   ├── subject.py
│   ├── syllabs.py
│   ├── main.py
│   └── __init__.py
└── steps
    ├── clean.py
    ├── download.py
    ├── init.py
    ├── insert.py
    ├── main.py
    └── __init__.py
    
```

- `run.py` shell script to administrate the database in command line argumenst 
- `steps` module for data acquisition from raw to database 
- `stats` module for data analysis creating the statistical tables exposed in API and served in front


## API

The interface API to consult and modify the database
in  Flask with Celery and Swagger

```
.
├── API.py
├── celery_tasks
│   ├── app_task.py
│   ├── __init__.py
│   └── __pycache__
├── celery_workers.py
├── csv_blueprints
│   ├── activity.py
│   ├── admin.py
│   ├── index.py
│   ├── __init__.py
│   ├── progression.py
│   ├── skills.py
│   └── tasks.py
├── factory.py
├── namespaces
│   ├── activity.py
│   ├── admin.py
│   ├── classrooms.py
│   ├── __init__.py
│   ├── progression.py
│   ├── skills.py
│   ├── status.py
│   ├── students.py
│   └── tasks.py
└── __init__.py

```

API is the main access point to the API that consists in 2 main submodules:
- namespaces : JSON access and Swagger Interface
- csv_bvlueprint: CSV facilities with Flask

API website is exposed throught NGINX configuration file, using gunicorn and supervisord for handling process (API + celery).



## FRONT

The website for teacher and researcher in VUE.js

```
├── build.js
├── node_modules
├── dist
├── package.json
├── src
│   ├── App.vue
│   ├── assets
│   ├── components
│   |    ├──    
│   ├── main.js
│   ├── routes.js
│   └── services.js
├── vue.config.js
└── webpack.config.js
```

FRONT website is exposed via NGINX
