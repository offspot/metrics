import logging
import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

import backend.db.models as dbm
from backend.business.inputs.content_visit import ContentHomeVisit, ContentObjectVisit
from backend.business.period import Period
from backend.business.processor import Processor
from backend.constants import BackendConf

# Some known contents (some are repeated many times to influence the distribution)
contents = [
    "wikipedia_fr",
    "wikipedia_fr",
    "wikipedia_fr",
    "wikipedia_en",
    "wikipedia_en",
    "wikipedia_en",
    "gutenberg",
    "gutenberg",
    "gutenberg",
    "stackoverflow",
    "ted_en_playlist-11-must-see-ted-talks",
    "ted_en_playlist-11-must-see-ted-talks",
    "ted_en_playlist-how-to-survive-following-your-passions",
    "ted_en_playlist-how-to-survive-following-your-passions",
]

# For every known content, some known objects
# (some are repeated many times to influence the distribution)
objects = {
    "wikipedia_fr": [
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
    "wikipedia_en": [
        "Kiwix",
    ],
    "gutenberg": [
        "Romeo and Juliet_cover.1513",
        "The Blue Castle%3A a novel.67979",
        "The Odyssey_cover.1727",
    ],
    "stackoverflow": [
        "questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-"
        "unsorted-array",
        "questions/2003505/how-do-i-delete-a-git-branch-locally-and-remotely",
    ],
    "ted_en_playlist-11-must-see-ted-talks": [
        "do-schools-kill-creativity",
        "do-schools-kill-creativity",
        "the-danger-of-a-single-story",
    ],
    "ted_en_playlist-how-to-survive-following-your-passions": [
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
            session.execute(delete(dbm.KpiValue))


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


def get_random_content_from_sim() -> str:
    return contents[random.randint(0, len(contents) - 1)]


def get_random_object_from_sim(content: str) -> str:
    if random.randint(0, 3) == 3:
        rnd = random.randint(0, 100)
        if rnd < 10:
            return "random_object_1"
        elif rnd < 12:
            return "random_object_2"
        elif rnd < 18:
            return "random_object_3"
        elif rnd < 25:
            return "random_object_4"
        elif rnd < 40:
            return "random_object_5"
        elif rnd < 52:
            return "random_object_6"
        elif rnd < 66:
            return "random_object_7"
        elif rnd < 72:
            return "random_object_8"
        elif rnd < 84:
            return "random_object_9"
        elif rnd < 90:
            return "random_object_10"
        elif rnd < 94:
            return "random_object_11"
        elif rnd < 96:
            return "random_object_12"
        else:
            return "random_object_11"
    else:
        return objects[content][random.randint(0, len(objects[content]) - 1)]


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
            processor.process_tick(current_period=Period(now))
            processor = restart_processor(now)

        content = get_random_content_from_sim()

        object = get_random_object_from_sim(content)

        if random.randint(0, 10) == 10:
            processor.process_input(ContentHomeVisit(content))
        else:
            processor.process_input(ContentObjectVisit(content, object))

        if random.randint(0, 10) == 10:
            processor.process_tick(current_period=Period(now))

        if step % 1000 == 999:
            logger.info(f"{step+1} steps executed")

    logger.info(f"Completed, end of simulation: {now}")


def small_sim():
    """This is a first small simulation, usefull for checking processor restarts"""
    clear_db()

    now = datetime.fromisoformat("2023-01-01 00:00:00")
    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(ContentObjectVisit("content1", f"object{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=45)

    for i in range(10):
        processor.process_input(ContentObjectVisit("content1", f"object{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(seconds=15)

    processor.process_tick(current_period=Period(now))

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(ContentObjectVisit("content1", f"object{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(current_period=Period(now))

    now = now + timedelta(minutes=59)

    processor = restart_processor(now)

    for i in range(10):
        processor.process_input(ContentObjectVisit("content1", f"object{(i+2) % 4}"))
        processor.process_input(ContentHomeVisit(f"content{(i+2) % 3}"))

    now = now + timedelta(minutes=1)

    processor.process_tick(current_period=Period(now))


if __name__ == "__main__":
    # small_sim()
    rand_sim()
