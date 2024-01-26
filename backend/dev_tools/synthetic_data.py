import datetime
import logging
import random
from enum import Enum
from os import environ

from dateutil.relativedelta import relativedelta
from pydantic.dataclasses import dataclass
from sqlalchemy import delete, func, select, text

import offspot_metrics_backend.db.models as dbm
from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators import get_indicator_name
from offspot_metrics_backend.business.indicators.package import (
    PackageHomeVisit,
)
from offspot_metrics_backend.business.indicators.shared_files import (
    SharedFilesOperations,
)
from offspot_metrics_backend.business.inputs.shared_files import (
    SharedFilesOperationKind,
)
from offspot_metrics_backend.business.kpis import get_kpi_name
from offspot_metrics_backend.business.kpis.popularity import (
    PackagePopularity,
    PackagePopularityItem,
    PackagePopularityValue,
)
from offspot_metrics_backend.business.kpis.shared_files import (
    SharedFiles,
    SharedFilesValue,
)
from offspot_metrics_backend.business.kpis.total_usage import (
    TotalUsage,
    TotalUsageByPackage,
    TotalUsageItem,
    TotalUsageOverall,
    TotalUsageValue,
)
from offspot_metrics_backend.business.kpis.uptime import (
    Uptime,
    UptimeIndicator,
    UptimeValue,
)
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.constants import BackendConf, logger
from offspot_metrics_backend.db import Session, count_from_stmt
from offspot_metrics_backend.db.initializer import Initializer

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s: %(levelname)s] %(message)s"
)


class DatasetKind(str, Enum):
    """List of dataset kinds we can generate"""

    TWENTY = "TWENTY"
    FIFTY = "FIFTY"
    HUNDRED = "HUNDRED"
    HUNDRED_LIGHT = "HUNDRED_LIGHT"
    TWOHUNDRED = "TWOHUNDRED"
    TWOHUNDRED_LIGHT = "TWOHUNDRED_LIGHT"
    FIVEHUNDRED = "FIVEHUNDRED"
    FIVEHUNDRED_LIGHT = "FIVEHUNDRED_LIGHT"
    THOUSAND = "THOUSAND"
    THOUSAND_LIGHT = "THOUSAND_LIGHT"


@dataclass
class IndicatorData:
    """Dataclass to store existing indicator dimension already injected in DB"""

    iden: int
    value0: str | None
    value1: str | None
    value2: str | None


@dataclass
class Dataset:
    """Dataclass representing our synthetic dataset definition"""

    content_popularity: list["PackagePopularityData"]
    content_popularity_total: int
    content_popularity_random_packages_amount: int
    content_popularity_random_packages_visits: int
    usage_by_package: list["UsageData"]
    usage_overall: int
    shared_files_created: int
    shared_files_deleted: int
    offspot_uptime: int

    @dataclass
    class PackagePopularityData:
        package: str
        visits: int

    @dataclass
    class UsageData:
        package: str
        nb_slots: int  # number of 10 minutes slots


@dataclass
class AggKindAndValue:
    agg_kind: AggKind
    agg_value: str


periods_in_db: list[int] = []  # store list of periods already injected in DB
dimensions_in_db: list[
    IndicatorData
] = []  # store list of dimensions already injected in DB


def clear_db():
    """Delete all data and vacuum to reclain free space"""
    logging.info("Clearing DB")
    with Session.begin() as session:
        session.execute(delete(dbm.IndicatorRecord))
        session.execute(delete(dbm.IndicatorState))
        session.execute(delete(dbm.IndicatorDimension))
        session.execute(delete(dbm.IndicatorPeriod))
        session.execute(delete(dbm.KpiRecord))

    with Session.begin() as session:
        session.execute(text("VACUUM"))

    logging.info("DB is now empty")


now_period = Period(datetime.datetime.fromisoformat("2023-12-31 23:00:00"))


def scale_and_randomize_value(
    value: int,
    agg_kind: AggKind | None = None,
    lower_probability: int = -50,
    lower_value: int = 0,
    upper_probability: int = 150,
) -> int:
    """Generate a random and scaled value

    Scale is simply based on the number of days in the aggregation ; not applied if
    agg_kind is None
    Randomness is based on the lower and upper probabilities (percentages)
    Returned value is always 0 or above (hence the default negative lower probability
    which simulates higher chances of being lower_value)
    """
    factor = (
        1
        if agg_kind == AggKind.YEAR or agg_kind is None
        else 12
        if agg_kind == AggKind.MONTH
        else 52
        if agg_kind == AggKind.WEEK
        else 365
        if agg_kind == AggKind.DAY
        else 0
    )

    return max(
        lower_value,
        int(
            value / factor * random.randint(lower_probability, upper_probability) / 100
        ),
    )


def create_average_yearly_data(kind: DatasetKind):
    """Define the average yearly data dataset

    This dataset is then used to derive KPI and indicator values based on some
    randomness around this average yearly data (scaled to the number of
    days in the aggregation for KPIs)
    """
    logging.info("Creating average yearly data")

    content_popularity_random_packages_amount_dict: dict[DatasetKind, int] = {
        DatasetKind.TWENTY: 4,
        DatasetKind.FIFTY: 34,
        DatasetKind.HUNDRED: 84,
        DatasetKind.HUNDRED_LIGHT: 84,
        DatasetKind.TWOHUNDRED: 184,
        DatasetKind.TWOHUNDRED_LIGHT: 184,
        DatasetKind.FIVEHUNDRED: 484,
        DatasetKind.FIVEHUNDRED_LIGHT: 484,
        DatasetKind.THOUSAND: 984,
        DatasetKind.THOUSAND_LIGHT: 984,
    }

    return Dataset(
        shared_files_created=500,
        shared_files_deleted=100,
        offspot_uptime=90000,  # ~ 8 hours per day, 3.5 days per week in average
        content_popularity=[
            Dataset.PackagePopularityData(package="Wikipedia FR", visits=4000),
            Dataset.PackagePopularityData(package="Wikipedia EN", visits=4000),
            Dataset.PackagePopularityData(package="iFixit Guides FR", visits=4000),
            Dataset.PackagePopularityData(package="Khan Academy", visits=1000),
            Dataset.PackagePopularityData(package="Movies and TV", visits=1000),
            Dataset.PackagePopularityData(
                package="WikiMed Medical Encyclopedia FR", visits=1000
            ),
            Dataset.PackagePopularityData(package="TED MED", visits=1000),
            Dataset.PackagePopularityData(package="3D Printing", visits=500),
            Dataset.PackagePopularityData(package="African Storybooks", visits=500),
            Dataset.PackagePopularityData(
                package="Harnessing the future of data", visits=500
            ),
            Dataset.PackagePopularityData(
                package="Project Gutenberg Library", visits=500
            ),
            Dataset.PackagePopularityData(package="MathOverflow", visits=200),
            Dataset.PackagePopularityData(package="Chess", visits=200),
            Dataset.PackagePopularityData(
                package="WikiMed Medical Encyclopedia EN", visits=200
            ),
            Dataset.PackagePopularityData(
                package="The quest to end poverty", visits=100
            ),
            Dataset.PackagePopularityData(
                package="TED Talks - Entertainment", visits=100
            ),
        ],
        content_popularity_total=30000,
        # random packages that will be injected (to mimic real number of packages with
        # low total number of visits, which won't make it to the KPI but are still
        # stored for one year in indicators), with
        # - amount: total number of packages to create
        # - visit: yearly number of visits on each package (will be randomized)
        content_popularity_random_packages_amount=(
            content_popularity_random_packages_amount_dict[kind]
        ),
        content_popularity_random_packages_visits=50,
        usage_by_package=[
            Dataset.UsageData(package="Wikipedia FR", nb_slots=500),
            Dataset.UsageData(package="Wikipedia EN", nb_slots=500),
            Dataset.UsageData(package="iFixit Guides FR", nb_slots=200),
            Dataset.UsageData(package="Khan Academy", nb_slots=100),
            Dataset.UsageData(package="Movies and TV", nb_slots=100),
            Dataset.UsageData(package="WikiMed Medical Encyclopedia FR", nb_slots=100),
            Dataset.UsageData(package="TED MED", nb_slots=100),
            Dataset.UsageData(package="3D Printing", nb_slots=50),
            Dataset.UsageData(package="African Storybooks", nb_slots=50),
            Dataset.UsageData(package="Harnessing the future of data", nb_slots=50),
            Dataset.UsageData(package="Project Gutenberg Library", nb_slots=50),
            Dataset.UsageData(package="MathOverflow", nb_slots=20),
            Dataset.UsageData(package="Chess", nb_slots=20),
            Dataset.UsageData(package="WikiMed Medical Encyclopedia EN", nb_slots=20),
            Dataset.UsageData(package="The quest to end poverty", nb_slots=10),
            Dataset.UsageData(package="TED Talks - Entertainment", nb_slots=10),
        ],
        usage_overall=10000,  # minutes
    )


def get_all_previous_kpi_aggregations():
    """List all aggregations (year, month, ...) for which a KPI might exist"""
    previous_aggregations: list[AggKindAndValue] = []

    def get_year_agg_value(delta: int):
        return now_period.get_shifted(relativedelta(years=delta)).get_truncated_value(
            agg_kind=AggKind.YEAR
        )

    def get_month_agg_value(delta: int):
        return now_period.get_shifted(relativedelta(months=delta)).get_truncated_value(
            agg_kind=AggKind.MONTH
        )

    def get_week_agg_value(delta: int):
        return now_period.get_shifted(relativedelta(weeks=delta)).get_truncated_value(
            agg_kind=AggKind.WEEK
        )

    def get_day_agg_value(delta: int):
        return now_period.get_shifted(relativedelta(days=delta)).get_truncated_value(
            agg_kind=AggKind.DAY
        )

    for year in range(-4, 1):
        previous_aggregations.append(
            AggKindAndValue(agg_kind=AggKind.YEAR, agg_value=get_year_agg_value(year))
        )

    for month in range(-2, 1):
        previous_aggregations.append(
            AggKindAndValue(
                agg_kind=AggKind.MONTH, agg_value=get_month_agg_value(month)
            )
        )

    for week in range(-3, 1):
        previous_aggregations.append(
            AggKindAndValue(agg_kind=AggKind.WEEK, agg_value=get_week_agg_value(week))
        )

    for day in range(-6, 1):
        previous_aggregations.append(
            AggKindAndValue(agg_kind=AggKind.DAY, agg_value=get_day_agg_value(day))
        )
    return previous_aggregations


def inject_package_popularity_kpis(
    average_yearly_data: Dataset, previous_aggregations: list[AggKindAndValue]
):
    """Create package popularity KPIs in DB for all aggregations (year, month, ...)"""

    logging.info("Inject Package Popularity KPIs")
    with Session.begin() as session:
        for previous_aggregation in previous_aggregations:
            session.add(
                dbm.KpiRecord(
                    kpi_id=PackagePopularity.unique_id,
                    agg_kind=previous_aggregation.agg_kind,
                    agg_value=previous_aggregation.agg_value,
                    kpi_value=PackagePopularityValue(
                        items=sorted(
                            [
                                PackagePopularityItem(
                                    package=cdp.package,
                                    visits=scale_and_randomize_value(
                                        cdp.visits,
                                        agg_kind=previous_aggregation.agg_kind,
                                    ),
                                )
                                for cdp in average_yearly_data.content_popularity
                            ],
                            key=lambda ppi: ppi.visits,
                            reverse=True,
                        )[:10],
                        total_visits=scale_and_randomize_value(
                            average_yearly_data.content_popularity_total,
                            agg_kind=previous_aggregation.agg_kind,
                            lower_probability=50,
                        ),
                    ),
                )
            )


def inject_total_usage_kpis(
    average_yearly_data: Dataset, previous_aggregations: list[AggKindAndValue]
):
    """Create total usage KPIs in DB for all aggregations (year, month, ...)"""

    logging.info("Inject Total Usage KPIs")
    with Session.begin() as session:
        for previous_aggregation in previous_aggregations:
            session.add(
                dbm.KpiRecord(
                    kpi_id=TotalUsage.unique_id,
                    agg_kind=previous_aggregation.agg_kind,
                    agg_value=previous_aggregation.agg_value,
                    kpi_value=TotalUsageValue(
                        items=sorted(
                            [
                                TotalUsageItem(
                                    package=ud.package,
                                    minutes_activity=scale_and_randomize_value(
                                        ud.nb_slots,
                                        agg_kind=previous_aggregation.agg_kind,
                                    )
                                    * 10,
                                )
                                for ud in average_yearly_data.usage_by_package
                            ],
                            key=lambda tui: tui.minutes_activity,
                            reverse=True,
                        )[:10],
                        total_minutes_activity=scale_and_randomize_value(
                            average_yearly_data.usage_overall,
                            agg_kind=previous_aggregation.agg_kind,
                            lower_probability=50,
                        ),
                    ),
                )
            )


def inject_uptime_kpis(
    average_yearly_data: Dataset, previous_aggregations: list[AggKindAndValue]
):
    """Create uptime KPIs in DB for all aggregations (year, month, ...)"""

    logging.info("Inject Uptime KPIs")
    with Session.begin() as session:
        for previous_aggregation in previous_aggregations:
            session.add(
                dbm.KpiRecord(
                    kpi_id=Uptime.unique_id,
                    agg_kind=previous_aggregation.agg_kind,
                    agg_value=previous_aggregation.agg_value,
                    kpi_value=UptimeValue(
                        nb_minutes_on=scale_and_randomize_value(
                            average_yearly_data.offspot_uptime,
                            agg_kind=previous_aggregation.agg_kind,
                            lower_probability=50,
                        ),
                    ),
                )
            )


def inject_shared_files_kpis(
    average_yearly_data: Dataset, previous_aggregations: list[AggKindAndValue]
):
    """Create shared files KPIs in DB for all aggregations (year, month, ...)"""

    logging.info("Inject Shared Files KPIs")
    with Session.begin() as session:
        for previous_aggregation in previous_aggregations:
            session.add(
                dbm.KpiRecord(
                    kpi_id=SharedFiles.unique_id,
                    agg_kind=previous_aggregation.agg_kind,
                    agg_value=previous_aggregation.agg_value,
                    kpi_value=SharedFilesValue(
                        files_created=scale_and_randomize_value(
                            average_yearly_data.shared_files_created,
                            previous_aggregation.agg_kind,
                        ),
                        files_deleted=scale_and_randomize_value(
                            average_yearly_data.shared_files_deleted,
                            previous_aggregation.agg_kind,
                        ),
                    ),
                )
            )


def get_random_period(session: dbm.Session):
    """Select a random period during last year office hours

    The period is selected from 364 days ago to yesteday and online from 8am to 5pm
    It is created in DB if not already present"""
    period = now_period.get_shifted(
        relativedelta(days=random.randint(-365, -1), hours=random.randint(8, 17))
    )
    if period.timestamp not in periods_in_db:
        db_period = dbm.IndicatorPeriod.from_period(period)
        periods_in_db.append(db_period.timestamp)
        session.add(db_period)
    return period


def get_or_create_indicator_dimension(
    session: dbm.Session, value0: str | None, value1: str | None, value2: str | None
) -> IndicatorData:
    """Look after already existing indicator dimension or create a new one in DB"""
    dimension = next(
        filter(
            lambda dimension: dimension.value0 == value0
            and dimension.value1 == value1
            and dimension.value2 == value2,
            dimensions_in_db,
        ),
        None,
    )
    if dimension:
        return dimension
    dimension = dbm.IndicatorDimension(value0=value0, value1=value1, value2=value2)
    session.add(dimension)
    session.flush()
    data = IndicatorData(
        iden=dimension.id,
        value0=dimension.value0,
        value1=dimension.value1,
        value2=dimension.value2,
    )
    dimensions_in_db.append(data)
    return data


def inject_package_popularity_indicators(average_yearly_data: Dataset):
    """Create indicator records (and dimensions and periods) for package popularity"""

    logging.info("Inject Package Popularity Indicators")
    with Session.begin() as session:
        # First, randomly select a period for every input we should have received.
        # We have to select all periods first and count the number of visits per
        # package and period.
        # For convenience, we reuse the PackagePopularityValue dataclass to hold
        # this temporary data.
        values_per_period: dict[int, PackagePopularityValue] = {}
        for cpd in average_yearly_data.content_popularity:
            for _ in range(int(cpd.visits * 364 / 365)):
                # for every visit, select a random period and count 1
                period = get_random_period(session=session)
                current_value = values_per_period.get(period.timestamp, None)
                if not current_value:
                    current_value = PackagePopularityValue(
                        items=[],
                        total_visits=0,  # Unused, we only inject the indicator here
                    )
                    values_per_period[period.timestamp] = current_value

                current_item = next(
                    filter(
                        lambda item: item.package == cpd.package, current_value.items
                    ),
                    None,
                )
                if not current_item:
                    current_item = PackagePopularityItem(package=cpd.package, visits=0)
                    current_value.items.append(current_item)
                current_item.visits += 1

        # Also create random pages with low volume of visits
        for item_number in range(
            average_yearly_data.content_popularity_random_packages_amount
        ):
            package = f"Package{item_number}"
            for _ in range(
                scale_and_randomize_value(
                    average_yearly_data.content_popularity_random_packages_visits,
                    lower_probability=20,
                    lower_value=1,
                )
            ):
                period = get_random_period(session=session)
                current_value = values_per_period.get(period.timestamp, None)
                if not current_value:
                    current_value = PackagePopularityValue(
                        items=[],
                        total_visits=0,  # Unused, we only inject the indicator here
                    )
                    values_per_period[period.timestamp] = current_value

                current_item = next(
                    filter(lambda item: item.package == package, current_value.items),
                    None,
                )
                if not current_item:
                    current_item = PackagePopularityItem(package=package, visits=0)
                    current_value.items.append(current_item)
                current_item.visits += 1

        # Then we create indicator records (and dimensions if needed)
        for period_ts, value in values_per_period.items():
            for package_data in value.items:
                record = dbm.IndicatorRecord(
                    indicator_id=PackageHomeVisit.unique_id, value=package_data.visits
                )
                dimension = get_or_create_indicator_dimension(
                    session=session,
                    value0=package_data.package,
                    value1=None,
                    value2=None,
                )
                record.dimension_id = dimension.iden
                record.period_id = period_ts
                session.add(record)


def inject_total_usage_by_package_indicators(average_yearly_data: Dataset):
    """Create records (and dimensions and periods) for total usage by package"""

    logging.info("Inject Total Usage By Package Indicators")
    with Session.begin() as session:
        # First, randomly select a period for every input we should have received.
        # We have to select all periods first and count the usage amount per
        # package and period.
        # For convenience, we reuse the PopularPagesValue dataclass to hold
        # this temporary data.
        values_per_period: dict[int, TotalUsageValue] = {}
        for usage in average_yearly_data.usage_by_package:
            for _ in range(int(usage.nb_slots * 364 / 365)):
                # for every visit, select a random period and count 1
                period = get_random_period(session=session)
                current_value = values_per_period.get(period.timestamp, None)
                if not current_value:
                    current_value = TotalUsageValue(
                        items=[],
                        total_minutes_activity=0,
                    )
                    values_per_period[period.timestamp] = current_value

                current_item = next(
                    filter(
                        lambda value_item: value_item.package == usage.package,
                        current_value.items,
                    ),
                    None,
                )
                if not current_item:
                    current_item = TotalUsageItem(
                        package=usage.package, minutes_activity=0
                    )
                    current_value.items.append(current_item)
                current_item.minutes_activity += 10

        # Then we create indicator records (and dimensions if needed)
        for period_ts, value in values_per_period.items():
            for package_data in value.items:
                record = dbm.IndicatorRecord(
                    indicator_id=TotalUsageByPackage.unique_id,
                    value=package_data.minutes_activity,
                )
                dimension = get_or_create_indicator_dimension(
                    session=session,
                    value0=package_data.package,
                    value1=None,
                    value2=None,
                )
                record.dimension_id = dimension.iden
                record.period_id = period_ts
                session.add(record)


def inject_total_usage_overall_indicators(average_yearly_data: Dataset):
    """Create records (and dimensions and periods) for total usage overall"""

    logging.info("Inject Total Usage Overall Indicators")
    with Session.begin() as session:
        # First, randomly select a period for every input we should have received.
        # We have to select all periods first and count the usage amount per period.
        values_per_period: dict[int, int] = {}
        for _ in range(int(average_yearly_data.usage_overall / 10 * 364 / 365)):
            # for every visit, select a random period and count 1
            period = get_random_period(session=session)
            if period.timestamp not in values_per_period:
                values_per_period[period.timestamp] = 10
            else:
                values_per_period[period.timestamp] += 10

        # Then we create indicator records (and dimensions if needed)
        for period_ts, value in values_per_period.items():
            record = dbm.IndicatorRecord(
                indicator_id=TotalUsageOverall.unique_id,
                value=value,
            )
            dimension = get_or_create_indicator_dimension(
                session=session,
                value0=None,
                value1=None,
                value2=None,
            )
            record.dimension_id = dimension.iden
            record.period_id = period_ts
            session.add(record)


def inject_uptime_indicators(average_yearly_data: Dataset):
    """Create records (and dimensions and periods) for uptime"""

    logging.info("Inject Uptime Indicators")
    with Session.begin() as session:
        # First, randomly select a period for every input we should have received.
        # We have to select all periods first and count the usage amount per period.
        values_per_period: dict[int, int] = {}
        for _ in range(int(average_yearly_data.offspot_uptime * 364 / 365)):
            # select a random period and count 1
            period = get_random_period(session=session)
            if period.timestamp not in values_per_period:
                values_per_period[period.timestamp] = 1
            else:
                values_per_period[period.timestamp] += 1

        # Then we create indicator records (and dimensions if needed)
        for period_ts, value in values_per_period.items():
            record = dbm.IndicatorRecord(
                indicator_id=UptimeIndicator.unique_id,
                value=value,
            )
            dimension = get_or_create_indicator_dimension(
                session=session,
                value0=None,
                value1=None,
                value2=None,
            )
            record.dimension_id = dimension.iden
            record.period_id = period_ts
            session.add(record)


def inject_shared_files_indicators(average_yearly_data: Dataset):
    """Create indicator records (and dimensions and periods) for shared files"""

    logging.info("Inject Shared Files Indicators")
    with Session.begin() as session:
        # First, randomly select a period for every input we should have received.
        # We have to select all periods first and count the number of shared files
        # created / deleted per period
        # For convenience, we reuse the SharedFilesValue dataclass to hold
        # this temporary data.
        shared_files_values_per_period: dict[int, SharedFilesValue] = {}
        for _ in range(int(average_yearly_data.shared_files_created * 364 / 365)):
            # for every shared files created, select a random period and count 1
            period_ts = get_random_period(session=session)
            if period_ts.timestamp not in shared_files_values_per_period:
                shared_files_values_per_period[period_ts.timestamp] = SharedFilesValue(
                    files_created=0, files_deleted=0
                )
            shared_files_values_per_period[period_ts.timestamp].files_created += 1

        for _ in range(int(average_yearly_data.shared_files_deleted * 364 / 365)):
            # for every shared files deleted, select a random period and count 1
            period_ts = get_random_period(session=session)
            if period_ts.timestamp not in shared_files_values_per_period:
                shared_files_values_per_period[period_ts.timestamp] = SharedFilesValue(
                    files_created=0, files_deleted=0
                )
            shared_files_values_per_period[period_ts.timestamp].files_deleted += 1

        # Then we create indicator records (and dimensions if needed)
        for period_ts, value in shared_files_values_per_period.items():
            if value.files_created > 0:
                record = dbm.IndicatorRecord(
                    indicator_id=SharedFilesOperations.unique_id,
                    value=value.files_created,
                )
                dimension = get_or_create_indicator_dimension(
                    session=session,
                    value0=SharedFilesOperationKind.FILE_CREATED,
                    value1=None,
                    value2=None,
                )
                record.dimension_id = dimension.iden
                record.period_id = period_ts
                session.add(record)

            if value.files_deleted > 0:
                record = dbm.IndicatorRecord(
                    indicator_id=SharedFilesOperations.unique_id,
                    value=value.files_deleted,
                )
                dimension = get_or_create_indicator_dimension(
                    session=session,
                    value0=SharedFilesOperationKind.FILE_DELETED,
                    value1=None,
                    value2=None,
                )
                record.dimension_id = dimension.iden
                record.period_id = period_ts
                session.add(record)


def display_stats():
    """Display statistics about how many records are present in DB"""
    with Session.begin() as session:
        logger.info(
            f"{count_from_stmt(session, select(dbm.IndicatorState))} IndicatorState"
            " stored in DB"
        )

        details = ", ".join(
            [
                f"{get_indicator_name(row.indicator_id)}: {row.count}"
                for row in session.execute(
                    select(
                        dbm.IndicatorRecord.indicator_id,
                        func.count().label("count"),
                    ).group_by(dbm.IndicatorRecord.indicator_id)
                ).all()
            ]
        )

        logger.info(
            f"{count_from_stmt(session, select(dbm.IndicatorRecord))} IndicatorRecord"
            f" stored in DB ({details})"
        )
        logger.info(
            f"{count_from_stmt(session, select(dbm.IndicatorDimension))}"
            " IndicatorDimension stored in DB"
        )
        logger.info(
            f"{count_from_stmt(session, select(dbm.IndicatorPeriod))} IndicatorPeriod"
            " stored in DB"
        )

        details = ", ".join(
            [
                f"{get_kpi_name(row.kpi_id)}: {row.count}"
                for row in session.execute(
                    select(
                        dbm.KpiRecord.kpi_id,
                        func.count().label("count"),
                    ).group_by(dbm.KpiRecord.kpi_id)
                ).all()
            ]
        )
        logger.info(
            f"{count_from_stmt(session, select(dbm.KpiRecord))} KpiRecord stored in DB"
            f" ({details})"
        )


def synthetic_data():
    """Generate the synthetic dataset"""

    force = environ.get("FORCE", "N").lower() == "y"

    if not force:
        print(  # noqa: T201
            f"This will erase the whole database at {BackendConf.database_url}"
        )

        response = input("Are you sure you want to continue ? Type YES to confirm. ")
        if response != "YES":
            return

    Initializer.upgrade_db_schema()

    # seed with a constant value to have reproducible sims (123456 is just random)
    random.seed(a=123456)

    clear_db()

    kind = DatasetKind(environ.get("DATASET_KIND", "FIFTY"))
    logger.info(f"Generating {kind.value} dataset")

    average_yearly_data = create_average_yearly_data(kind)
    previous_kpi_aggregations = get_all_previous_kpi_aggregations()
    inject_package_popularity_kpis(
        average_yearly_data=average_yearly_data,
        previous_aggregations=previous_kpi_aggregations,
    )
    inject_total_usage_kpis(
        average_yearly_data=average_yearly_data,
        previous_aggregations=previous_kpi_aggregations,
    )
    inject_uptime_kpis(
        average_yearly_data=average_yearly_data,
        previous_aggregations=previous_kpi_aggregations,
    )
    inject_shared_files_kpis(
        average_yearly_data=average_yearly_data,
        previous_aggregations=previous_kpi_aggregations,
    )
    inject_package_popularity_indicators(average_yearly_data=average_yearly_data)
    inject_total_usage_by_package_indicators(average_yearly_data=average_yearly_data)
    inject_total_usage_overall_indicators(average_yearly_data=average_yearly_data)
    inject_uptime_indicators(average_yearly_data=average_yearly_data)
    inject_shared_files_indicators(average_yearly_data=average_yearly_data)

    display_stats()

    logger.info("DONE")


if __name__ == "__main__":
    synthetic_data()
