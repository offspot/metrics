import logging
import os
from asyncio import sleep
from pathlib import Path
from subprocess import PIPE, Popen

import psutil

from offspot_metrics_backend.business.log_converter import LogConverter
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.constants import BackendConf

logger = logging.getLogger(__name__)


class FileBeatRunner:
    """Manages filebeat execution"""

    def __init__(self, converter: LogConverter) -> None:
        self.converter = converter

    async def run(self, processor: Processor):
        """Keep a filebeat process up and running at all times"""

        # restart filebeat forever
        while True:
            # kill all already running filebeat processes
            for proc in psutil.process_iter():
                if proc.name() == "filebeat":
                    logger.info(f"Killing filebeat process {proc.pid}")
                    proc.kill()

            # start filebeat and capture stdout
            logger.info("Starting filebeat in background")
            filebeat = Popen(
                BackendConf.filebeat_process_location,
                cwd=Path(BackendConf.filebeat_process_location).parent,
                stdout=PIPE,
            )

            # mainly for type hinter, not supposed to happen
            if filebeat.stdout is None:
                logger.error("Failed to capture stdout, will retry in 10 secs")
                await sleep(10)
                continue

            # set stdout as non blocking
            os.set_blocking(filebeat.stdout.fileno(), False)

            while True:
                for line in iter(filebeat.stdout.readline, b""):
                    logger.debug(f"Filebeat sent: {line}")
                    inputs = self.converter.process(line.decode().strip())
                    for input_ in inputs:
                        logger.debug(f"Processing input: {input_}")
                        processor.process_input(input_=input_)

                if filebeat.poll() is not None:
                    logger.error("Filebeat has exited, will restart in 10 secs")
                    # process has exited, let's restart the process after 10 secs
                    # to let the system recover
                    await sleep(10)
                    break

                await sleep(0.1)
