# Menu API

API for beantownpub.com food menu
_work in progress_

## Usage

### Requirements

- Docker
- Make

#### Export Env Vars

```shell
export MENU_API_MONGO_USER=<mongo user>
export MENU_API_MONGO_PW=<mongo password>
export MENU_API_DB=<name of auth db for mongo user>
export MONGO_REMOTE=<mongodb hostname>
```

#### Build Image

```shell
make build
```

#### Start Server

```shell
make start
````
