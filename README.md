# Installation and running in development mode

## System Requirements:

    - python-poetry
    - docker
    - docker-compose

## Running webapi in local

### Clone the repo

`git clone git@gitlab.com:krispcall/krispcall-backend.git`

### Change into the project directory

`cd krispcall-backend`

### Create virtual environment

`poetry install`

### Export the development environment

`export KRISPCALL_APP_ENV=development`

>> Use `set` instead of export on Windows for setting env variables.
>> Create and place `development.yaml` or `production.yaml`
>>

### Create the docker container with the postgres

`docker-compose -f webapi/docker-compose.yaml up`

### Create a new database for salesdb

```bash
echo "create database salesdb;" | docker exec -i db psql -U postgres
```

### Alembic migrations

`poetry run cli webapi alembic migrate heads`
`poetry run cli salesapi alembic migrate heads`
`poetry run cli automationapi alembic migrate heads`

##### Run webapi server

`poetry run cli webapi serve`
`poetry run cli salesapi serve`
`poetry run cli krisprpc serve`
> create /var/logs and /var/secrets directory under root folder
> > Make sure you have /var/logs under /webapi, /salesapi, /analtyicsapi, /automationapi, and /krisprpc before running the project

>> Make sure you have /var under /webapi, /salesapi, /analtyicsapi, and /krisprpc before running the project
>>

---

## Development settings and setup in local

### Check alembic branches

`poetry run cli webapi alembic heads`
`poetry run cli salesapi alembic heads`
`poetry run cli automationapi alembic heads`

### Create migrations

`poetry run cli webapi alembic makemigrations --branch-label=example --message=" custom message"`
`poetry run cli salesapi alembic makemigrations --branch-label=example --message=" custom message"`
`poetry run cli automationapi alembic makemigrations --branch-label=example --message=" custom message"`

### Run migrations

`poetry run cli webapi alembic migrate heads`
`poetry run cli salesapi alembic migrate heads`
`poetry run cli automationapi alembic migrate heads`

---

## Creating new sub app

`register subapp or component in webapp/config.py`

`poetry run cli webapi alembic initrevision --message "Init example base" --branch-label=example --version-path=krispcall/example/alembic_versions/`

`poetry run cli automationapi alembic initrevision --message "Init example base" --branch-label=example --version-path=krispcall/example/alembic_versions/`

> > Only use in case of subapp migrations

---

## Docker Commands

### Copy and create `production.yaml` file

```bash
cp webapi/config/production.yaml.sample webapi/config/production.yaml
```

>> Make sure you are changing `@db` to `@localhost` when serving on local.
>>

### Build image

```bash
docker build -t codeavatar/krispcall:0.0.1 .
```

### Copy var to webapi

```bash
cp -r var webapi/
```

### Run application

```bash
docker-compose up
```

### Run application in the background

```bash
docker-compose up -d
```

## Stop Application

```bash
docker-compose down
```

---

## Database operations with docker and alembic

### Create database tables

```bash
docker exec -t api python cli.py alembic migrate
```

### Dump database

```bash
docker exec -it db pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```

### Restore the dump

```bash
cat dump_some_date.sql | docker exec -i db psql -U postgres
```

### Running Worker

```bash
poetry run arq webapi.worker_swarm.general_worker.WorkerSettings
poetry run arq webapi.worker_swarm.payment_worker.WorkerSettings
poetry run arq webapi.worker_swarm.twilio_worker.WorkerSettings
poetry run arq webapi.worker_swarm.log_worker.WorkerSettings
poetry run arq webapi.worker_swarm.crm_worker.WorkerSettings

```

### Loading Policies

```bash
poetry run cli webapi load_permission_policy
poetry run cli webapi load_plan_policy
```

## Refreshing and fixing routes

```bash
poetry run cli webapi channels  check_and_repair_routes WORKSPACE_SID
```

## Compiling po files to mo files

```bash
msgfmt -o <path_to_base.mo> <path_to_base.po>
*msgfmt installation required
```
