Database schema
=======

## Indicator records

One indicator record hold the value of:
- a given indicator (e.g. number of visits on contents homes)
- for a given [period](#indicator-periods) (8. July 2023 at 8am)
- and a given [dimension](#indicator-dimensions) (wikipedia)

![Indicators record](docs/images/database_indicator_record.excalidraw.png)

One given indicator (number of visits on contents homes) may have multiple records for a given period because there is multiple dimensions (wikipedia, ted, gutenberg, ...).

One given indicator (number of visits on contents homes) may have multiple records for a given dimension because there is multiple periods (8am, 9am, ...).

Indicator values are simple string to allow to store any complex indicator value that has been serialized (could by lists, lists of dicts, ...).

## Indicator periods

Periods are a given hour on a given calendar day. They are stored in the `indicator_period` table.

The primary goal is to store the epoch timestamp of the period, since this is sufficient to store the information needed + this make queries for a time range (which we almost always need) performant. This column is directly used as a Primary Key since it is already a unique column.

Storing the timestamp in a distinct period table is efficient for queries probably because it will be a unique index, while placing the information directly in Indicator record and Indicator state tables will be a regular index, plus we will need two of them.

For now we do not need more information about the period for some queries to compute some kind of indicators, so we do not extra information in this table (could be the year, month, day, hour, and weekday, with an index on each of them, but is is not used so we avoid the useless extra).

## Indicator dimensions

Dimensions are a represented by one to three values. They are stored in the `indicator_dimension` table.

Indicator dimensions are used to represent the fact that one indicator (e.g. number of visits on contents homes) might need multiple values for a given period (e.g. one per content).

Indicator dimensions might need multiple values for one dimension. For instance the indicator "number of visits on one content page" needs two values, one to store the content name and one to store the page identifier. `metrics` currently supports up to three values.

## Indicator states

Indicator states are the transient values of the indicators before they are transformed in records every hour.

![Indicators state](docs/images/database_indicator_state.excalidraw.png)

States are hence also linked to a period and a dimension, as well as an indicator value (or transient state more exactly). Period and dimension records are shared between states and records.

States are stored in the DB every minute because the offspot might be shut down without prior notice, so we need this to avoid loosing too much data.

They are deleted when the corresponding record is created.

State values usually have a different data structure than indicator records. For instance, to compute an indicator which is the average of some data, we have to store the sum of values and the number of values in the state, before computing the average at record creation.

## Kpi

One single table is used to store KPIs with following columns:
- `kpi_id`: the unique identifier of the KPI
- `agg_kind`: the kind of aggregation for this KPI value (Daily, Weekly, Monthly, Yearly). Only first letter is stored.
- `agg_value`: the value of the aggregation for this KPI value (e.g 2023-06-01 for a daily aggregation, 2023 for a yearly aggregation, ...)
- `kpi_value`: the value of the given KPI for the given `agg_kind` and `agg_value` (e.g. the value of KPI id `1` for the `Month` of `March 2023`)

![KPI](docs/images/database_kpi.excalidraw.png)

Just like for indicators values, KPI values are stored as string so that we can store an serialized object.