This is a docker-compose configuration to be used **only** for development purpose.

It is recommended to use it in combination with Mutagen to effeciently sync data from your machine to the Docker containers.

## List of URLS

- Reverse proxy ("fake"): http://localhost:8000
- Kiwix-serve ("fake"): http://localhost:8001
- Application: http://localhost:8002
- Dev Frontend: http://localhost:8003
- Edupi ("fake"): http://localhost:8004

## List of containers

### metrics

This container is the full application (UI + API), close to the real production container.

Python code is mounted inside the container and hot-reloaded (i.e. API development can be tested on this).

UI is statically compiled, so changes are not refreshed, use the frontend-tools UI for testing UI changes.

### backend-tools

This container is simply a Python stack with all backend requirements (including qa) but no web server.

It is used to setup database, run tests, etc ...

Context is setup with appropriate environment variables:
- DATABASE_URL points to the database used by the backend
- TEST_DATABASE_URL points to the test database

### frontend-tools

This container hosts the development frontend UI (i.e. `yarn dev`).

It is not the statically compiled version, so it is very usefull to test UI changes locally.

### kiwix-serve

This is a kiwix server, serving zim files placed in the `zims` subfolder.

See below for recommended ZIMs in the [Instructions](#instructions) section.

### reverse-proxy

This is the reverse proxy, simulating what is used on the offspot to expose multiple contents.

It is configured with a sample sets of contents :
- `kiwix-serve` contents
- a fake `nomad` content from `file-browser-data/nomad`
- a fake `mathews` content from `file-browser-data/mathews`

### edupi

This is an Edupi serve, to host files locally. See docker-compose for admin credentials.

## Instructions

Download the ZIMs you want to use for tests in the `zims` folder.

Kiwix-serve is configured to use these two zims which should be downloaded in the `zims` folder:
- https://download.kiwix.org/zim/stack_exchange/sqa.stackexchange.com_en_all_2023-05.zim
- https://download.kiwix.org/zim/stack_exchange/devops.stackexchange.com_en_all_2023-05.zim

Start the Docker-Compose stack:

```sh
cd dev
docker compose build --no-cache
docker compose -p offspot_metrics up -d
```

Nota: the build is mandatory only if you already started the stack previously and the code has changed significantly.

### Setup DB

If this is your first run or if you made any schema change, you need to set/update the DB schema before having all containers OK.

Ask Alembic to update the schema:

```sh
docker exec -it om_backend-tools invoke db-upgrade
```

You can also check that everything is ok:

```sh
docker exec -it om_backend-tools invoke alembic check
```

### Inject synthetic data

In order to inject synthetic data into the database, a script can be run:

```sh
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="TWENTY" python dev_tools/synthetic_data.py
```

Various DATASET_KIND are available, see the script for details. TWENTY is the smallest one, usually enough for UI tests.

### Create real data

You can test the whole integration suite (i.e. with landing page, kiwix-serve and Filebeat).

**Nota:** this is not compatible with synthetic data which will progressively be erased by new live data.

You first have to enable processing in `docker-compose.yml`: set `PROCESSING_DISABLED: "False"` (or just remove the environment variable).

```
docker compose -p offspot_metrics up -d --force-recreate backend
```

You can then browse packages at http://127.0.0.1:8000/ and statistics will show up after up to 1 hour in the web UI at http://127.0.0.1:8003/

### Restart the application

The application might typically fail if the DB schema is not up-to-date, or if you create some nasty bug while modifying the code.

Restart it with:

```sh
docker restart om_metrics
```

Other containers might be restarted the same way.

### Run tests

Create + upgrade test DB schema if needed:

```sh
docker exec -it om_backend-tools invoke db-upgrade --test-db
```

Check that schema is up to date:
```sh
docker exec -it om_backend-tools invoke alembic check --test-db
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
