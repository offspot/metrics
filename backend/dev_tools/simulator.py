import logging
import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

import offspot_metrics_backend.db.models as dbm
from offspot_metrics_backend.business.inputs.package import (
    PackageHomeVisit,
)
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.constants import BackendConf, logger

# Some known contents (some are repeated many times to influence the distribution)
contents = [
    "Wikipedia FR",
    "Wikipedia FR",
    "Wikipedia FR",
    "Wikipedia EN",
    "Wikipedia EN",
    "Wikipedia EN",
    "Gutenberg Project",
    "Gutenberg Project",
    "Gutenberg Project",
    "StackOverflow",
    "TED EN - 11 must see talks",
    "TED EN - 11 must see talks",
    "TED EN - How to survive following your passions",
    "TED EN - How to survive following your passions",
]

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s: %(levelname)s] %(message)s"
)


def restart_processor(now: datetime) -> Processor:
    """Start or restart the processor

    This is just like it would happen in real life when the process / machine is
    restarted
    """
    logger.info("(re-)Starting processor")
    processor = Processor()
    processor.startup(current_period=Period(now))
    return processor


def clear_db():
    """Clear all DB tables"""
    logger.info("Clearing database")
    with Session(create_engine(url=BackendConf.database_url, echo=False)) as session:
        with session.begin():
            session.execute(delete(dbm.IndicatorRecord))
            session.execute(delete(dbm.IndicatorState))
            session.execute(delete(dbm.IndicatorDimension))
            session.execute(delete(dbm.IndicatorPeriod))
            session.execute(delete(dbm.KpiRecord))


def rand_sim_update_now(now: datetime) -> datetime:
    """Move 'now' variable to a random point in time in the future

    'now' is increased by:
    - a random number of seconds between 0 and 5 (included)
    - with 25% chance, a random number of minutes between 0 and 5 (included)
    - with 6.25% chance, a random bumber of hours between 0 and 5 (included)
    """
    now = now + timedelta(seconds=random.randint(0, 5))
    if random.randint(0, 3) == 3:
        now = now + timedelta(minutes=random.randint(0, 5))
        if random.randint(0, 3) == 3:
            now = now + timedelta(hours=random.randint(0, 5))
    return now


def get_random_content() -> str:
    """Return one random content"""
    return contents[random.randint(0, len(contents) - 1)]


def rand_sim():
    """This is a big simulation, inputing random stuff many times"""
    nbsteps = 10000

    clear_db()

    now = datetime.fromisoformat("2023-01-01 00:00:00")
    processor = restart_processor(now)

    # seed with a constant value to have reproducible sims (123456 is just random)
    random.seed(a=123456)

    for step in range(nbsteps + 1):
        now = rand_sim_update_now(now)

        # randomly restart the processor (like if a shutdown occured)
        if random.randint(0, 5000) == 5000:
            # process a tick first to save everything in state ; this does not happens
            # like this in reality but is mandatory to be able to compare results
            processor.process_tick(tick_period=Period(now))
            processor = restart_processor(now)

        content = get_random_content()

        if random.randint(0, 10) == 10:
            processor.process_input(PackageHomeVisit(content))

        if random.randint(0, 10) == 10:
            processor.process_tick(tick_period=Period(now))

        if step % 1000 == 999:
            logger.info(f"{step+1} steps executed")

    logger.info(f"Completed, end of simulation: {now}")


def small_sim():
    """This is a first small simulation, usefull for checking processor restarts"""
    clear_db()

    now = datetime.fromisoformat("2023-01-01 00:00:00")
    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(PackageHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=45)

    for i in range(10):
        processor.process_input(PackageHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=15)

    processor.process_tick(tick_period=Period(now))

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(PackageHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(tick_period=Period(now))

    now = now + timedelta(minutes=59)

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(PackageHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(tick_period=Period(now))


if __name__ == "__main__":
    # small_sim()
    rand_sim()
