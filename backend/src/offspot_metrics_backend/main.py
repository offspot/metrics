import functools
import logging
import sys
from asyncio import Task, create_task, sleep
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from offspot_metrics_backend import __about__
from offspot_metrics_backend.business.caddy_log_converter import CaddyLogConverter
from offspot_metrics_backend.business.inputs.clock_tick import ClockTick
from offspot_metrics_backend.business.log_watcher import LogWatcher, NewLineEvent
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.constants import BackendConf, logger
from offspot_metrics_backend.db.initializer import Initializer
from offspot_metrics_backend.routes import aggregations, kpis

PREFIX = "/v1"
TICK_PERIOD = (
    60  # tick period in seconds, changing this need a detailed impact analysis
)

# - fix this, this is not the same log format as uvicorn logs but are mixed in the same
#  STDOUT...
# - read debug level from environment variable
# - output JSON in production
# - disable some logs? (Inotify)
logging.basicConfig(
    level=logging.DEBUG, format="[%(asctime)s: %(levelname)s] %(message)s"
)


class Main:
    def __init__(self) -> None:
        self.log_watcher = None
        if BackendConf.processing_enabled:
            self.log_watcher = LogWatcher(
                watched_folder=BackendConf.reverse_proxy_logs_location,
                handler=self.handle_log_event,
                data_folder=BackendConf.logwatcher_data_folder,
            )
        self.background_tasks = set[Task[Any]]()

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        # Startup
        logger.debug(f"Database URL: {BackendConf.database_url}")
        Initializer.upgrade_db_schema()
        if BackendConf.processing_enabled:
            logger.info("Starting processing")
            self.processor = Processor()
            self.config = ReverseProxyConfig()
            self.config.parse_configuration()
            self.converter = CaddyLogConverter(self.config)
            self.processor.startup(current_period=Period.now().period)

            log_watcher_task = create_task(self.start_watcher())
            self.background_tasks.add(log_watcher_task)
            log_watcher_task.add_done_callback(
                functools.partial(self.task_stopped, "Log Watcher")
            )

            input_ticker_task = create_task(self.input_ticker())
            self.background_tasks.add(input_ticker_task)
            input_ticker_task.add_done_callback(
                functools.partial(self.task_stopped, "Input ticker")
            )

            processing_ticker_task = create_task(self.processing_ticker())
            self.background_tasks.add(processing_ticker_task)
            processing_ticker_task.add_done_callback(
                functools.partial(self.task_stopped, "Processing ticker")
            )
        else:
            logger.warning("Processing is disabled")
        # Startup complete
        yield
        # Shutdown
        if self.log_watcher:
            self.log_watcher.stop()

    def task_stopped(self, task_name: str, task: Task[Any]) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        self.background_tasks.discard(task)
        if exc:
            logger.error(f"{task_name} has stopped anormally", exc_info=exc)
            sys.exit(1)

    async def start_watcher(self):
        """Start the log watcher as a coroutine"""
        if not self.log_watcher:
            raise ValueError("Log watcher has not been initialized")
        await self.log_watcher.run_async()

    async def input_ticker(self):
        """Generate a ClockTick input every minute

        We need this input to be as precisely as possible generated every
        minute, i.e. 60 times per hour. Currently we assume that the logic
        processing input is fast enough to take less than one minute (if it
        does take longer, we have many other issues anyway so no need to
        overwhelm the system with 60 inputs per hour).
        """
        while True:
            await sleep(TICK_PERIOD - Period.now().datetime.second)
            logger.debug("Generating a ClockTick input")
            try:
                self.processor.process_input(ClockTick(ts=Period.now().datetime))
            except Exception as exc:
                logger.debug("Exception occured in clock tick", exc_info=exc)

    async def processing_ticker(self):
        """Start processing cycles with one minute pauses between them

        We do not need something precise here because we want to let
        the system "breath" between processing cycle and the processing logic
        does not mind if there is not 60 cycles per hour, it just need to
        regularly persist data in DB + perform needed computation every hour.
        """
        while True:
            await sleep(TICK_PERIOD)
            logger.debug("Background processing started")
            try:
                self.processor.process_tick(tick_period=Period.now().period)
            except Exception as exc:
                logger.debug("Exception occured in clock tick", exc_info=exc)
            logger.debug("Background processing completed")

    def handle_log_event(self, event: NewLineEvent):
        logger.debug(f"Log watcher sent: {event.line_content}")
        try:
            result = self.converter.process(event.line_content)
            for input_ in result.inputs:
                logger.debug(f"Processing input: {input_}")
                try:
                    self.processor.process_input(input_=input_)
                except Exception as exc:
                    logger.debug("Error processing input", exc_info=exc)
        except Exception as exc:
            logger.debug("Error log event", exc_info=exc)

    def create_app(self) -> FastAPI:
        self.app = FastAPI(
            title=__about__.__api_title__,
            description=__about__.__api_description__,
            version=__about__.__version__,
            lifespan=self.lifespan,
        )

        @self.app.get("/")
        async def landing() -> RedirectResponse:  # pyright: ignore
            """Redirect to root of latest version of the API"""
            return RedirectResponse(f"/{__about__.__api_version__}/", status_code=308)

        api = FastAPI(
            title=__about__.__api_title__,
            description=__about__.__api_description__,
            version=__about__.__version__,
            docs_url="/",
            openapi_tags=[
                {
                    "name": "all",
                    "description": "all APIs",
                },
            ],
            contact={
                "name": "Kiwix/openZIM Team",
                "url": "https://www.kiwix.org/en/contact/",
                "email": "contact+offspot_metrics@kiwix.org",
            },
            license_info={
                "name": "GNU General Public License v3.0",
                "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
            },
        )

        api.add_middleware(
            CORSMiddleware,
            allow_origins=BackendConf.allowed_origins,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        api.include_router(router=aggregations.router)
        api.include_router(router=kpis.router)

        self.app.mount(f"/{__about__.__api_version__}", api)

        return self.app
