
# Kalulu_app documentation

## Introduction

Kalulu app consists of a dashboard for teacher, researcher and administrators to consult, edit and manage the data produced for the educational game `Kalulu`. 


This project consists of 3 main website applications:

- a [dashboard](user-guide/getting-started.md) for teacher

- a [dashboard](researcher-guide/getting-started.md) for researcher to mine and control the data

- a [documentation](contribution-guide/index.md) on methods and parameters  

## Install


- clone this [repository](https://lab.driss.org/kalulu_team/kalulu_app)

- update the [settings](../../settings.json) with your own [parameters](./admin-guide/configuration-options.md)

- run the script [install.sh](./admin-guide/install.md) with sudo privileges

- launch [run.sh](./contribution-guide/db.md) script 

###### Activate HTTPS (Optionnal)

- run `certbot`
- select domain names you want a new certificate for
- reload nginx `sudo nginx -s reload` 

## Test and enjoy!

Test the availablility of the 3 services (adapt to your domain names):

- Consult the FRONT page [http://tdb.ludoeducation.fr](http://tdb.ludoeducation.fr)

- Consult the API page at [http://research.ludoeducation.fr](http://research.ludoeducation.fr)

- Read the documentation [http://doc.ludoeducation.fr](http://doc.ludoeducation.fr)


#### More tests

- check dashboard website functionnalities: 
    
    > follow the [dashboard tutorial](/user-guide/)

- check api website: 

    > follow the [api tutorial](./research-guide/)

- check doc website: 

    > check the [documentation website](http://doc.ludoeducation.fr)


## More informations

* [About this software](about.md)
* [Dashboard tutorial](./user-guide/)
* [API Tutorial](./researcher-guide/)
* [Admin doc](./admin-guide/)
* [Developper doc](./contribution-guide/)
