# SETTINGS

The file settings.json define all the user parameters needed to configure the full system
from install to deployement:

- Environnement
- FILE_SERVER
- SOURCES_SERVER
- API
- FRONT
- DOC
- DB

[`settings.json`](../../../settings.json)

##### Environnement

Define the generic information on the execution context of the project

`user` declare the user that is in charge of the application setup and deploy. 
He must be sudoer as he will be in charge of install and execute the processes(gunicorn, celery, nginx & supervisor)

`ENV` declare the context of the application execution set by default to `default` if set to `test` will launch the tests after installation, if `local` will try to find settings.json to install.


##### FILES SERVER

If `activate` is set to false:  script db/run.py will use **relative** path `dir` (default is files/raw) to proceed to next steps( clean, init, insert, stats).

If `activate` is set to true: script db/run.py will perform a download using `login` `host` to securely copy files from remote **absolute** `dir` location  to files/raw and then proceed to newt steps (clean, init, insert, stats).

> For this option, you must **set the credentials first** 

##### SOURCES SERVER

Declares the location where source code of this application are stored. Basically consisting in a git repository. 

##### API

Declares the parameters for launching and exposing the API. 
Parameters are used in flask, celery, nginx, gunicorn and supervisor

Set up the token and sudo_token to allow specific user to update content of the database.

> The setup procedure will take the parameters of API, write from an api.conf template conf/nginx-api.conf 
and place it into /etc/nginx/sites-enabled/api.conf 


##### FRONT

Declares the parameters for exposing the front app. 
Used in NGINX.

- hostname declares the srvname for nginx
- name declares the name of the log file in nginx and supervisor
- root_dir declares the location of the front app directory
- host and port are used in gunicorn as bind address (address to listen to)
- user declares which user will launch the supervisor process

- allowed_IPS add a directive to headers in nginx to allow Cross Origin: can be set to `*` as low security standard or better to the API hostname 

> The setup procedure will take the parameters of FRONT, write main.js from template front-main.js and place it into front/src/main.js befor build
and write from a front.conf template conf/nginx-front.conf and place it into /etc/nginx/sites-enabled/front.conf


##### DOC

Declare the parameters for erxposing the documentation site.

##### DB

Declare the database name and allows connection to database.

If additionnal parameters are setup: such as data_directory and memStorage this will write a mongod.conf into /etc/mongod.conf
storage.wiredTiger.engineConfig.cacheSizeGB

storage.journal.enabled False

mongod --config /etc/mongod.conf

```
storage:
   dbPath: /var/lib/mongodb
   engine: wiredTiger
   wiredTiger:
      engineConfig:
         cacheSizeGB: 2
         maxCacheOverflowFileSizeGB: 1
```

