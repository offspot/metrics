Glossary
=======

# Input

An input is a pre-processed information that something happened. It is pre-processed meaning that we have already transformed the raw data (e.g. a reverse proxy log line) into a business information (e.g. someone visited the home page of the 'wikipedia_en' content).

Multiple kind of inputs 

# Period

A period is a timespan of one hour. It is hence represented by a date (day, month, year) and hour. Time is always relative to the local machine timezone (which is supposed to always be UTC).

# Indicator

An indicator is an aggregation of input information over a period (i.e. one hour). Indicators are transient information.

Example: the number of visits of contents home pages.

One indicator has multiple dimensions (e.g. one per content name) and multiple records (one per dimension and per period).

# Indicator Dimension

Am indicator dimension is used to store the textual value of an indicator (e.g "wikipedia_en"). Dimensions are reused across multiple records / periods.

# Indicator Record

An indicator record is the value of given indicator across a given dimension for a given period.

# KPI

A KPI is the business indicator. For a given KPI, there is one value per aggregation kind (daily, weekly, ...) and aggregation value (day 1, day 2, ...). The KPI value is usually complex. 

For instance, it might be the list of all contents order by number of visits. The KPI value for a given aggregation kind and aggregation value is hence a list. And for each item in the list, we store the content title, the total number of visit during the aggregation kind/value, the percentage relative to the total number of visit across all contents during the aggregation kind/value, etc...
