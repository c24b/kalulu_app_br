# INSTALL

Full procedure to install the application into a server:

- [Get the sources](##Get)
- [Configure](##Configure)
- [Install](##Install)
- [Run](##Run)

> Special note on activating HTTPS 

- [Uninstall](uninstall.md)

## Get the sources

Download the project into the server: 

* ZIP link:

[https://lab.driss.org/kalulu_team/kalulu/-/archive/master/kalulu-master.zip](https://lab.driss.org/kalulu_team/kalulu/-/archive/master/kalulu-master.zip):

```
curl https://lab.driss.org/kalulu_team/kalulu/-/archive/master/kalulu-master.zip --output kalulu-master.zip
unzip kalulu-master.zip
```

* Git : 
        
    - SSH: `git@lab.driss.org:kalulu_team/kalulu.git` 
        
    - HTTPS: `https://lab.driss.org/kalulu_team/kalulu.git`

```
git clone https://lab.driss.org/kalulu_team/kalulu.git
```

## Configure

* Go into the directory and 
* Edit the [settings file](../../settings.json) in `settings.json` replacing by your parameters.


This configuration file simply consists of 
declaring the direction and server_name for the 3 main web services:

- api
- front 
- doc

Optionnaly you can change the database name, declare the server were to download the raw files, etc..
Consult [configurations options](configuration-options.md) to get the full details.

## Install

Execute `./install.sh`.

Setup will install the system dependencies, python package and deploy the vue application following the parameters defines in settings.json

Once your done and you want to secure application run
`sudo certbot`
to add certificates to the wanted domains
if you want the change be effective restart services using `deploy.sh`

## Run

Populate the database for the first time by running `run.sh`

that run db/run.py script  in the virtual environnement and in background


```
$ source .venv/bin activate
(venv) $ python db/run.py &
```

consult [contribution guide](../contribution-guide/db.md) to get more options on initializing the database

<small>
> You have also a secret way to rebuild the database using API endpoint by PUTting admin/files with the correct PASSWORD  (corresponds SUDO_TOKEN declared in the settings.json files ;) )

If this make sense to you, use your power with great sense of responsability
</small>

## Test and Enjoy

Test the availablility of the 3 main services by consulting the differents domains (adapt to your own domain name):

- Consult the API page at [http://research.ludoeducation.fr](http://research.ludoeducation.fr)
- Consult the FRONT page [http://tdb.ludoeducation.fr](http://tdb.ludoeducation.fr)
- Read the documentation [http://doc.ludoeducation.fr](http://doc.ludoceducation.fr)



### ACTIVATE HTTPS

This procedure does no longer supports ssl and https at the installation steps.

- create/renew the certificates (they will updated the existing nginx configuration of your domain)
`sudo certbot`

- (optionnal) You can execute `.deploy.sh`

This is a facility to rebuild the front app (npm) and restart the services (redis, nginx, supervisor)
but generally restarting nginx does the trick `sudo nginx -s reload`

> HTTPS is mandatory for FRONT application

### Uninstall

[See procedure to remove application](uninstall.md)
