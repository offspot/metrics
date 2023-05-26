Metrics - Software architecture
=======
## Backend

### Stack

Standard OpenZIM stack:
- Python 3.11
- API : FastAPI
- ORM/DB : SQLAlchemy
- pytest

### KPI/indicators definition and update

KPI/indicators are defined in the code only. Some definitions are generic, i.e. they can create multiple indicators / KPI on the fly. Some definitions can also be configured via a configuration file.

It is possible to create a new indicator / KPI or to update their computation. This has no impact on previous data / records / aggregations, which are kept as-is. Old raw-data is not processed to re-compute new indicator / KPIs, only new one is used on-the-fly (the benefit is too little compared to the complexity of managing such rare situations). 

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
