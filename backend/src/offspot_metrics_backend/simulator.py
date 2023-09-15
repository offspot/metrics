import logging
import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

import offspot_metrics_backend.db.models as dbm
from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.constants import BackendConf

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

# For every known content, some known items
# (some are repeated many times to influence the distribution)
items = {
    "Wikipedia FR": [
        "Coupe_de_France_de_rugby_à_XIII_1938-1939",
        "Électricité_de_France",
        "Esthétique_environnementale",
        "Esthétique_environnementale",
        "Ouganda",
        "Jikji",
        "Kiwix",
        "Kiwix",
        "Kiwix",
    ],
    "Wikipedia EN": [
        "Kiwix",
    ],
    "Gutenberg Project": [
        "Romeo and Juliet_cover.1513",
        "The Blue Castle%3A a novel.67979",
        "The Odyssey_cover.1727",
    ],
    "StackOverflow": [
        "questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-"
        "unsorted-array",
        "questions/2003505/how-do-i-delete-a-git-branch-locally-and-remotely",
    ],
    "TED EN - 11 must see talks": [
        "do-schools-kill-creativity",
        "do-schools-kill-creativity",
        "the-danger-of-a-single-story",
    ],
    "TED EN - How to survive following your passions": [
        "how-to-find-work-you-love",
        "how-to-find-work-you-love",
        "how-to-find-work-you-love",
        "a-kinder-gentler-philosophy-of-success",
        "a-kinder-gentler-philosophy-of-success",
    ],
}


logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s: %(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


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


def get_random_item(content: str) -> str:
    """Return one random item"""
    if random.randint(0, 3) == 3:
        rnd = random.randint(0, 100)
        if rnd < 10:
            return "random_item_1"
        elif rnd < 12:
            return "random_item_2"
        elif rnd < 18:
            return "random_item_3"
        elif rnd < 25:
            return "random_item_4"
        elif rnd < 40:
            return "random_item_5"
        elif rnd < 52:
            return "random_item_6"
        elif rnd < 66:
            return "random_item_7"
        elif rnd < 72:
            return "random_item_8"
        elif rnd < 84:
            return "random_item_9"
        elif rnd < 90:
            return "random_item_10"
        elif rnd < 94:
            return "random_item_11"
        elif rnd < 96:
            return "random_item_12"
        else:
            return "random_item_11"
    else:
        return items[content][random.randint(0, len(items[content]) - 1)]


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

        random_item = get_random_item(content)

        if random.randint(0, 10) == 10:
            processor.process_input(ContentHomeVisit(content))
        else:
            processor.process_input(ContentItemVisit(content, random_item))

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
        processor.process_input(ContentItemVisit("content1", f"item{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=45)

    for i in range(10):
        processor.process_input(ContentItemVisit("content1", f"item{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=15)

    processor.process_tick(tick_period=Period(now))

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(ContentItemVisit("content1", f"item{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(tick_period=Period(now))

    now = now + timedelta(minutes=59)

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(ContentItemVisit("content1", f"item{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(tick_period=Period(now))


if __name__ == "__main__":
    # small_sim()
    rand_sim()
