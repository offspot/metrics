Metrics
=======

The `metrics` subsystem is responsible to transform raw data (e.g. web server logs) available on the offspot into business-oriented KPIs displayed on web dashboards. 

The whole system is runing locally on the offspot. Dashboards are hence only presenting local offspot data.

At some point in the future, the system is meant to centralize data in a Cloud for aggregating multiple offspots. An intermediate data format is hence present, between raw data and KPIs.

## High-level overview

![Technical architecture](architecture_technical.excalidraw.png)

A Logstash server is used to process the various inputs easily (read rotating log files nicely, poll a webserver with some stats, ...) and forwards these events (via HTTP) to a backend server.

A custom backend server is responsible to process events sent by Logstash to compute indicator records. 

On-the-fly, every indicator has a current state used to store intermediate computations that will be needed to create the final record value. This state is updated at each event.

Indicator states are kept in memory. They are transfered to the SQLite database every minute (this is mandatory since it is quite common that the offspot is not shutdown properly).

The backend is also capable to handle nicely SIGINT signals to shutdown Logstash properly and transfer all indicator state to the database.

When the backend starts, it first reload this state data from database.

Every hour, the backend server process automatically the indicator states to create indicator records. It then computes/updates KPI aggregations. Indicator records and KPI aggregations are immediately persisted to the SQLite DB.

KPI aggregations do not rely on an in-memory state, they reuse as many indicator records as necessary every time.

The custom backend is serving the KPI data via a REST API.

A Vue.JS application serves dashboards of the KPI data.

## SQLite

SQLite is **highly resistant to corruption**, even when a power failure occurs in the middle of a transaction. However, [corruption might still occur](https://www.sqlite.org/howtocorrupt.html). 

Probability is however very low, [detection](https://www.sqlite.org/pragma.html#pragma_integrity_check) is time/resource-consuming, fully automated recovery is highly improbable (aside from restoring as many records as possible, we also need to perform applicative recovery for consistency).

Moreover, since there is little chance that this corruption targets more specifically SQLite database than any other part of the system (which have no recovery mechanism), the risk is assumed and no [recovery](https://sqlite.org/cli.html#recover) is implemented for SQLite DB.

Backups of the DB are not considered either since the disk space is constrained in our situation, and we can reasonably assume that we need to keep many backups since detection of corruption might be many days after it occurs.