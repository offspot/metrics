Metrics - Data architecture
=======

![Data architecture](docs\images\architecture_data.excalidraw.png)

## Raw data

Raw data is produced by existing systems, typically reverse proxy log files, nmon system monitoring, ...

Raw data is expected to be purged at least when older than one year, at most when older than few minutes (needed to transfer them to indicators).

## Indicators

Indicators are intermediate data, computed based on raw data and meant to be easily "stackable" (at the hotspot level or more globally at the deployment/project level, or even world-wide).

Indicators have a granularity of one hour, sufficiently precise to produce detailed insight but still aggregated a bit to limit storage requirements.

Indicators do not contain any information about visitor / IP Adress / User-Agent since this information makes little sense in Kiwix setup (there is no logged-in user, IP Address are local and hence significantly reused,
User-Agent are often identical across devices in a deployment and devices are often reused by many users).

Each indicator record has the same structure:
- year
- month
- day
- day of week
- hour
- indicator
- value

Some sample types of indicators:
- pages opened (globally, excluding assets like CSS, JS, ...)
- pages opened in package X
- pages opened in sub-portion Y of package X
- package home pages opened

Indicators are often created on-the-fly, e.g. when based on package or sub-portion which are not known in advance.

Indicator records are stored in an SQLite database and purged after one year.

Back of the envelope size of one indicator record is 10 bytes (year: 2 + month: 1 + day : 1 + day of week : 1 + hour : 1 + indicator : 2 + value : 2) ; total DB is hence 87.6 KB per indicator record per year.

In a future release, indicators will be transfered to the Cloud so that more transverse KPIs could be computed (e.g. top package over a given deployement).

##  KPIs

KPIs are pre-computed values, with multiple aggregations horizons: daily, weekly, monthly and yearly.

Aggregations are computed based on indicators.

Each kind of aggregations has its own retention period:
- 7 days for daily
- 4 week for weekly
- 12 month for monthly
- indefinetely for yearly

Each kind of aggregations have its own refresh period :
- once per hour for daily, weekly and monthly
- one per day for yearly

All aggregations have a "pending" aggregation period (i.e. current day so far, current week so far, ...).

Aggregations are stored as well in an SQLite database.

Example KPI :
- Top 5 packages (sorted by nb of hits to home url of each content)
- Top 50 pages per package (sorted by nb of hits inside content, resources like css/js/fonts/etc excluded)

Back of the envelope size of one KPI record is 100 bytes (47 UTF-8 chars, assuming most will use only 2 bytes + 2 bytes to store KPI ID + 1 bytes to store order).

If we store a KPI at all aggregations levels  (daily, weekly, monthly and yearly), assuming 10 years retention of yearly indicators, it will consume 100 B * (7 + 4 + 12 + 10) = 3.3 KB

If we compute both example KPIs at all aggregation levels and assume 10 different packages present on the device, this give us a total DB size of 3.3 KB * (5 + 50 * 10) = 1.666 MB
