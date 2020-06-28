# INSTALL

## Package overview

* python package:
    * db/
    * api/
* vue.js package:
    * front/
* conf/
    * settings.json
    * templates/
* settings/


## System requirements

Debian stretch based distribution

Minimal requirements: 8GBof RAM 4 cores 

> Core numbers and CPU capabilities will impact drastically 
> the time of processing data (insert records and build stats tables)

## Install procedure

### Download the project

* zip version https://lab.driss.org/kalulu_team/kalulu/-/archive/master/kalulu-master.zip


### Edit the settings file

In the project edit `conf/settings.json` replacing by you parameters.

This configuration file has multiple sections
- Environnement
- SSL
- FILE_SERVER
- SOURCES_SERVER
- API
- FRONT
- DB

##### Environnement

Define the generic information on the context of execution of the project

`user` declare the user that is in charge of the application setup and deploy. 
He must be sudoer as he will be in charge of install and execute the processes(gunicorn, celery, nginx & supervisor)

`ENV` declare the context of the application execution set by default to `default` if set to `test` will launch the tests after installation, if `local` will try to find conf/local_settings.json to install.

##### SSL

Declare the location of your certificates to update NGINX configuration and activate HTTPS

If activate is set to False: web applications (API and front) will fall back to `http://`.

##### FILES SERVER

Declares the location of the server where to download the files sent by the Game application. 

Usefull when --download option is provided to the main shell script (back/run.py)

Theses parameters are used to execute a shell command `scp` using SSH credentials (set up of credential not implemented YET)  executed when populating the database at first step (download)

##### SOURCES SERVER

Declares the location where sources of this application are stored. Basically consisting in a git repository. 

##### API

Declares the parameters for launching and exposing the API. 
Parameters are used in flask, celery, nginx, gunicorn and supervisor

Set up the token and sudo_token to allow specific user to update content of the database.

##### FRONT

Declares the parameters for exposing the front app. 
Used in NGINX.

- hostname declares the srvname for nginx
- name declares the name of the log file in nginx and supervisor
- root_dir declares the location of the front app directory
- host and port are used in gunicorn as bind address (address to listen to)
- user declares which user will launch the supervisor process

- allowed_IPS add a directive to headers in nginx to allow Cross Origin: can be set to `*` as low security standard or better to the API hostname 
  
##### DB

Declare the database name and allows connection to database.


## Setup detailled procedure  

The script `./setup.sh` 

- install the system dependencies :
    - [python3]()
    - [pip]()
    - [virtualenv]()
    - [mongo-db]()
    - [redis]()
    - [redis-server]()
    - [node]()
    - [npm]()
    - [nginx]()
    - [supervisor]()

- install back and api [python private package]() inside a virtualenv
- install front using [node]() and [npm]() and build front dist
- launch the initialization of the database in background (using main shell script `back/run.py`) from previous stored files (shipped install `files` directory) using database parameters set `conf/settings.json`
- injecting into template files (stored in `conf/templates`) the parameters declared in `conf/settings.json` parameters copying into conf/ for debug purpose and sending it to the required directory (nginx => /etc/nginx/sites-enables/ supervisor /etc/supervisor/supervisor.d/). Template building procedure managed by `utils/install.py`

### TO DO:

- copy /etc/nginx/ templates files to sites-available first
- check nosssl templates
 