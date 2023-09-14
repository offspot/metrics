import logging
from asyncio import Task, create_task, sleep
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from offspot_metrics_backend import __about__
from offspot_metrics_backend.business.caddy_log_converter import CaddyLogConverter
from offspot_metrics_backend.business.log_watcher import LogWatcher, NewLineEvent
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.constants import BackendConf
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


logger = logging.getLogger(__name__)


class Main:
    def __init__(self) -> None:
        self.log_watcher = None
        if BackendConf.processing_enabled:
            self.log_watcher = LogWatcher(
                watched_folder=BackendConf.reverse_proxy_logs_location,
                handler=self.handle_log_event,
                data_folder=BackendConf.logwatcher_data_folder,
            )
        self.processor = Processor()
        self.config = ReverseProxyConfig()
        self.converter = CaddyLogConverter(self.config)
        self.background_tasks = set[Task[Any]]()

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        # Startup
        logger.debug(f"Database URL: {BackendConf.database_url}")
        Initializer.upgrade_db_schema()
        if BackendConf.processing_enabled:
            logger.info("Starting processing")
            self.config.parse_configuration()
            self.processor.startup(current_period=Period.now())
            log_watcher_task = create_task(self.start_watcher())
            self.background_tasks.add(log_watcher_task)
            log_watcher_task.add_done_callback(self.background_tasks.discard)

            ticker_task = create_task(self.ticker())
            self.background_tasks.add(ticker_task)
            ticker_task.add_done_callback(self.background_tasks.discard)
        else:
            logger.warning("Processing is disabled")
        # Startup complete
        yield
        # Shutdown
        if self.log_watcher:
            self.log_watcher.stop()

    async def start_watcher(self):
        """Start the log watcher as a coroutine"""
        if not self.log_watcher:
            raise ValueError("Log watcher has not been initialized")
        await self.log_watcher.run_async()

    async def ticker(self):
        """Start a processor tick every minute"""
        while True:
            await sleep(TICK_PERIOD)
            logger.debug("Processing a clock tick")
            self.processor.process_tick(tick_period=Period.now())

    def handle_log_event(self, event: NewLineEvent):
        logger.debug(f"Log watcher sent: {event.line_content}")
        inputs = self.converter.process(event.line_content)
        for input_ in inputs:
            logger.debug(f"Processing input: {input_}")
            self.processor.process_input(input_=input_)

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
