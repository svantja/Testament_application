# About this application
This application was developed as part of my Bachelorthesis at the HTWG Konstanz.
The usage of the latest Version of the BigchainDB Server ist not yet implemented. The application uses the ``version 1.3.0 kyber-master``. 

---
_**Note:**_

It would make sense to migrate the functions of ``version 1.3.0 kyber-master`` to the latest version in the future. To do so the plugin ``bigchaindb-smart-assets`` needs to be adapted.

To start the latest version of the server (as at 09.08.2018 ``version 2.0.0b3``) a small change in the docker-compose.yml file is necessary. Replace the command ``.ci/entrypoint.sh`` in line 45 with the command inside the entrypoint.sh file ``bigchaindb -l DEBUG start``.

---

## Prequesites
To run this application you need the plugin smart-assets and a specific branch of bigchaindb (kyber-master):
### Smart Assets

#### Installation

##### Clone
Clone or fork the bigchaindb-smart-asset repo

```bash
git clone git@github.com:ascribe/bigchaindb-smart-assets.git
```

and clone the specific branch of bigchaindb `kyber-master` inside the bigchaindb-smart-asset repo:

```bash
cd bigchaindb-smart-assets
```

```bash
git clone git@github.com:bigchaindb/bigchaindb.git
cd bigchaindb
git checkout kyber-master
cd ..
```

#### Start the BigchainDB Server with Docker

> Supports BigchainDB Server v1.0

##### Prequisites

`docker`, `docker-compose` and `make` must be installed.

##### Make or docker-compose

To start the Server using Docker, simply run the `make` command. Inside the Makefile several `docker-compose` commands are wrapped. 

```bash
make
```


### Start the application

Verify with the command:
```bash
docker-compose ps
```
that the Server is running. If it is running you can start the application.

## Usage of the application

The commands, which can be processed by the TUI are:
* `set up`: set up the BigchainDB, create Asset-Types and Admin User *should only be called once!*
* `Login`: Login, requires the name of the User
* `Logout`: Logout, other User can Login
* `create User`: add a new User with a specific role
* `create testament`: create a new desposit information Asset
* `read testament`: search for specific desposit information Asset. Returns location of the testament file
* `file`: *only for test purpose* create files in which the User information and Asset-Group information is stored
* `load old`: *only for test purpose* after restart of the application without restarting BigchainDB. No new setup needed.
* `q`: Stop the application




