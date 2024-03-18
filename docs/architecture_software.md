Metrics - Software architecture
=======
## Backend

### Stack

Standard OpenZIM stack:
- Python 3.11
- API : FastAPI
- ORM/DB : SQLAlchemy
- pytest

### Business logic

The business logic is responsible to implement the logic which handles the transformation from raw logs into KPIs.

Raw logs are transformed into inputs via the [LogConverter](backend/src//backend/business/log_converter.py). This LogConverter is configured by the `packages.yaml` configuration file used on the `offspot` to configure Caddy reverse proxy. This is mandatory to automatically associate host names with content title for instance.

Inputs are then transformed into Indicators by an [Indicator Processor](backend/src//backend/business/indicators/processor.py). This processor knows the list of all indicators configured on the system. It is responsible to :
- proposes each input to each indicator capable to handle the current kind of input
- transfer data once per minute into the database to resist unattended process shutdown (e.g. due to power outages)
- refresh indicators once per hour and store them into the database
- cleanup old indicators data and associated unused data
- reload transient data from the database when the backend restarts (after a power cycle for instance)

Indicators are then transformed into Kpis by a [KPI Processor](backend/src//backend/business/kpis/processor.py). This processor knows the list of all kpis configured on the system. It is responsible to :
- refresh all KPIs aggregation once per hour (or per day for yearly aggregations) and store them into the database
- refresh KPIs when the backend restarts (after a power cycle for instance, some KPIs might have to be refreshed)
- maintain only the expected number of aggregations (7 for daily aggregations, ...)

### KPI/indicators definition and update

KPIs and indicators are defined in the code only.

It is possible to create a new indicators / KPIs or to update their computation. This has no impact on previous data, which is kept as-is. Old raw-data (which is not kept anyway) is not re-processed to re-compute new indicator / KPIs, only new raw-data is used on-the-fly.

It is possible to remove an indicator / KPI. In such a case, all historical values are removed from the databases.

## Frontend
### Stack

Standard OpenZIM stack:
- VueJS 3, Vue Router 4, Vuex 4 and axios for HTTP communications
- Bootstrap 5 for UI. FontAwesome (via vue-fontawesome) for icons
- Vuejs Coding Style, 2 spaces, no-tab indentation (idem for HTML and CSS)

Custom:
- TbD (do we really need charts ? cf. datapost)

### Dashboards
