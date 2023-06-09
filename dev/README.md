This is a docker-compose configuration to be used **only** for development purpose.

It is recommended to use it in combination with Mutagen to effeciently sync data from your machine to the Docker containers.

## List of containers

### backend

This container is the backend web server.

### backend-tools

This container is simply a Python stack with all backend requirements (including qa) but no web server.

It is used to setup database, run tests, etc ...

Context is setup with appropriate environment variables:
- DATABASE_URL points to the database used by the backend
- TEST_DATABASE_URL points to the test database

### backend-tests

This container is simply a Python stack with all backend requirements but no web server. Context is
setup with appropriate environment variables for tests (i.e. it uses the test DB). Usefull to run
tests locally.

### frontend-ui

This container hosts the frontend UI for end-users.

## Instructions

First start the Docker-Compose stack:

```sh
cd dev
docker compose -p offspot_metrics up -d
```

## Setup DB

If this is your first run or if you made any schema change, you need to set/update the DB schema before having all containers OK.

Ask Alembic to update the schema:

```sh
docker exec -it om_backend-tools invoke db-upgrade
```

You can also check that everything is ok:
```sh
docker exec -it om_backend-tools invoke alembic --args "check"
```

Note that to run integration tests, we use a separate DB, you hence have to set/update the DB schema as well.
Just do the same as above with the backend-tests container (instead of the backend-tools)

## Restart the backend

The backend might typically fail if the DB schema is not up-to-date, or if you create some nasty bug while modifying the code.

Restart it with:
```sh
docker restart om_backend
```

Other containers might be restarted the same way.

## Run tests

Create + upgrade test DB schema if needed:

```sh
docker exec -it om_backend-tools invoke db-upgrade --test-db
```

Run all tests:
```sh
docker exec -it om_backend-tools invoke test
```

You can select one specific set of tests by path

```sh
docker exec -it om_backend-tools invoke test --path "unit/business/indicators/test_indicators.py"
```

Or just one specific test function

```sh
docker exec -it om_backend-tools invoke test --path "unit/business/indicators/test_indicators.py" --args "-k test_no_input"
```