# DB

`db` directory groups all the steps to populate database from files, compute stats by building tables. 

To launch the full process in command line use [`run.py`](Run).
 
db consists of in 2 main folders:


- [steps](steps.md##Steps) is a groups all the steps from initialization of the database to insertion in the main tables `records`. See [steps page](steps.md) to have a detailled description and [steps section](Steps) to have the overview.
If you want to download the files from a remote server: take a look at the previous instructions inside [download section]Download) 


- [stats](stats.md##Stats) groups all the scripts to create the tables storing the metrics needed. See [stats page](stats.md) to have a complete description



## Run

`run.py` is a shell script managing all the process related to database . It is the main entrypoint to launch the full process which have been separated in 2 main sub-processes: 
- steps (data-acquisition): archive, download, clean, insert
- stats (data-analysis): 

```bash
cd kalulu/
source .venv/bin/activate 
python db/run.py
```

Many additionnal options are available.  

```
python db/run.py -h
### RUN
usage: run.py [-h] [--debug] [--from] [--to] [--old] [--ref]
              [--download DOWNLOAD] [--skip SKIP] [--step STEP]
              [--stats STATS]

optional arguments:
  -h, --help           show this help message and exit
  --debug              Debug information
  --from               Declare the source directory of the files 
  --to                 Declare the destination directory of the files
  --old                Declare the directory for archiving the files
  --ref                Declare the directory of your references files
  --download DOWNLOAD  Download the documents inside the source directory
  --skip SKIP          Skip specified steps using ',' delimiter such as:
                       download,clean,init,insert,stats
  --steps              Execute all the steps: clean, init,insert 
                       (set --download option if need to download)
  --step STEP          Execute only the step mentionned among theses
                       options: download init insert 
  --stat               Regenerate the stat category specified: activity,
                       progression, tasks, letters, digits
  --stats STATS        Regenerate the stat category using ',' delimiter among:
                       activity, progression, tasks, skills, numbers, digits
  --table TABLE        Regenerate the specified table among:
                       day,dataset,subject,lesson,chapter,confusion,decision,digits,tags,words,syllabs
  --student  STUDENT   specify the student
```
##### Command line examples

* execute the full process:
```
# activate the  virtualenv
user@srv:/home/user/kalulu/ source ./venv/bin/activate
# lauch run.py
(.venv) user@srv:/home/user/kalulu/ python db/run.py
```

* relaunch init, clean, insert from files
```
(.venv) user@srv:/home/user/kalulu/ python db/run.py --steps
```

* relaunch download, init, clean, insert from files
```
(.venv) user@srv:/home/user/kalulu/ python db/run.py --steps --download
```

* relaunch stats creation
```
(.venv) user@srv:/home/user/kalulu/ python db/run.py --stats
```

## Steps

> For more information please consult the [Steps dedicated page](steps.md) 

Steps consists of a collection of isolated actions. These actions corresponds to scripts that have to be executed in a specific order as they represents a step for acquiring the data:
- handling the **files** in their different states: 
  - `archive.py` move content of raw/ into old/ and dump database into dump
  - `download.y` put content into /raw
  - `clean.py` clean content from /raw to clean/

- **initialize** the database: `init.py`
  - declare the datasets accepted
  - declare the students group
  - insert the references files from /references/ 

- parse and **insert** the documents inside the database: `insert.py`     
  Each [dataset] type has its own function for inserting into the master table `records`

---
##### Archive

See [Steps dedicated page](steps.md)

##### Download

A special note on downloading option

If you want to download the files from a remote server:

###### Set up the credentials

In order to allow the current server to copy the files from remote server:

- create the ssh_keys inside the current server

```
ssh-keygen -t rsa 

```

- add your srv public key to remote server
```
ssh-copy-id remote_login@remote_hostname
```

After entering the password, credentials will be set up 
and script will be able to download the file from the server 
if you declare it inside the `conf/settings.json` file

###### Declare the remote files server:

Inside global settings configuration file `conf/settings.json` edit the FILES_SERVER section declaring the host (FQDN or IP) 
the login user and the complete path to location of the files 
```
"FILES_SERVER":
        {
            "name": "files_srv",
            "host":"",
            "hostname":"files.example.org",
            "login":"user_login",
            "dir":"/kalulu_data"
        },
```

###### run with download option activated 

Now you declared all the informations needed to download the files
launch run script from shell using the `--download` option

```bash
cd kalulu/
source .venv/bin/activate 
python db/run.py --download
```


This will rebuild the database from 0 archiving the previous files into `files/old/` and the database into `files/dumps`

##### Clean

See [Steps dedicated page](steps.md)

##### Insert

See [Steps dedicated page](steps.md)

## Stats

> For more information please consult the [Stats dedicated page](stats.md) 

Stats consists of a collection of scripts organized in sections that from the master `records` table  build the tables needed for the graphs and the analysis: they are exposed in the API 



