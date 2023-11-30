In order to generate data to test metrics performances, the procedure is divided in two parts/tools:
- a synthetic dataset of KPIs + Indicators
- a log injector which injects raw Caddy logs

The synthetic dataset is useful to exercise the end-of-year computation of KPIs on a huge dataset.

The log injector is useful to exercise the live processing capability of incoming events.

## Synthetic dataset

Datetime of the test system must be manipulated for performance tests so that we update KPIS on the 1st of January at midnight. Since we keep data for one year (from 1st of January to 31st of December), this will be the worst case scenario.

Indicators are generated to represent a whole year of data.

KPIs are generated for all aggregation periods except the last ones which will be anyway computed by the live system: 6 days, 3 weeks, 2 months. For years, there are 3 years already stored in DB.


### Indicators

Indicators are very important since they consist in the sheer size of the database and are mandatory for KPI refresh.

Indicators are kept for one year, so we need to generate one year worth of data.

Indicator values are numerous because we keep all data since we do not yet know what will be useful (e.g. we keep track of the number of visits on all pages we find, because we will need it to compute the top 50 but do not yet know which pages will be the top 50 - any page even with very low volume could become the top 1 on the last day of the year if the page receives a very huge traffic on this last day).

The volume of indicators is the main driver of the load to refresh yearly, monthly, weekly and daily KPIs.

### KPIs

KPIs are not really useful since they are very small and almost do not impact performance, but this synthetic data will be very useful later on to exercise the UI with real data, so we still generate them.

### Data definition

We have defined an average yearly dataset which is used to generate the synthetic dataset. This average dataset is composed of sufficient data to generate indicators and KPIs.

Indicator values are randomized to produce different but still coherent values around a baseline.

KPI values are randomized as well, and scaled to adjust to the aggregation period (e.g. the monthly KPI will be 1/12th of the baseline, etc, ...).

Indicator dimensions (e.g. package name for popular packages) are partially defined in the average dataset. But for some data, we also need to generate some indicator dimensions randomly. E.g. for the PopularPages, we have some page names which have been defined in the average dataset and will be present in the top 50 (useful for UI testing for instance) but many pages with low visit volumes are generated and named for instance Page1, Page2, ... They are useful only to produce lots of data volume in the database.

Main driver of the data volume is the number of ZIMs which drives the number of packages and the number of pages visited.

### Scenarios

Multiple scenarios are tested for the average yearly dataset to exercise the system. We can test scenarios with 16, 50, 100, 200, 500 and finally 1000 ZIMs. We won't go further than 1000 since it is probably not ran on a small Pi3 or most content is never accessed.

For every scenario, we:
- create the synthetic dataset on a fast machine and transfer the DB to the test Pi 3
- start the benchmarking suite to record machine activity on the Pi3 (and wait few minutes so that we have a baseline of computing activity)
- position the clock just before midnight on 31 Dec
- start the metrics system (with processing activated)
- wait for the KPI update logic to trigger at midnight
- stop the metrics system
- transfer the benchmarking data to a fast machine and analyze the results
- observe the system performance at midnight where all KPIs (yearly, monthly, weekly and yearly) will have been refreshed, with what is almost the biggest possible dataset
  - we measure the time it takes to perform this end-of-year computation and the memory (RSS) consumed


## Log injection

Log injection consists in creating logs as Caddy would have produced them. They are then processed by metrics stack to create indicators (and then KPIs).

The log injection scenario can be either:
- ran during a small period of time (5-10 mins) just to assess the CPU / memory / disk IO consumption under a given load
- ran during a long period (1h, 24h, ...) to check the system stability on the long term (again in terms of CPU / memory / disk IO)

### Data definition

Log events are generated "manually", based on the Caddy log format and the reverse-engineering application URLs (or at least what we expect to compute inputs in metrics). We do not use real systems to simplify the testing procedure. We define the number of log events per kind of events (edupi file creation or deletion, edupi random request, ...). All these logs are generated in a temporary file and then randomized. This consumes a significant disk space but avoids to do all this in memory (which would probably never work on a Pi3). All logs are then inserted in the log file, which is also rotated as it would be in reality.

The load generated by the log injection is a function of:
- the number of log events generated for each kind of event
- an acceleration factor used to generate logs more kickly (with acceleration = 1, logs are equally spread on 24h, with acceleration = 4 they are spread on 6h, ...)

The load is repeated forever (i.e. once we have reached the end of logs to generate, we start over).

### Scenarios

Multiple scenarios are tested, from 1 log every 5 secs to 1 log every 0.05 secs.

For every scenario, we:
- start the benchmarking suite to record machine activity on the Pi3 (and wait few minutes so that we have a baseline of computing activity)
- start the metrics system (with processing activated)
- start the log injection
- stop the metrics system
- transfer the benchmarking data to a fast machine and analyze the results
- observe the system performance during log injection (CPU / memory / disk IO)
