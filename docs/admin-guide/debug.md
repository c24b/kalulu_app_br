# DEBUG

Something went wrong? Unexpected behaviour?

## FAQ

- Page is showing nothing
    - API is not running 
        > see Api
    - Database is empty 
        > see db
    - Front has a compile error
        > see front

- Graph dashboard are shown as loading but never displayed:
    - API is not running 
        > see Api
    - Database is empty 
        > see db

- Data is outdated:

Relauch the full process for new data with db/run.py --download 

> See db

- Some classroom/student are missing:

Relaunch the stats with db/run.py --stats=create 

- Page displays 'Oups... Table xxx is empty' 

Relaunch the stats with db/run.py --stats=create

> See db

- API is not displaying anything

> See API

Determine which module thraw the error between:
- database
- db
- api 
- tests
- front


## DATABASE

- Is the database working? Can I connect to the database?
    
```
$ mongo kalulu
```

- Is the mongo process working?

`$sudo service mongod status`


To repair the database

```
rm -rf /var/lib/mongod/mongod.lock
mongo repair
sudo service mongod start
sudo service mongod status
```


## DB 

### Run

- Did the `run` process encounter an error?
 
`$tail ./logs/run.log`

#### Init

##### Process

- Did the init process encounter an error?

```$tail logs/run.log | grep 'init'```

##### References    

- Are the reference files all presents?

You must have 8 files

```
$ ls -l files/raw | wc -l 
```

Is something problematic in references files?

```bash
$ mongo kalulu
> db.references.find({status: false})

```

##### Raw files

- Is the raw files directory empty?

```
$ ls -l files/raw | wc -l 
```

- Is something wrong in downloading?

```$tail logs/run.log | grep 'download'```

Remember that you have 3 options to populate database with raw files:
- download from remote server
- copy files into default directory files/raw/
- declare the location of your raw files 


- **download from remote server** 

This requires to set up the credentials for the server as described in [download section of db](db.md#####Download)

Once this is done, you can run all the process by activating the download option in run.py cmd 

`(venv)$ python db/run.py --download`

- **copy files into files/raw and run the process**

`(venv)$ python db/run.py --download`

- **specify the location of the raw documents file while running the process**

`(venv)$ python db/run.py --from=/home/user/kalulu_raw_data/`


### Clean files

- Is the clean files directory empty?

`$ ls -l /files/raw | wc -l `

- Was something wrong in cleaning?
```$tail logs/run.log | grep 'download'```

- Are files not cleaned properly ?

```
$mongo kalulu
> db.files.find({status: false})
``` 

### Inserted files into records

- Was something wrong in inserting into database?
```$tail logs/run.log | grep 'insert'```

- Do the database have records?

```
$ mongo kalulu
> db.records.count()
10132450

``` 


## API 


- Is the API up?

test using xcurl or visit the API interface

- Check process API
```
supervisorctl status all
```


tail /var/log/api.err.log
tail /var/log/celery-api.err.log


## TESTS


Tests are written to ensure that the database is correctly populated 
and the API is answering as designed so it can be a good way to investigate
whether the responsability is held by the db module or the api module

launch the  tests using virtualenv 
inside tests directory

Available tests:
