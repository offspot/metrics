""" Simulate offspot activity by creating log lines in Caddy format.

This script is used to simulate an offspot activity and observe metrics behavior.
In order to reproduce the whole chain with high fidelity, logs are created in Caddy
JSON format and pushed to a log file just like Caddy would do. The rest of the chain is
not modified at all.

Injector behavior is parameterized to reproduce various usage patterns / volumes.
"""

import datetime
import json
import logging
import os
import random
import time
from collections.abc import Generator
from io import TextIOWrapper
from itertools import chain
from pathlib import Path
from typing import Any, NamedTuple

from pydantic.dataclasses import dataclass

from offspot_metrics_backend.constants import logger

logging.basicConfig(
    level=logging.DEBUG, format="[%(asctime)s: %(levelname)s] %(message)s"
)


@dataclass
class Setup:
    target_folder: str  # Folder where logs will be created
    tmp_folder: str  # Folder where temporary file(s) will be created
    max_log_size: int  # Simulated caddy log size where rotation happens
    edupi_activity: "EdupiActivity"  # Details of EduPi activity
    zim_normalized_activity: "NormalizedZimActivity"  # Normalized activity for one ZIM
    zims_with_scaling: list["ZimAndScale"]  # List of ZIMs + scaling factor
    other_activity: list[
        "OtherPackageAndActivity"
    ]  # Details of activity on other packages

    class EdupiActivity(NamedTuple):
        hostname: str
        homepage: int
        randompage: int
        files_created: int
        files_deleted: int

    class OtherPackageAndActivity(NamedTuple):
        hostname: str
        homepage: int
        randompage: int

    class NormalizedZimActivity(NamedTuple):
        homepage: int
        randompage: int
        randomasset: int

    class ZimAndScale(NamedTuple):
        zim: str
        hostname: str
        scale_factor: int


ACCELERATION = float(
    os.getenv("ACCELERATION", "1")
)  # let's play the generated logs xx times per 24h (avoids too big tmp file)


SETUP = Setup(
    target_folder=os.getenv(
        "LOG_INJECTOR_TARGET", "/tmp/caddy_logs"  # noqa S108 # nosec B108
    ),
    tmp_folder=os.getenv(
        "LOG_INJECTOR_TMP", "/tmp/log_injector"  # noqa S108 # nosec B108
    ),
    max_log_size=1000000,
    edupi_activity=Setup.EdupiActivity(
        hostname="edupi.localhost:8000",
        homepage=10,
        randompage=100,
        files_created=2,
        files_deleted=1,
    ),
    other_activity=[
        Setup.OtherPackageAndActivity(
            hostname="wikifundi.localhost:8000", homepage=5, randompage=100
        ),
        Setup.OtherPackageAndActivity(
            hostname="nomad.localhost:8000", homepage=5, randompage=100
        ),
        Setup.OtherPackageAndActivity(
            hostname="mathews.localhost:8000", homepage=5, randompage=100
        ),
    ],
    zim_normalized_activity=Setup.NormalizedZimActivity(
        homepage=10,
        randompage=100,
        randomasset=1000,
    ),
    zims_with_scaling=[
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="devops.stackexchange.com_en_all_2023-05",
            scale_factor=1,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="sqa.stackexchange.com_en_all_2023-05",
            scale_factor=1,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="wikipedia_fr_all_maxi_2023-09",
            scale_factor=40,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="wikipedia_en_all_maxi_2023-09",
            scale_factor=40,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="ifixit_fr_all_2023-08",
            scale_factor=40,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="khanacademy_fr_all_2023-03",
            scale_factor=10,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="movies.stackexchange.com_en_all_2023-11",
            scale_factor=10,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="wikipedia_fr_medicine_maxi_2023-11",
            scale_factor=10,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="ted_en_playlist-the-future-of-medicine_2021-12",
            scale_factor=10,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="3dprinting.stackexchange.com_en_all_2023-07",
            scale_factor=5,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="africanstorybook.org_mul_all_2023-10",
            scale_factor=5,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="ted_en_playlist-harnessing-the-future-of-data_2021-12",
            scale_factor=5,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="gutenberg_mul_all_2023-08",
            scale_factor=5,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="mathoverflow.net_en_all_2023-01",
            scale_factor=2,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="chess.stackexchange.com_en_all_2023-11",
            scale_factor=2,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="wikipedia_en_medicine_maxi_2023-11",
            scale_factor=2,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="ted_en_playlist-the-quest-to-end-poverty_2021-01",
            scale_factor=1,
        ),
        Setup.ZimAndScale(
            hostname="kiwix.localhost:8000",
            zim="ed_en_entertainment_2023-09",
            scale_factor=1,
        ),
    ],
)


def get_log_file(logs_folder: Path, max_log_size: int) -> Path:
    """Utility function to retrieve current log file and move older one

    This simulates the log rotation like Caddy would do.
    """
    log_file_name = "caddy_access_logs.json"
    log_file = logs_folder.joinpath(log_file_name)
    if log_file.exists() and log_file.stat().st_size > max_log_size:
        log_file.rename(
            logs_folder.joinpath(
                "caddy_access_logs-"
                f"{datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')[:-3]}"  # noqa DTZ005
                ".json"
            )
        )
        log_file = logs_folder.joinpath(log_file_name)
    return log_file


def get_next_log_line(all_logs: Path) -> Generator[str, None, None]:
    """Return the next log line from temporary file to inject as simulated Caddy log

    This is the part of the code which is responsible to randomize the logs order.
    It is a generator, hence returning only one line at a time (after the initial
    loading and shuffling of lines).
    """

    all_lines_start_pos: list[int] = []  # we keep only the start line position in mem
    with open(all_logs) as fh:
        next_line = 0
        while fh.readline():
            all_lines_start_pos.append(next_line)
            next_line = fh.tell()
        random.shuffle(all_lines_start_pos)
        while True:
            for line in all_lines_start_pos:
                fh.seek(line)
                yield fh.readline()


def generate_edupi_tmp_lines(
    setup: Setup.EdupiActivity,
) -> Generator[Any, None, None]:
    """Generate all logs lines for Edupi activity"""
    for _ in range(setup.files_created):
        yield {
            "status": "201",
            "request": {
                "host": setup.hostname,
                "method": "POST",
                "uri": "/api/documents/",
            },
        }
    for i in range(setup.files_deleted):
        yield {
            "status": "204",
            "request": {
                "host": setup.hostname,
                "method": "DELETE",
                "uri": f"/api/documents/{i}",
            },
        }
    yield from generate_other_packages_tmp_lines(
        setup=Setup.OtherPackageAndActivity(
            hostname=setup.hostname,
            homepage=setup.homepage,
            randompage=setup.randompage,
        )
    )


def generate_other_packages_tmp_lines(
    setup: Setup.OtherPackageAndActivity,
) -> Generator[Any, None, None]:
    """Generate all logs lines for other packages activity"""
    for i in range(setup.randompage):
        yield {
            "status": "200",
            "request": {
                "host": setup.hostname,
                "method": "GET",
                "uri": f"/page{i}.html",
            },
        }
    for _ in range(setup.homepage):
        yield {
            "status": "200",
            "request": {
                "host": setup.hostname,
                "method": "GET",
                "uri": "/",
            },
        }


def generate_zims_tmp_lines(
    normalized_activity: Setup.NormalizedZimActivity,
    zim_with_scale: Setup.ZimAndScale,
) -> Generator[Any, None, None]:
    """Generate all logs lines for Zim activity"""
    for i in range(normalized_activity.randompage * zim_with_scale.scale_factor):
        yield {
            "status": "200",
            "request": {
                "host": zim_with_scale.hostname,
                "method": "GET",
                "uri": f"/content/{zim_with_scale.zim}/page{i}.html",
            },
        }
    for i in range(normalized_activity.randomasset * zim_with_scale.scale_factor):
        yield {
            "status": "200",
            "request": {
                "host": zim_with_scale.hostname,
                "method": "GET",
                "uri": f"/content/{zim_with_scale.zim}/page{i}.html",
            },
            "resp_headers": {"Content-Type": ["application/javascript; charset=utf-8"]},
        }
    for _ in range(normalized_activity.homepage * zim_with_scale.scale_factor):
        yield {
            "status": "200",
            "request": {
                "host": zim_with_scale.hostname,
                "method": "GET",
                "uri": f"/content/{zim_with_scale.zim}/",
            },
        }


def generate_all_logs_in_tmp(all_logs: Path, setup: Setup) -> int:
    """Generate all logs lines in a temporary file"""
    logger.info(f"Generating logs in temporary file at {all_logs}")
    nb_logs = 0
    generators = [
        generate_edupi_tmp_lines(setup=setup.edupi_activity),
        *[
            generate_other_packages_tmp_lines(setup=setup)
            for setup in setup.other_activity
        ],
        *[
            generate_zims_tmp_lines(
                normalized_activity=setup.zim_normalized_activity, zim_with_scale=zim
            )
            for zim in setup.zims_with_scaling
        ],
    ]
    with open(all_logs, "w") as fh:
        for data in chain.from_iterable(generators):
            json.dump(data, fh)
            fh.write("\n")
            nb_logs += 1

    return nb_logs


def count_log_lines(all_logs: Path) -> int:
    """Count logs lines already present in temporary file"""
    logger.info(f"Counting log lines in temporary file at {all_logs}")
    with open(all_logs) as fh:
        return sum(1 for _ in fh.readlines())


def inject_one_line(line: str, fh: TextIOWrapper):
    """Insert one log line in simulated Caddy file

    Generic Caddy data is injected only at this stage to facilitate maintenance
    """
    data = json.loads(line)
    # set real timestamp
    data["ts"] = datetime.datetime.now().timestamp()  # noqa DTZ005
    # set constant fields
    data["level"] = "info"
    data["msg"] = "handled request"
    # inject lots of "noise" to represent "real" JSON parsing load
    data["logger"] = "http.log.access.log0"
    data["request"]["remote_ip"] = "167.94.145.58"
    data["request"]["remote_port"] = "33716"
    data["request"]["proto"] = "HTTP/1.1"
    data["request"]["headers"] = {
        "User-Agent": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11"
            " (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
        ],
        "Accept-Encoding": ["gzip"],
    }
    data["user_id"] = ""
    data["duration"] = "0.000123"
    data["size"] = "123"
    # some data is injected only if not already set by the data generator
    if "resp_headers" not in data:
        data["resp_headers"] = {}
    if "Server" not in data["resp_headers"]:
        data["resp_headers"]["Server"] = ["Caddy"]
    if "Etag" not in data["resp_headers"]:
        data["resp_headers"]["Etag"] = ['"rzvxcle2"']
    if "Content-Type" not in data["resp_headers"]:
        data["resp_headers"]["Content-Type"] = ["text/html; charset=utf-8"]
    if "Last-Modified" not in data["resp_headers"]:
        data["resp_headers"]["Last-Modified"] = ["Thu, 24 Aug 2023 07:41:09 GMT"]
    if "Accept-Ranges" not in data["resp_headers"]:
        data["resp_headers"]["Accept-Ranges"] = ["bytes"]
    if "Content-Length" not in data["resp_headers"]:
        data["resp_headers"]["Content-Length"] = ["506"]
    json.dump(data, fh)
    fh.write("\n")


def main():
    """Generate logs if needed, then inject them at the requested pace"""

    # seed with a constant value to have reproducible log data (123456 is just random)
    random.seed(a=123456)

    log_folder = Path(SETUP.target_folder)
    log_folder.mkdir(parents=True, exist_ok=True)
    Path(SETUP.tmp_folder).mkdir(parents=True, exist_ok=True)
    all_logs = Path(SETUP.tmp_folder).joinpath("all_logs.json")
    if os.getenv("FORCE", "n").lower() == "y" or not all_logs.exists():
        nb_logs = generate_all_logs_in_tmp(all_logs, SETUP)
    else:
        nb_logs = count_log_lines(all_logs)
    interval = int(24 * 3600 / nb_logs * 1000) / 1000 / ACCELERATION
    logger.info(
        f"{nb_logs} log lines have been generated and will be repeated {ACCELERATION}"
        f" times on 24 hours, i.e one every {interval} seconds"
    )

    count = 0
    while True:
        for line in get_next_log_line(all_logs):
            log_file = get_log_file(log_folder, SETUP.max_log_size)
            with open(log_file, "a") as fh:
                inject_one_line(line, fh)
            count += 1
            if count == ACCELERATION:
                print(".", end="", flush=True)  # noqa T201
                count = 0
            time.sleep(interval)


if __name__ == "__main__":
    main()
