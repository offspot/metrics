These are instructions to run performance tests

Monitoring and analysis are done with https://github.com/benoit74/benchmarking

These instructions have to be adapted to your local setup.

In the local setup described below, we used:
- a Raspberry Pi (monitored node) to run offspot/metrics + log injector
- a "powerfull" server (analysis node) to analyze test results (with ES + Kibana + custom tooling)
- a local laptop to serve as a "control tower" (Raspberry Pi and powerfull server do not see each others)

# How to run synthetic data tests

Here, the goal is to load a test DB with lots of data, set the time just before midnight on Dec. 31 and wait for end-of-year computation.

We observe the duration of the whole computation + the RAM consumption (CPU is always at 100% during this period, the system tries to run the end-of-year computation as fast as possible).

## Preparation

Preparation consists in creating all datasets in advance on the powerfull server and transferring them on the Pi.

### On Raspberry Pi

- Disable NTP clock synchronization and check status:

```sh
sudo timedatectl set-ntp false
timedatectl status
```

- Clone the benchmarking + offspot/metrics repositories and set environment variables accordingly

```sh
# path where the benchmarking repo is stored
BENCH_REPO_PATH="~/benchmarking"
# path where the metrics repo is stored
METRICS_REPO_PATH="~/metrics"
```

- In offspot/metrics:
  - modify the dev stack to start only backend and backend_tools containers (other are useless)
  - modify the backend-tools/Dockerfile to install only production Python dependencies (`.` instead of `.dev`)

- Create a temporary directory which will hold all test databases

```sh
DB_DIR="/data/perf"
sudo mkdir -p $DB_DIR
sudo chown user:user $DB_DIR
rm -rf "$DB_DIR/*"
```

### On powerfull server

- Clone the benchmarking + offspot/metrics repositories and set environment variables accordingly

```sh
# path where the benchmarking repo is stored
BENCH_REPO_PATH="/home/benoit/Repos/benoit74/benchmarking"
# path where the metrics repo is stored
METRICS_REPO_PATH="/home/benoit/Repos/offspot/metrics"
```

- In dev stack, ensure that processing is disabled for backend and backend_tools

- Start the dev stack (backend_tools at least)

- Generate synthetic databases

```sh
TMP_DIR="/tmp/perf_datasets"
mkdir -p $TMP_DIR
rm -rf "$TMP_DIR/*"

echo "Generating TWENTY dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="TWENTY" python dev_tools/synthetic_data.py > $TMP_DIR/test_twenty.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_twenty.db
echo "Generating FIFTY dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="FIFTY" python dev_tools/synthetic_data.py > $TMP_DIR/test_fifty.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_fifty.db

echo "Generating HUNDRED_LIGHT dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="HUNDRED_LIGHT" python dev_tools/synthetic_data.py > $TMP_DIR/test_hundred_light.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_hundred_light.db
echo "Generating TWOHUNDRED_LIGHT dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="TWOHUNDRED_LIGHT" python dev_tools/synthetic_data.py > $TMP_DIR/test_twohundred_light.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_twohundred_light.db
echo "Generating FIVEHUNDRED_LIGHT dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="FIVEHUNDRED_LIGHT" python dev_tools/synthetic_data.py > $TMP_DIR/test_fivehundred_light.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_fivehundred_light.db
echo "Generating THOUSAND_LIGHT dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="THOUSAND_LIGHT" python dev_tools/synthetic_data.py > $TMP_DIR/test_thousand_light.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_thousand_light.db

echo "Generating HUNDRED dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="HUNDRED" python dev_tools/synthetic_data.py > $TMP_DIR/test_hundred.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_hundred.db
echo "Generating TWOHUNDRED dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="TWOHUNDRED" python dev_tools/synthetic_data.py > $TMP_DIR/test_twohundred.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_twohundred.db
echo "Generating FIVEHUNDRED dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="FIVEHUNDRED" python dev_tools/synthetic_data.py > $TMP_DIR/test_fivehundred.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_fivehundred.db
echo "Generating THOUSAND dataset"
docker exec -it om_backend-tools env FORCE="Y" DATASET_KIND="THOUSAND" python dev_tools/synthetic_data.py > $TMP_DIR/test_thousand.txt
cp $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db $TMP_DIR/test_thousand.db

```

### On local laptop

- Create a temporary directory which will hold all files in transit

```sh
TMP_DIR="/tmp/offspot"
mkdir -p $TMP_DIR
rm -rf "$TMP_DIR/*"
```

And set environment variables appropriatly

```sh
POWERFULL_SERVER_HOSTNAME="hetzner1"
RASPBERY_PI_HOSTNAME="koffspot"
POWERFULL_SERVER_TMP_DIR="/tmp/perf_datasets"
RASPBERY_PI_DB_DIR="/data/perf"
POWERFULL_SERVER_BENCH_REPO_PATH="/home/benoit/Repos/benoit74/benchmarking"
RASPBERY_PI_BENCH_REPO_PATH="~/benchmarking"
```

- Transfer files between powerfull server and Raspberry PI

```sh
scp -r "$POWERFULL_SERVER_HOSTNAME:$POWERFULL_SERVER_TMP_DIR/*" $TMP_DIR/
scp -r $TMP_DIR/* $RASPBERY_PI_HOSTNAME:$RASPBERY_PI_DB_DIR
```

## For every synthetic dataset

### On Raspberry Pi

- Cleanup previous runs and start stuff (adjust name of DB file to use)

```sh
find $(eval echo $BENCH_REPO_PATH/monitored_node/output) -name "*.ndjson*" -type f -delete

sudo date 123123582023.00

cp $(eval echo $DB_DIR/dev_twenty.db) $(eval echo $METRICS_REPO_PATH/backend/src/offspot_metrics_backend/dev.db)

sudo systemctl start benchmarking-compressor.service
sudo systemctl start benchmarking-metricbeat.service

cd $(eval echo $METRICS_REPO_PATH/dev)

docker compose -p offspot up -d
```

### On powerfull server

- Archive raw data of previous run, cleanup and restart

```sh

# name used to archive perf data from previous run
DATANAME="data_perf_log_injection2"

cd $BENCH_REPO_PATH/analysis_node

docker compose -p bench down

find $BENCH_REPO_PATH/analysis_node/input -name "*.done" -type f -delete

mv $BENCH_REPO_PATH/analysis_node/input $BENCH_REPO_PATH/analysis_node/$DATANAME
tar -czvf $DATANAME.tar.gz -C $BENCH_REPO_PATH/analysis_node $DATANAME
mv $BENCH_REPO_PATH/analysis_node/$DATANAME $BENCH_REPO_PATH/analysis_node/input

find $BENCH_REPO_PATH/analysis_node/input -name "*.ndjson*" -type f -delete

docker volume rm bench_esdata01
docker volume rm bench_kibanadata

docker compose -p bench up -d
```

### On local laptop

Cleanup temporary data:

```sh
rm -rf "$TMP_DIR/*"
```

### On Raspberry Pi

Wait for background processing to trigger yearly computation and complete. Note down execution duration.

```sh
docker logs -f offspot_backend
```

Prepare data transfer and stock the stacks.

```sh
sudo chown -R user:user $(eval echo $BENCH_REPO_PATH/monitored_node/output/)

sudo systemctl stop benchmarking-metricbeat.service
sudo systemctl stop benchmarking-compressor.service

docker compose -p offspot down
```

### On local laptop

Transfer files between Raspberry PI and powerfull server:

```sh
rm -rf "$$TMP_DIR/*"
scp -r "$RASPBERY_PI_HOSTNAME:$RASPBERY_PI_BENCH_REPO_PATH/monitored_node/output/*" $TMP_DIR/
scp -r $TMP_DIR/* $POWERFULL_SERVER_HOSTNAME:$POWERFULL_SERVER_BENCH_REPO_PATH/analysis_node/input
```

### On powerfull server

Open Kibana UI (http://localhost:5601), log in with user/password (elastic/changeme) and observe data (adjust date/time to begining of year, do not forget that Kibana UI adjust the time to your local machine one, including in selector).

# How to run log injection

To run log injection, you should reuse the same instructions than for synthetic data with the "TWENTY" dataset (we do not mind to have much data in DB).

The only difference is that instead of just waiting for the end-of-year computation to complete, you will start to inject logs in log files.

Depending on what you want to observe, you might want to wait a long time (1h, 24h, ...) to collect long term performance under "stress".

To do this, it is advised to use the `backend_tools` container on the Rapsberry Pi:

```sh
docker exec -it om_backend-tools env ACCELERATION="1" python dev_tools/log_injector.py
```

You should probably run this in a `screen` session so that you can disconnect safely from the Rapsberry Pi machine.

You can adjust the `ACCELERATION` environment variable to inject more or less logs. An acceleration of 1 create one log about every 0.4 secs. An acceleration of 10 will hence inject one
log every 0.04 secs. The dataset is replayed forever, so you shouldn't mind about exhausting it.
