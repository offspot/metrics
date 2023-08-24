This is a docker-compose configuration to be used **only** for development purpose.

It is recommended to use it in combination with Mutagen to effeciently sync data from your machine to the Docker containers.

## List of URLS

- Reverse proxy ("fake"): http://localhost:8000
- Kiwix-serve ("fake"): http://localhost:8001
- Backend API: http://localhost:8002
- Dev Frontend: http://localhost:8003

## List of containers

### backend

This container is the backend web server.

### backend-tools

This container is simply a Python stack with all backend requirements (including qa) but no web server.

It is used to setup database, run tests, etc ...

Context is setup with appropriate environment variables:
- DATABASE_URL points to the database used by the backend
- TEST_DATABASE_URL points to the test database

### frontend-tools

This container hosts the development frontend UI (i.e. `yarn dev`). 

It is not the statically compiled version.

### kiwix-serve

This is a kiwix server, serving zim files placed in the `zims` subfolder.

See below for recommended ZIMs in the [Instructions](#instructions) section.

### reverse-proxy

This is the reverse proxy, simulating what is used on the offspot to expose multiple contents.

It is configured with a sample sets of contents :
- `kiwix-serve` contents
- a fake `nomad` content from `file-browser-data/nomad`
- a fake `mathews` content from `file-browser-data/mathews`

## Instructions

Download the ZIMs you want to use for tests in the `zims` folder. 

Caddy is configured to use these two zims:
- https://download.kiwix.org/zim/stack_exchange/sqa.stackexchange.com_en_all_2023-05.zim
- https://download.kiwix.org/zim/stack_exchange/devops.stackexchange.com_en_all_2023-05.zim

Start the Docker-Compose stack:

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
docker exec -it om_backend-tools invoke alembic check
```

Note that to run integration tests, we use a separate DB, you hence have to set/update the DB schema as well.
Just do the same as above with the backend-tests container (instead of the backend-tools)

## Run a simulation to inject synthetic data

In order to inject synthetic data into the database, a simulation script can be run

```sh
docker exec -it om_backend-tools python src/simulator.py
```

## Create real data

You can test the whole integration suite (i.e. with landing page, kiwix-serve and Filebeat).

**Nota:** this is not compatible from simulator data which will progressively be erased by new live data.

You first have to enable processing in `docker-compose.yml`: set `RUN_PROCESSING: "True"`.

```
docker compose -p om up -d --force-recreate backend
```

You can then browse packages at http://127.0.0.1:8000/ and statistics will show up after up to 1 hour in the web UI at http://127.0.0.1:8003/

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

### backend database schema

To generate DB schema documentation, you can run the following command once your
docker-compose setup is started (and supposing that your local DB is up-to-date):

```sh
cd dev
wget -O /tmp/sqlite-jdbc-3.42.0.0.jar https://github.com/xerial/sqlite-jdbc/releases/download/3.42.0.0/sqlite-jdbc-3.42.0.0.jar
docker run -name schemaspy-offspot-metrics --rm -v "/tmp/sqlite-jdbc-3.42.0.0.jar:/drivers/sqlite-jdbc-3.42.0.0.jar" -v "$(pwd)/schemaspy.properties:/schemaspy.properties" -v "$(pwd)/schemaspy:/output" -v "$(pwd)/../backend/src/offspot_metrics_backend/dev.db:/data/database.db" schemaspy/schemaspy:latest
```

Nota: of course you might update the Sqlite JDBC driver version 😉
